#!/bin/bash

# PixelPerfect Type - 一键启动脚本

clear

echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║        🎨 PixelPerfect Type 字体验收工具 🎨          ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "   请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"
echo ""

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在设置环境..."
    echo ""

    echo "   [1/3] 创建虚拟环境..."
    python3 -m venv venv

    echo "   [2/3] 激活虚拟环境..."
    source venv/bin/activate

    echo "   [3/3] 安装依赖包（这可能需要几分钟）..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt

    echo ""
    echo "✅ 环境设置完成！"
    echo ""
else
    source venv/bin/activate
fi

# 检查是否是首次运行（PaddleOCR模型下载提示）
if [ ! -d "$HOME/.paddleocr" ]; then
    echo "⚠️  首次运行提示："
    echo "   PaddleOCR 将自动下载模型文件（约100MB）"
    echo "   请确保网络连接正常，下载可能需要5-10分钟"
    echo ""
    read -p "   按回车键继续..." -r
    echo ""
fi

# 启动服务
echo "🚀 正在启动服务..."
echo ""
echo "────────────────────────────────────────────────────────"
echo ""

python app.py

# 如果服务被停止
echo ""
echo "────────────────────────────────────────────────────────"
echo ""
echo "👋 服务已停止"
echo ""
