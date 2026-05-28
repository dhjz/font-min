import argparse
import uvicorn
from backend.routes import app

def main():
    parser = argparse.ArgumentParser(description='DFont - 字体转换与压缩工具')
    parser.add_argument('-p', '--port', type=int, default=40050, help='指定端口号 (默认: 40050)')
    args = parser.parse_args()
    
    print("=" * 50)
    print("  DFont -  字体转换与压缩工具")
    print(f"  访问地址: http://127.0.0.1:{args.port}")
    print(f"  API文档: http://127.0.0.1:{args.port}/docs")
    print("=" * 50)
    uvicorn.run(app, host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    main()
