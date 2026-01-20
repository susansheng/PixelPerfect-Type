#!/usr/bin/env python3
"""
调试OCR坐标系统
"""
from paddleocr import PaddleOCR
from PIL import Image
import sys

if len(sys.argv) < 2:
    print("用法: python3 debug_ocr_coords.py <图片路径>")
    sys.exit(1)

image_path = sys.argv[1]

# 读取图片实际尺寸
img = Image.open(image_path)
print(f"输入图片尺寸: {img.size} (宽x高)")

# 初始化OCR
print("\n初始化PaddleOCR...")
ocr = PaddleOCR(
    use_textline_orientation=True,
    lang='ch',
    det_db_thresh=0.5,
    det_db_box_thresh=0.6,
    rec_batch_num=6
)

# 执行OCR
print("执行OCR识别...")
result = ocr.ocr(image_path)

if not result or not result[0]:
    print("没有识别到文本")
    sys.exit(0)

ocr_result = result[0]

print(f"\nOCR结果类型: {type(ocr_result)}")

# 检查是否有doc_preprocessor结果
if hasattr(ocr_result, 'keys'):
    keys = list(ocr_result.keys())
    print(f"可用的keys: {keys}")

    # 检查预处理结果
    if 'doc_preprocessor_res' in keys:
        doc_res = ocr_result['doc_preprocessor_res']
        print(f"\ndoc_preprocessor_res类型: {type(doc_res)}")
        if hasattr(doc_res, 'keys'):
            print(f"doc_preprocessor_res keys: {list(doc_res.keys())}")
            # 查找图像尺寸相关的信息
            for key in doc_res.keys():
                value = doc_res[key]
                print(f"  {key}: {type(value)}")
                if hasattr(value, 'shape'):
                    print(f"    shape: {value.shape}")
                elif hasattr(value, 'size'):
                    print(f"    size: {value.size}")

    # 获取检测框
    if 'dt_polys' in keys:
        dt_polys = ocr_result['dt_polys']
        print(f"\n检测框数量: {len(dt_polys)}")
        if len(dt_polys) > 0:
            # 分析坐标范围
            all_x = []
            all_y = []
            for poly in dt_polys:
                for point in poly:
                    all_x.append(point[0])
                    all_y.append(point[1])

            print(f"坐标范围:")
            print(f"  X: {min(all_x):.1f} ~ {max(all_x):.1f}")
            print(f"  Y: {min(all_y):.1f} ~ {max(all_y):.1f}")
            print(f"\n第一个检测框坐标: {dt_polys[0]}")
            if 'rec_texts' in keys:
                print(f"第一个文本内容: {ocr_result['rec_texts'][0]}")

print("\n分析完成！")
