#!/usr/bin/env python3
"""
调试脚本：检查 PaddleOCR 的实际输出结构
"""
from paddleocr import PaddleOCR
import json

print("=" * 60)
print("🔍 调试 PaddleOCR 输出结构")
print("=" * 60)
print()

# 初始化 PaddleOCR
print("正在初始化 PaddleOCR...")
ocr = PaddleOCR(
    use_textline_orientation=True,
    lang='ch'
)
print("✅ PaddleOCR 初始化完成")
print()

# 测试图片路径
test_image = "/Users/sxsheng/Documents/代码/字号自动测量器2/backend/uploads/b259b615-adff-4929-b3c4-4081909c4d9d_original.jpg"

print(f"📷 测试图片: {test_image}")
print()

# 执行 OCR
print("🚀 执行 OCR 识别...")
result = ocr.ocr(test_image)
print("✅ OCR 完成")
print()

# 输出结果结构
print("=" * 60)
print("📊 OCR 结果结构分析:")
print("=" * 60)
print()

print(f"result 类型: {type(result)}")
print(f"result 长度: {len(result) if result else 'None'}")
print()

if result:
    print(f"result[0] 类型: {type(result[0])}")
    if result[0]:
        print(f"result[0] 长度: {len(result[0])}")
        print()

        # 查看前3个结果的结构
        for i, line in enumerate(result[0][:3]):
            print(f"--- 结果 #{i+1} ---")
            print(f"line 类型: {type(line)}")
            print(f"line 长度: {len(line)}")
            print()

            if len(line) >= 1:
                print(f"  line[0] (坐标) 类型: {type(line[0])}")
                print(f"  line[0] 内容: {line[0]}")

            if len(line) >= 2:
                print(f"  line[1] 类型: {type(line[1])}")
                print(f"  line[1] 内容: {line[1]}")

                # 尝试访问 line[1] 的元素
                if isinstance(line[1], (list, tuple)):
                    print(f"  line[1] 是列表/元组，长度: {len(line[1])}")
                    if len(line[1]) > 0:
                        print(f"    line[1][0]: {line[1][0]}")
                    if len(line[1]) > 1:
                        print(f"    line[1][1]: {line[1][1]}")
                elif isinstance(line[1], str):
                    print(f"  ⚠️  line[1] 是字符串: '{line[1]}'")
                    print(f"  字符串长度: {len(line[1])}")

            print()

    # 保存完整结果到文件
    print("💾 保存完整结果到 ocr_debug_output.json")
    with open('ocr_debug_output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("=" * 60)
print("✅ 调试完成")
print("=" * 60)
