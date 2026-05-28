# DFont - 字体转换与压缩工具

一个基于 Python 的字体转换和压缩工具，支持多种字体格式之间的相互转换，以及字体子集提取压缩。

## 功能特性

- **字体格式转换**: 支持 TTF、OTF、WOFF、WOFF2、EOT、SVG 格式之间的相互转换
- **字体压缩**: 提取字体子集，仅保留需要的字符，大幅减小字体文件体积
- **Web 界面**: 提供简洁美观的 Web 操作界面
- **API 服务**: 基于 FastAPI 的 RESTful API，支持程序化调用
- **自动清理**: 定时清理上传和输出的临时文件

## 技术栈

- Python 3.10+
- FastAPI (Web 框架)
- FontTools (字体处理)
- Brotli (WOFF2 压缩)
- uv (依赖管理)

## 快速开始

### 环境要求

- Python 3.10 或更高版本
- uv 包管理器

### 安装依赖

```bash
# 安装 uv (如果尚未安装)
pip install uv

# 同步项目依赖
uv sync
```

### 运行项目

```bash
# 默认端口 40050
uv run python main.py

# 指定端口
uv run python main.py -p 8080
```

启动后访问:
- Web 界面: http://127.0.0.1:40050
- API 文档: http://127.0.0.1:40050/docs

## 使用说明

### 字体转换

1. 点击上传按钮或拖拽字体文件到上传区域
2. 选择目标格式 (TTF/OTF/WOFF/WOFF2/EOT/SVG)
3. 点击"转换"按钮
4. 下载转换后的字体文件

### 字体压缩

1. 点击上传按钮或拖拽字体文件到上传区域
2. 输入需要保留的文字字符
3. 选择目标格式
4. 点击"压缩"按钮
5. 下载压缩后的字体文件

## 打包部署

### Windows 打包

运行打包脚本:

```bash
cd bin
build_windows.bat
```

打包完成后，可执行文件位于 `dist/dfont.exe`

### Linux 打包

运行打包脚本:

```bash
cd bin
chmod +x build_linux.sh
./build_linux.sh
```

打包完成后，可执行文件位于:
- `dist/dfont-linux-amd64` (x86_64 架构)
- `dist/dfont-linux-arm64` (ARM64 架构)

### 打包说明

打包使用 PyInstaller 将项目打包为独立可执行文件，包含:
- Python 运行时
- 所有依赖库
- Web 静态资源

打包后的可执行文件可直接运行，无需安装 Python 环境。

## 项目结构

```
dfont/
├── backend/           # 后端代码
│   ├── routes.py      # API 路由
│   ├── font_converter.py   # 字体转换模块
│   ├── font_compressor.py  # 字体压缩模块
│   └── file_manager.py     # 文件管理模块
├── web/               # 前端资源
│   ├── index.html     # 主页面
│   └── static/        # 静态资源
├── bin/               # 打包脚本
│   ├── build_windows.bat   # Windows 打包
│   └── build_linux.sh      # Linux 打包
├── main.py            # 入口文件
├── pyproject.toml     # 项目配置
└── requirements.txt   # 依赖列表
```

## API 接口

### 字体转换

```
POST /api/convert
```

参数:
- `file`: 字体文件
- `target_format`: 目标格式

### 字体压缩

```
POST /api/compress
```

参数:
- `file`: 字体文件
- `text`: 需要保留的字符
- `target_format`: 目标格式

完整 API 文档请访问 `/docs` 路径。

## 开发

### 安装开发依赖

```bash
uv sync --extra dev
```

### 依赖说明

核心依赖:
- `fonttools`: 字体文件处理
- `brotli`: WOFF2 格式压缩
- `fastapi`: Web 框架
- `uvicorn`: ASGI 服务器
- `python-multipart`: 文件上传支持
- `apscheduler`: 定时任务调度

开发依赖:
- `pyinstaller`: 可执行文件打包

## 许可证

MIT License
