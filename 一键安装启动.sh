#!/bin/bash

echo "════════════════════════════════════════════════════════"
echo "  🎨 PixelPerfect Type - 安装和启动"
echo "════════════════════════════════════════════════════════"
echo ""

# 进入后端目录
cd "$(dirname "$0")/backend"

echo "📦 第1步：检查并安装依赖..."
echo ""

# 安装依赖到用户目录（使用最新稳定版本）
python3 -m pip install --user Flask Flask-CORS \
    paddlepaddle paddleocr \
    Pillow opencv-python \
    numpy scipy shapely

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 依赖安装失败！"
    echo ""
    echo "请尝试手动安装："
    echo "python3 -m pip install --user Flask Flask-CORS paddlepaddle paddleocr Pillow opencv-python numpy scipy shapely"
    echo ""
    exit 1
fi

echo ""
echo "✅ 依赖安装完成！"
echo ""

# 检查首次运行提示
if [ ! -d "$HOME/.paddleocr" ]; then
    echo "⚠️  首次运行提示："
    echo "   PaddleOCR 将自动下载模型文件（约100MB）"
    echo "   请确保网络连接正常，下载可能需要5-10分钟"
    echo ""
fi

echo "🚀 第2步：启动服务..."
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

# 启动服务
python3 app.py

echo ""
echo "════════════════════════════════════════════════════════"
echo "👋 服务已停止"
echo ""
