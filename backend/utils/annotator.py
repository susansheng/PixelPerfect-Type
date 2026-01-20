"""
View 4: Result Annotation
在标准化图片上标注拟合出的字号信息
"""
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from typing import List, Dict


class ResultAnnotator:
    """结果标注器 - 在图片上标注字号信息"""

    def __init__(self):
        self.annotation_color = (0, 120, 255)  # 蓝色
        self.annotation_bg_color = (255, 255, 255)  # 白色背景
        self.font_size = 14

    def annotate_image(
        self,
        image_path: str,
        text_regions: List[Dict],
        output_path: str,
        show_confidence: bool = True
    ):
        """
        在图片上标注字号信息

        Args:
            image_path: 输入图片路径（750px宽度）
            text_regions: 包含拟合结果的文本区域列表
            output_path: 输出图片路径
            show_confidence: 是否显示拟合质量
        """
        # 使用OpenCV加载图片以便绘制
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法加载图片: {image_path}")

        for region in text_regions:
            if not region.get('fitted_font_size'):
                continue

            font_size = region['fitted_font_size']
            fit_quality = region.get('fit_quality', 0)
            bbox = region['bbox']
            text_content = region['text']

            # 标注文本
            if show_confidence:
                label = f"{font_size}px (Q:{fit_quality:.2f})"
            else:
                label = f"{font_size}px"

            # 计算标注位置（文字框上方）
            x = int(bbox['x'])
            y = int(bbox['y'])

            # 绘制标签背景
            label_size = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                1
            )[0]

            # 背景矩形
            padding = 4
            bg_x1 = x
            bg_y1 = y - label_size[1] - padding * 2 - 5
            bg_x2 = x + label_size[0] + padding * 2
            bg_y2 = y - 5

            # 确保不越界
            bg_y1 = max(0, bg_y1)

            # 绘制半透明背景
            overlay = img.copy()
            cv2.rectangle(
                overlay,
                (bg_x1, bg_y1),
                (bg_x2, bg_y2),
                self.annotation_bg_color,
                -1
            )
            img = cv2.addWeighted(overlay, 0.7, img, 0.3, 0)

            # 绘制文本
            cv2.putText(
                img,
                label,
                (x + padding, y - padding - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.annotation_color,
                1,
                cv2.LINE_AA
            )

            # 绘制指示线
            cv2.line(
                img,
                (x, bg_y2),
                (x, y),
                self.annotation_color,
                1,
                cv2.LINE_AA
            )

            # 绘制边界框（可选）
            box_x, box_y = int(bbox['x']), int(bbox['y'])
            box_w, box_h = int(bbox['width']), int(bbox['height'])
            cv2.rectangle(
                img,
                (box_x, box_y),
                (box_x + box_w, box_y + box_h),
                (0, 255, 0),
                1,
                cv2.LINE_AA
            )

        # 保存结果
        cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])

    def generate_report(self, text_regions: List[Dict]) -> Dict:
        """
        生成字号分析报告

        Args:
            text_regions: 包含拟合结果的文本区域列表

        Returns:
            Dict: 分析报告
        """
        font_sizes = [
            r['fitted_font_size']
            for r in text_regions
            if r.get('fitted_font_size')
        ]

        if not font_sizes:
            return {
                "total_texts": len(text_regions),
                "fitted_texts": 0,
                "font_sizes": {}
            }

        # 统计字号分布
        font_size_counts = {}
        for size in font_sizes:
            rounded_size = round(size)
            font_size_counts[rounded_size] = font_size_counts.get(rounded_size, 0) + 1

        # 排序
        sorted_sizes = sorted(
            font_size_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "total_texts": len(text_regions),
            "fitted_texts": len(font_sizes),
            "unique_font_sizes": len(font_size_counts),
            "font_size_distribution": dict(sorted_sizes),
            "most_common_size": sorted_sizes[0][0] if sorted_sizes else None,
            "average_font_size": round(sum(font_sizes) / len(font_sizes), 1),
            "min_font_size": round(min(font_sizes), 1),
            "max_font_size": round(max(font_sizes), 1)
        }
