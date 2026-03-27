# 提示词
- 项目实现一个基于python的字体转换和压缩工具
- 项目依赖uv 管理python依赖 `pyproject.toml`
- 前端资源在web目录, 启动时需要先启动前端服务, api请求到python服务
- python服务主要写在在backend目录
- 页面整体清爽美观, 基于 FontTools 开发
- tab切换2大主要功能: 字体转换和 字体压缩
- 字体转换: 页面点击按钮上传或者拖拽字体到body区域(显示上传文件大小), 选择目标格式,  点击转换按钮后, 字体转换服务会将字体转换为指定格式提供给前端下载, 显示输出文件大小以及转换耗时
- 字体压缩: 页面点击按钮上传或者拖拽字体到body区域, 然后可以输入任意文字, 选择目标字体格式, 点击压缩按钮后, 字体压缩服务会将字体提取子集, 并转换成指定格式提供给前端下载
- 还有什么其他我没考虑得到的可以帮我考虑优化下

# 命令
```sh
# 1. 创建目录并解压 (注意替换你的压缩包实际名称)
mkdir -p ~/.local/python && tar -xf 你的压缩包.tar.gz -C ~/.local/python --strip-components=1

# 2. 将 Python 路径写入环境变量文件 (让系统能找到它)
echo 'export PATH="$HOME/.local/python/bin:$PATH"' >> ~/.bashrc

# 3. 刷新环境变量，使其立即生效
source ~/.bashrc

git archive --format=zip --output=./latest.zip HEAD

sed -i 's/\r$//' bin/build_linux.sh

python3.10 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```
