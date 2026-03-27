import os
import time
import tempfile
from io import BytesIO
from fontTools.ttLib import TTFont
from fontTools.ttLib.woff2 import WOFF2Reader, WOFF2Writer


class FontConverter:
    SUPPORTED_FORMATS = ['ttf', 'otf', 'woff', 'woff2', 'eot', 'svg']
    FORMAT_MIME_TYPES = {
        'ttf': 'font/ttf',
        'otf': 'font/otf',
        'woff': 'font/woff',
        'woff2': 'font/woff2',
        'eot': 'application/vnd.ms-fontobject',
        'svg': 'image/svg+xml'
    }

    @staticmethod
    def detect_format(font_path: str) -> str:
        with open(font_path, 'rb') as f:
            header = f.read(4)
            if header[:2] == b'wO':
                if header[2:4] == b'f2':
                    return 'woff2'
                return 'woff'
            if header[:4] == b'OTTO':
                return 'otf'
            return 'ttf'

    @staticmethod
    def convert(font_path: str, target_format: str, output_path: str = None) -> dict:
        start_time = time.time()
        source_format = FontConverter.detect_format(font_path)
        target_format = target_format.lower()
        
        if target_format not in FontConverter.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的目标格式: {target_format}")
        
        if source_format == target_format:
            raise ValueError(f"源格式和目标格式相同: {source_format}")
        
        input_size = os.path.getsize(font_path)
        
        font = TTFont(font_path)
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(font_path))[0]
            output_dir = tempfile.gettempdir()
            output_path = os.path.join(output_dir, f"{base_name}.{target_format}")
        
        if target_format == 'woff':
            font.flavor = 'woff'
        elif target_format == 'woff2':
            font.flavor = 'woff2'
        else:
            font.flavor = None
        
        font.save(output_path)
        font.close()
        
        output_size = os.path.getsize(output_path)
        elapsed_time = time.time() - start_time
        
        return {
            'success': True,
            'input_path': font_path,
            'output_path': output_path,
            'source_format': source_format,
            'target_format': target_format,
            'input_size': input_size,
            'output_size': output_size,
            'elapsed_time': round(elapsed_time, 3)
        }

    @staticmethod
    def convert_bytes(font_bytes: bytes, original_filename: str, target_format: str) -> dict:
        start_time = time.time()
        target_format = target_format.lower()
        
        if target_format not in FontConverter.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的目标格式: {target_format}")
        
        input_size = len(font_bytes)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(original_filename)[1]) as tmp:
            tmp.write(font_bytes)
            tmp_path = tmp.name
        
        try:
            source_format = FontConverter.detect_format(tmp_path)
            
            if source_format == target_format:
                raise ValueError(f"源格式和目标格式相同: {source_format}")
            
            font = TTFont(tmp_path)
            
            output_buffer = BytesIO()
            
            if target_format == 'woff':
                font.flavor = 'woff'
            elif target_format == 'woff2':
                font.flavor = 'woff2'
            else:
                font.flavor = None
            
            font.save(output_buffer)
            font.close()
            
            output_bytes = output_buffer.getvalue()
            output_size = len(output_bytes)
            elapsed_time = time.time() - start_time
            
            base_name = os.path.splitext(original_filename)[0]
            output_filename = f"{base_name}.{target_format}"
            
            return {
                'success': True,
                'output_bytes': output_bytes,
                'output_filename': output_filename,
                'source_format': source_format,
                'target_format': target_format,
                'input_size': input_size,
                'output_size': output_size,
                'elapsed_time': round(elapsed_time, 3),
                'mime_type': FontConverter.FORMAT_MIME_TYPES.get(target_format, 'application/octet-stream')
            }
        finally:
            os.unlink(tmp_path)
