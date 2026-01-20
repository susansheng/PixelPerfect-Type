#!/usr/bin/env python3
"""
自动化测试脚本 - 测试完整的图片处理流程
"""
import requests
import sys
import os
from pathlib import Path

print("=" * 60)
print("  🧪 PixelPerfect Type - 自动化测试")
print("=" * 60)
print()

# 测试配置
API_URL = "http://localhost:9090/api/process"
TEST_IMAGE = "/Users/sxsheng/Documents/代码/字号自动测量器2/backend/uploads/7797ea66-e0d0-4b81-b894-8c2c194c0fb0_original.jpg"

print("📋 测试配置:")
print(f"   API地址: {API_URL}")
print(f"   测试图片: {TEST_IMAGE}")
print()

# 检查图片是否存在
if not os.path.exists(TEST_IMAGE):
    print("❌ 测试图片不存在！")
    print(f"   路径: {TEST_IMAGE}")
    sys.exit(1)

print("✅ 测试图片存在")
print()

# 上传图片进行处理
print("🚀 步骤1：上传图片...")
try:
    with open(TEST_IMAGE, 'rb') as f:
        files = {'image': ('test.jpg', f, 'image/jpeg')}
        response = requests.post(API_URL, files=files, timeout=120)

    print(f"   HTTP状态码: {response.status_code}")

    if response.status_code == 200:
        print("   ✅ 请求成功！")
    else:
        print(f"   ❌ 请求失败: {response.status_code}")
        print(f"   响应内容: {response.text[:500]}")
        sys.exit(1)

except requests.exceptions.Timeout:
    print("   ⚠️  请求超时（这可能是因为首次运行需要下载OCR模型）")
    print("   提示：请等待几分钟后重试")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ 请求错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("🔍 步骤2：解析响应...")

try:
    result = response.json()

    if result.get('success'):
        print("   ✅ 处理成功！")
        print()

        # 显示统计信息
        print("📊 处理结果:")
        print(f"   任务ID: {result.get('task_id')}")

        report = result.get('report', {})
        print()
        print("   统计数据:")
        print(f"   • 文本总数: {report.get('total_texts', 0)}")
        print(f"   • 成功拟合: {report.get('fitted_texts', 0)}")
        print(f"   • 不同字号: {report.get('unique_font_sizes', 0)}")
        print(f"   • 平均字号: {report.get('average_font_size', 'N/A')}")
        print(f"   • 最常用字号: {report.get('most_common_size', 'N/A')}")
        print(f"   • 字号范围: {report.get('min_font_size', 'N/A')} - {report.get('max_font_size', 'N/A')}")

        # 显示识别的文字示例
        text_regions = result.get('text_regions', [])
        if text_regions:
            print()
            print(f"   识别的文字示例（前5个）:")
            for i, region in enumerate(text_regions[:5]):
                text = region.get('text', '')
                font_size = region.get('fitted_font_size', 'N/A')
                quality = region.get('fit_quality', 'N/A')
                print(f"   {i+1}. \"{text}\" - {font_size}px (质量: {quality})")

        print()
        print("🖼️  生成的图片:")
        images = result.get('images', {})
        for name, url in images.items():
            print(f"   • {name}: http://localhost:9090{url}")

        print()
        print("=" * 60)
        print("✨ 测试完成！所有功能正常运行！")
        print("=" * 60)

    else:
        print("   ❌ 处理失败")
        print(f"   错误: {result.get('error', '未知错误')}")
        if 'error_type' in result:
            print(f"   错误类型: {result['error_type']}")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ 解析响应失败: {e}")
    print(f"   原始响应: {response.text[:500]}")
    sys.exit(1)
