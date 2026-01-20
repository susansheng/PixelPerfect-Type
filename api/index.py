"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# 导入 Flask app
from app import app

# 导出 app 供 Vercel 使用
# Vercel 的 @vercel/python runtime 会自动处理 WSGI
app = app
