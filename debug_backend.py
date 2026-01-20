#!/usr/bin/env python3
"""
调试脚本 - 直接测试后端处理流程
"""
import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("  🔍 PixelPerfect Type - 后端调试")
print("=" * 60)
print()

# 测试导入
print("📦 步骤1：测试导入模块...")
try:
    from utils.image_processor import ImageNormalizer
    print("  ✅ ImageNormalizer")
except Exception as e:
    print(f"  ❌ ImageNormalizer: {e}")

try:
    from utils.ocr_detector import OCRDetector
    print("  ✅ OCRDetector")
except Exception as e:
    print(f"  ❌ OCRDetector: {e}")

try:
    from utils.font_fitter import FontFitter
    print("  ✅ FontFitter")
except Exception as e:
    print(f"  ❌ FontFitter: {e}")

try:
    from utils.annotator import ResultAnnotator
    print("  ✅ ResultAnnotator")
except Exception as e:
    print(f"  ❌ ResultAnnotator: {e}")

print()
print("📦 步骤2：测试依赖包...")

# 测试关键依赖
dependencies = [
    'flask',
    'flask_cors',
    'PIL',
    'cv2',
    'numpy',
    'paddleocr'
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"  ✅ {dep}")
    except ImportError as e:
        print(f"  ❌ {dep}: {e}")

print()
print("=" * 60)
print()

# 如果所有导入都成功，测试OCR初始化
print("🚀 步骤3：测试 OCR 初始化...")
print("   (这可能需要几秒钟...)")
print()

try:
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False, show_log=False)
    print("  ✅ PaddleOCR 初始化成功！")
except Exception as e:
    print(f"  ❌ PaddleOCR 初始化失败:")
    print(f"     {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("✨ 调试完成！")
print()
