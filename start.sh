#!/bin/bash

# PixelPerfect Type - 快速启动脚本

echo "======================================"
echo "  PixelPerfect Type"
echo "  字体验收工具 - 快速启动"
echo "======================================"
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"
echo ""

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查依赖是否已安装
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate

    echo "📦 正在安装依赖（可能需要几分钟）..."
    pip install --upgrade pip
    pip install -r requirements.txt

    echo ""
    echo "✅ 依赖安装完成！"
    echo ""
else
    source venv/bin/activate
fi

# 启动Flask服务
echo "🚀 启动后端服务..."
echo "   API地址: http://localhost:5000"
echo ""
echo "💡 提示: 请在浏览器中打开 frontend/index.html"
echo ""
echo "按 Ctrl+C 停止服务"
echo "======================================"
echo ""

python app.py
