import uvicorn
from backend.routes import app

if __name__ == '__main__':
    print("=" * 50)
    print("  DFont - 字体转换与压缩工具")
    print("  访问地址: http://127.0.0.1:5000")
    print("  API文档: http://127.0.0.1:5000/docs")
    print("=" * 50)
    uvicorn.run(app, host='0.0.0.0', port=5000)
