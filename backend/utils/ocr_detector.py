"""
View 2: Intelligent OCR
使用 PaddleOCR 识别界面中所有文本内容及其位置
"""
from paddleocr import PaddleOCR
import numpy as np
from typing import List, Dict
import cv2


class OCRDetector:
    """OCR 文字识别器"""

    def __init__(self):
        """
        初始化 PaddleOCR，使用更严格的检测参数
        """
        self.ocr = PaddleOCR(
            use_textline_orientation=True,
            lang='ch',
            det_db_thresh=0.5,          # 提高文本检测阈值（默认0.3）
            det_db_box_thresh=0.6,      # 提高边框置信度阈值（默认0.5）
            rec_batch_num=6             # 减少批处理大小提高精度
        )

    def detect_texts(self, image_path: str) -> List[Dict]:
        """
        检测图片中的所有文本

        Args:
            image_path: 图片路径

        Returns:
            List[Dict]: 文本检测结果列表
        """
        # 执行OCR
        result = self.ocr.ocr(image_path)

        if not result or not result[0]:
            return []

        # 处理PaddleX 3.x 的OCRResult对象
        ocr_result = result[0]

        # 保存预处理后的图片（OCR实际使用的图片）
        if hasattr(ocr_result, 'keys') and 'doc_preprocessor_res' in ocr_result.keys():
            doc_res = ocr_result['doc_preprocessor_res']
            if hasattr(doc_res, 'keys') and 'output_img' in doc_res.keys():
                self.preprocessed_img = doc_res['output_img']  # 保存预处理后的图片
            else:
                self.preprocessed_img = None
        else:
            self.preprocessed_img = None

        # 解析OCR结果
        text_regions = []

        # 方法1：作为字典访问
        if hasattr(ocr_result, 'keys'):
            keys = list(ocr_result.keys())

            # 根据发现的keys来解析数据
            # 直接指定PaddleX 3.x的标准键名
            boxes_key = 'dt_polys' if 'dt_polys' in keys else ('rec_polys' if 'rec_polys' in keys else None)
            texts_key = 'rec_texts' if 'rec_texts' in keys else None
            scores_key = 'rec_scores' if 'rec_scores' in keys else None

            if boxes_key and texts_key:
                boxes_data = ocr_result[boxes_key]
                texts_data = ocr_result[texts_key]
                scores_data = ocr_result[scores_key] if scores_key else [1.0] * len(texts_data)

                for idx in range(len(texts_data)):
                    text = texts_data[idx]
                    box = boxes_data[idx]
                    confidence = scores_data[idx] if idx < len(scores_data) else 1.0

                    # 计算边界框
                    try:
                        if isinstance(box, (list, tuple)) and len(box) > 0:
                            # box可能是[[x1,y1],[x2,y2],[x3,y3],[x4,y4]]格式
                            x_coords = [point[0] if isinstance(point, (list, tuple)) else point for point in box]
                            y_coords = [point[1] if isinstance(point, (list, tuple)) else point for point in box]
                        elif hasattr(box, 'shape'):  # numpy array
                            # box是numpy数组，shape可能是(4,2)
                            x_coords = box[:, 0].tolist()
                            y_coords = box[:, 1].tolist()
                        else:
                            print(f"跳过文本{idx}: 未知的box格式 {type(box)}", flush=True)
                            continue

                        x = min(x_coords)
                        y = min(y_coords)
                        width = max(x_coords) - x
                        height = max(y_coords) - y

                        # ========== 过滤无效检测 ==========
                        # 1. 过滤置信度过低的结果
                        if confidence < 0.5:
                            continue

                        # 2. 过滤尺寸过小的文本框（可能是误识别）
                        if width < 10 or height < 8:
                            continue

                        # 3. 过滤无意义的文本
                        if not text or len(text.strip()) == 0:
                            continue

                        # 4. 过滤单个符号（可能是误识别的图案）
                        if len(text.strip()) == 1 and text in '□○△▽◇◆■●▲▼◎':
                            continue

                        # 计算中心点
                        center_x = x + width / 2
                        center_y = y + height / 2

                        # 转换box为标准格式
                        if hasattr(box, 'tolist'):
                            polygon = [[float(p[0]), float(p[1])] for p in box.tolist()]
                        else:
                            polygon = [[float(p[0]), float(p[1])] if isinstance(p, (list, tuple)) else [float(p), float(p)] for p in box]

                        text_region = {
                            "id": f"text_{idx}",
                            "text": text,
                            "confidence": float(confidence),
                            "bbox": {
                                "x": float(x),
                                "y": float(y),
                                "width": float(width),
                                "height": float(height)
                            },
                            "center": {
                                "x": float(center_x),
                                "y": float(center_y)
                            },
                            "polygon": polygon,
                            "fitted_font_size": None,
                            "fitted_baseline": None,
                            "fit_quality": None
                        }

                        text_regions.append(text_region)
                    except Exception as e:
                        print(f"解析文本{idx}时出错: {e}", flush=True)
                        continue

                print(f"成功解析{len(text_regions)}个文本区域（原始识别{len(texts_data)}个）", flush=True)

        return text_regions

    def visualize_detection(self, image_path: str, text_regions: List[Dict], output_path: str):
        """
        可视化OCR检测结果

        Args:
            image_path: 原始图片路径（如果有preprocessed_img则不使用）
            text_regions: 文本区域列表
            output_path: 输出图片路径
        """
        # 优先使用预处理后的图片（OCR实际处理的图片）
        if hasattr(self, 'preprocessed_img') and self.preprocessed_img is not None:
            img = self.preprocessed_img.copy()
            # preprocessed_img是RGB格式，需要转换为BGR供cv2使用
            if len(img.shape) == 3 and img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            print(f"使用预处理后的图片进行可视化，尺寸: {img.shape}")
        else:
            img = cv2.imread(image_path)
            print(f"使用原始图片进行可视化，尺寸: {img.shape}")

        for region in text_regions:
            # 绘制边界框
            box = region['polygon']
            pts = np.array(box, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)

            # 标注文本
            x, y = int(region['bbox']['x']), int(region['bbox']['y'])
            cv2.putText(
                img,
                region['text'][:10],  # 只显示前10个字符
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

        cv2.imwrite(output_path, img)
