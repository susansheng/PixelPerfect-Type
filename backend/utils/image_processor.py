"""
View 1: Image Normalization
将任意尺寸的UI截图等比缩放到750px宽度
"""
from PIL import Image
import numpy as np
from typing import Tuple


class ImageNormalizer:
    """图像标准化处理器"""

    TARGET_WIDTH = 750

    def __init__(self):
        self.scale_factor = 1.0
        self.original_size = (0, 0)
        self.normalized_size = (0, 0)

    def normalize(self, image_path: str, output_path: str) -> dict:
        """
        将图片标准化到750px宽度

        Args:
            image_path: 原始图片路径
            output_path: 输出图片路径

        Returns:
            dict: 包含缩放因子和尺寸信息的字典
        """
        # 打开图片
        img = Image.open(image_path)

        # 转换为RGB模式（移除透明通道）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        self.original_size = img.size

        # 计算缩放因子
        original_width, original_height = img.size
        self.scale_factor = self.TARGET_WIDTH / original_width

        # 计算新的高度
        new_height = int(original_height * self.scale_factor)
        self.normalized_size = (self.TARGET_WIDTH, new_height)

        # 使用高质量的重采样算法
        normalized_img = img.resize(
            self.normalized_size,
            Image.Resampling.LANCZOS
        )

        # 保存标准化后的图片
        normalized_img.save(output_path, quality=95)

        # 返回处理结果
        result = {
            "original_size": {
                "width": original_width,
                "height": original_height
            },
            "normalized_size": {
                "width": self.TARGET_WIDTH,
                "height": new_height
            },
            "scale_factor": self.scale_factor,
            "output_path": output_path
        }

        return result

    def get_normalized_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        """
        将原始坐标转换为标准化后的坐标

        Args:
            x: 原始x坐标
            y: 原始y坐标

        Returns:
            Tuple[float, float]: 标准化后的(x, y)坐标
        """
        return (x * self.scale_factor, y * self.scale_factor)
