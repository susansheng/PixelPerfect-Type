"""
View 3: Visual Regression & Fitting
核心字号拟合算法 - 通过像素重合度自动确定最佳字号
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from typing import Dict, Tuple, Optional
import os


class FontFitter:
    """字号拟合器 - 自动确定UI中文字的实际字号"""

    def __init__(self, font_path: Optional[str] = None):
        """
        初始化字号拟合器

        Args:
            font_path: PingFang SC 字体文件路径，如果为None则使用系统默认字体
        """
        self.font_path = font_path or self._get_default_font()
        self.line_height = 1.0  # 固定行高
        self.render_color = (255, 0, 0, 128)  # 红色半透明

    def _get_default_font(self) -> str:
        """获取默认的 PingFang SC 字体路径"""
        # macOS 系统字体路径
        macos_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]

        for font_path in macos_fonts:
            if os.path.exists(font_path):
                return font_path

        # 如果找不到，返回None，PIL会使用默认字体
        return None

    def fit_font_size(
        self,
        original_image_path: str,
        text: str,
        bbox: Dict,
        min_size: int = 8,
        max_size: int = 120,
        tolerance: float = 0.5
    ) -> Dict:
        """
        拟合字号的主函数

        算法原理：
        1. 使用二分搜索在合理的字号范围内搜索
        2. 对每个候选字号，在目标位置渲染文字
        3. 计算渲染文字与原图文字的重合度（IoU）
        4. 找到IoU最大的字号

        Args:
            original_image_path: 原始图片路径（750px宽度标准化后的）
            text: 要拟合的文字内容
            bbox: OCR检测到的文字边界框 {"x": ..., "y": ..., "width": ..., "height": ...}
            min_size: 最小字号（像素）
            max_size: 最大字号（像素）
            tolerance: 收敛容差（像素）

        Returns:
            Dict: 拟合结果，包含最佳字号、基线位置、拟合质量等
        """
        # 加载原图
        original_img = cv2.imread(original_image_path)
        if original_img is None:
            raise ValueError(f"无法加载图片: {original_image_path}")

        # 提取文字区域
        x, y, w, h = int(bbox['x']), int(bbox['y']), int(bbox['width']), int(bbox['height'])

        # 扩展区域以包含可能的基线变化（上下各扩展20%）
        expand_ratio = 0.2
        y_expand = int(h * expand_ratio)
        x_expand = int(w * expand_ratio)

        y_start = max(0, y - y_expand)
        y_end = min(original_img.shape[0], y + h + y_expand)
        x_start = max(0, x - x_expand)
        x_end = min(original_img.shape[1], x + w + x_expand)

        text_region = original_img[y_start:y_end, x_start:x_end]

        # 转换为灰度图并二值化
        text_gray = cv2.cvtColor(text_region, cv2.COLOR_BGR2GRAY)
        # 使用自适应阈值以应对不同背景
        text_binary = cv2.adaptiveThreshold(
            text_gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11, 2
        )

        # 二分搜索最佳字号
        best_font_size = None
        best_iou = 0.0
        best_baseline_offset = 0

        # 先粗略搜索，步长为4px
        for font_size in range(min_size, max_size, 4):
            result = self._evaluate_font_size(
                text, font_size, text_binary, (x_start, y_start), (x, y, w, h)
            )

            if result['iou'] > best_iou:
                best_iou = result['iou']
                best_font_size = font_size
                best_baseline_offset = result['baseline_offset']

        # 精细搜索（在最佳字号附近±4px范围内，步长为0.5px）
        if best_font_size:
            fine_min = max(min_size, best_font_size - 4)
            fine_max = min(max_size, best_font_size + 4)

            for font_size_decimal in np.arange(fine_min, fine_max, 0.5):
                result = self._evaluate_font_size(
                    text, font_size_decimal, text_binary,
                    (x_start, y_start), (x, y, w, h)
                )

                if result['iou'] > best_iou:
                    best_iou = result['iou']
                    best_font_size = font_size_decimal
                    best_baseline_offset = result['baseline_offset']

        return {
            "font_size": round(best_font_size, 1) if best_font_size else None,
            "baseline_offset": best_baseline_offset,
            "fit_quality": round(best_iou, 4),
            "font_family": "PingFang SC",
            "line_height": self.line_height,
            "bbox": bbox,
            "text": text
        }

    def _evaluate_font_size(
        self,
        text: str,
        font_size: float,
        target_binary: np.ndarray,
        region_offset: Tuple[int, int],
        original_bbox: Tuple[int, int, int, int]
    ) -> Dict:
        """
        评估特定字号的拟合质量

        Args:
            text: 文字内容
            font_size: 要评估的字号
            target_binary: 目标区域的二值化图像
            region_offset: 区域在原图中的偏移 (x_start, y_start)
            original_bbox: 原始边界框 (x, y, w, h)

        Returns:
            Dict: 包含IoU和基线偏移的评估结果
        """
        x, y, w, h = original_bbox
        x_start, y_start = region_offset

        # 创建渲染画布（与target_binary同样大小）
        canvas_height, canvas_width = target_binary.shape
        canvas = Image.new('L', (canvas_width, canvas_height), 0)
        draw = ImageDraw.Draw(canvas)

        # 加载字体
        try:
            if self.font_path and self.font_path.endswith('.ttc'):
                # TTC字体需要指定索引
                font = ImageFont.truetype(self.font_path, int(font_size), index=0)
            elif self.font_path:
                font = ImageFont.truetype(self.font_path, int(font_size))
            else:
                font = ImageFont.load_default()
        except Exception as e:
            # 降级到默认字体
            font = ImageFont.load_default()

        # 尝试不同的基线偏移（从-h/2 到 h/2）
        best_iou = 0.0
        best_offset = 0

        for baseline_offset in range(-h // 2, h // 2, 2):
            # 计算渲染位置（相对于canvas）
            render_x = x - x_start
            render_y = y - y_start + baseline_offset

            # 创建临时画布
            temp_canvas = canvas.copy()
            temp_draw = ImageDraw.Draw(temp_canvas)

            # 渲染文字
            temp_draw.text((render_x, render_y), text, fill=255, font=font)

            # 转换为numpy数组
            rendered = np.array(temp_canvas)

            # 计算IoU
            iou = self._calculate_iou(rendered, target_binary)

            if iou > best_iou:
                best_iou = iou
                best_offset = baseline_offset

        return {
            "iou": best_iou,
            "baseline_offset": best_offset
        }

    def _calculate_iou(self, rendered: np.ndarray, target: np.ndarray) -> float:
        """
        计算两个二值图像的IoU (Intersection over Union)

        Args:
            rendered: 渲染的文字二值图
            target: 目标文字二值图

        Returns:
            float: IoU值 (0-1)
        """
        # 确保尺寸一致
        if rendered.shape != target.shape:
            return 0.0

        # 计算交集和并集
        intersection = np.logical_and(rendered > 127, target > 127).sum()
        union = np.logical_or(rendered > 127, target > 127).sum()

        if union == 0:
            return 0.0

        iou = intersection / union
        return iou

    def render_overlay(
        self,
        original_image_path: str,
        text_regions: list,
        output_path: str
    ):
        """
        在原图上渲染红色半透明的拟合文字

        Args:
            original_image_path: 原始图片路径
            text_regions: 包含拟合结果的文本区域列表
            output_path: 输出图片路径
        """
        # 加载原图
        original = Image.open(original_image_path).convert('RGBA')

        # 创建透明图层用于绘制
        overlay = Image.new('RGBA', original.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for region in text_regions:
            if region.get('fitted_font_size'):
                font_size = int(region['fitted_font_size'])
                text = region['text']
                bbox = region['bbox']
                baseline_offset = region.get('fitted_baseline', 0)

                # 加载字体
                try:
                    if self.font_path and self.font_path.endswith('.ttc'):
                        font = ImageFont.truetype(self.font_path, font_size, index=0)
                    elif self.font_path:
                        font = ImageFont.truetype(self.font_path, font_size)
                    else:
                        font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()

                # 渲染位置
                x = int(bbox['x'])
                y = int(bbox['y']) + baseline_offset

                # 绘制半透明红色文字
                draw.text((x, y), text, fill=self.render_color, font=font)

        # 合并图层
        result = Image.alpha_composite(original, overlay)

        # 转换为RGB保存
        result.convert('RGB').save(output_path, quality=95)
