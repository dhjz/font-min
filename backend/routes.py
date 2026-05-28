import os
import sys
import uuid
import json
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from io import BytesIO
from .font_converter import FontConverter
from .font_compressor import FontCompressor
from .file_manager import FileManager

app = FastAPI(title="DFont API", description="字体转换与压缩工具API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    web_target = os.path.join(BASE_DIR, 'web')
    if not os.path.exists(web_target):
        web_source = os.path.join(sys._MEIPASS, 'web')
        if os.path.exists(web_source):
            shutil.copytree(web_source, web_target)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'ttf', 'otf', 'woff', 'woff2', 'eot', 'svg'}

file_manager = FileManager(BASE_DIR)
scheduler = BackgroundScheduler()


def cleanup_old_files():
    try:
        deleted_count = file_manager.cleanup_old_files(days=1)
        
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
        
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        try:
                            os.remove(filepath)
                        except Exception:
                            pass
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 清理完成: 删除了 {deleted_count} 条文件记录")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 清理失败: {str(e)}")


scheduler.add_job(
    cleanup_old_files,
    trigger=CronTrigger(hour=0, minute=0),
    id='cleanup_job',
    name='清理一天前的文件',
    replace_existing=True
)


@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 定时清理任务已启动，每天0点执行")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 定时清理任务已停止")


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def generate_output_filename(original_filename: str, target_format: str, is_compressed: bool = False) -> str:
    base_name = os.path.splitext(original_filename)[0]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    suffix = '_subset' if is_compressed else ''
    return f"{base_name}{suffix}_{timestamp}.{target_format}"

# 自定义uuid方法, 随机8位数
def generate_uuid() -> str:
    return str(uuid.uuid4())[:8]


@app.get("/")
async def index():
    web_path = os.path.join(BASE_DIR, 'web', 'index.html')
    return FileResponse(web_path)


@app.post("/webapi/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="没有上传文件")
    
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail=f'不支持的文件格式，支持: {", ".join(ALLOWED_EXTENSIONS)}')
    
    file_id = generate_uuid()
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{file_id}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    content = await file.read()
    with open(filepath, 'wb') as f:
        f.write(content)
    
    file_size = len(content)
    file_manager.save_file_info(file_id, file.filename, 'upload')
    
    return {
        'success': True,
        'file_id': file_id,
        'filename': file.filename,
        'path': filepath,
        'size': file_size,
        'size_formatted': format_size(file_size)
    }


@app.post("/webapi/convert")
async def convert_font(file_path: str = Form(...), target_format: str = Form('woff2'), original_filename: str = Form(...)):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail='文件不存在')
    
    target_format = target_format.lower()
    
    if target_format not in FontConverter.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f'不支持的目标格式: {target_format}')
    
    try:
        with open(file_path, 'rb') as f:
            font_bytes = f.read()
        
        result = FontConverter.convert_bytes(font_bytes, original_filename, target_format)
        
        output_id = generate_uuid()
        output_filename = generate_output_filename(original_filename, target_format, is_compressed=False)
        output_path = os.path.join(OUTPUT_FOLDER, f"{output_id}.{target_format}")
        
        with open(output_path, 'wb') as f:
            f.write(result['output_bytes'])
        
        file_manager.save_file_info(output_id, output_filename, 'output')
        
        history_data = {
            'type': 'convert',
            'output_id': output_id,
            'output_filename': output_filename,
            'source_format': result['source_format'],
            'target_format': result['target_format'],
            'input_size': result['input_size'],
            'output_size': result['output_size'],
            'elapsed_time': result['elapsed_time']
        }
        
        try:
            history_file = os.path.join(BASE_DIR, 'history.json')
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            history.insert(0, {**history_data, 'timestamp': datetime.now().isoformat()})
            history = history[:50]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        
        return {
            'success': True,
            'output_id': output_id,
            'output_filename': output_filename,
            'source_format': result['source_format'],
            'target_format': result['target_format'],
            'input_size': result['input_size'],
            'input_size_formatted': format_size(result['input_size']),
            'output_size': result['output_size'],
            'output_size_formatted': format_size(result['output_size']),
            'elapsed_time': result['elapsed_time']
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webapi/compress")
async def compress_font(file_path: str = Form(...), text: str = Form(''), target_format: str = Form('woff2'), original_filename: str = Form(...)):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail='文件不存在')
    
    if not text.strip():
        raise HTTPException(status_code=400, detail='请输入需要保留的文字')
    
    target_format = target_format.lower()
    
    if target_format not in FontCompressor.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f'不支持的目标格式: {target_format}')
    
    try:
        with open(file_path, 'rb') as f:
            font_bytes = f.read()
        
        result = FontCompressor.compress_bytes(font_bytes, original_filename, text, target_format)
        
        output_id = generate_uuid()
        output_filename = generate_output_filename(original_filename, target_format, is_compressed=True)
        output_path = os.path.join(OUTPUT_FOLDER, f"{output_id}.{target_format}")
        
        with open(output_path, 'wb') as f:
            f.write(result['output_bytes'])
        
        file_manager.save_file_info(output_id, output_filename, 'output')
        
        history_data = {
            'type': 'compress',
            'output_id': output_id,
            'output_filename': output_filename,
            'target_format': result['target_format'],
            'input_size': result['input_size'],
            'output_size': result['output_size'],
            'char_count': result['char_count'],
            'compression_ratio': result['compression_ratio'],
            'elapsed_time': result['elapsed_time']
        }
        
        try:
            history_file = os.path.join(BASE_DIR, 'history.json')
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            history.insert(0, {**history_data, 'timestamp': datetime.now().isoformat()})
            history = history[:50]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        
        return {
            'success': True,
            'output_id': output_id,
            'output_filename': output_filename,
            'target_format': result['target_format'],
            'input_size': result['input_size'],
            'input_size_formatted': format_size(result['input_size']),
            'output_size': result['output_size'],
            'output_size_formatted': format_size(result['output_size']),
            'char_count': result['char_count'],
            'compression_ratio': result['compression_ratio'],
            'elapsed_time': result['elapsed_time']
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webapi/download/{file_id}")
async def download_file(file_id: str):
    for ext in FontConverter.SUPPORTED_FORMATS:
        filepath = os.path.join(OUTPUT_FOLDER, f"{file_id}.{ext}")
        if os.path.exists(filepath):
            original_filename = file_manager.get_original_filename(file_id)
            if original_filename:
                return FileResponse(filepath, filename=original_filename)
            return FileResponse(filepath, filename=os.path.basename(filepath))
    
    raise HTTPException(status_code=404, detail='文件不存在')


@app.get("/webapi/preview/{file_id}")
async def preview_font(file_id: str):
    for ext in FontConverter.SUPPORTED_FORMATS:
        filepath = os.path.join(OUTPUT_FOLDER, f"{file_id}.{ext}")
        if os.path.exists(filepath):
            return FileResponse(filepath)
    
    filepath = os.path.join(UPLOAD_FOLDER, file_id)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    
    raise HTTPException(status_code=404, detail='文件不存在')


@app.get("/webapi/formats")
async def get_formats():
    return {
        'success': True,
        'formats': FontConverter.SUPPORTED_FORMATS,
        'format_names': {
            'ttf': 'TrueType Font',
            'otf': 'OpenType Font',
            'woff': 'Web Open Font Format',
            'woff2': 'Web Open Font Format 2.0'
        }
    }


@app.post("/webapi/history")
async def save_history(history_data: dict):
    try:
        history_file = os.path.join(BASE_DIR, 'history.json')
        history = []
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.insert(0, {
            **history_data,
            'timestamp': datetime.now().isoformat()
        })
        
        history = history[:50]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webapi/history")
async def get_history():
    try:
        history_file = os.path.join(BASE_DIR, 'history.json')
        
        if not os.path.exists(history_file):
            return {'success': True, 'history': []}
        
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
        history = [h for h in history if datetime.fromisoformat(h['timestamp']).timestamp() > cutoff_time]
        
        return {'success': True, 'history': history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, 'web', 'static')), name="static")
