# PixelPerfect Type - 字体验收工具

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**AI驱动的UI字体自动检测与验收工具**

通过像素级重合度算法，自动识别设计稿中的文字字号，提升设计验收效率

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [算法原理](#算法原理)
- [API文档](#api文档)
- [常见问题](#常见问题)

---

## 🎯 项目简介

**PixelPerfect Type** 是一个专为UI设计师和前端开发者打造的自动化字体验收工具。它能够：

✅ 自动检测设计稿中所有文字的字号
✅ 生成详细的字号规范报告
✅ 验证开发还原度
✅ 提取设计规范文档

**适用场景**：
- UI设计规范提取
- 前端还原度验收
- 设计稿字号一致性检查
- 移动端适配验证（基于750px标准）

---

## ⭐ 核心功能

### 四大处理视图 (4 Views Pipeline)

#### View 1: 图像标准化 📐
- 将任意尺寸的UI截图等比缩放到 **750px** 宽度
- 记录缩放因子，确保后续计算准确性
- 支持 JPG、PNG 等常见格式

#### View 2: OCR文字识别 🔍
- 基于 **PaddleOCR** 的高精度文字检测
- 识别所有文本区域的位置和内容
- 提供置信度评分

#### View 3: 字号拟合 🎨
- **核心算法**：像素重合度拟合
- 使用 PingFang SC 字体进行渲染对比
- 二分搜索 + 精细调优，确保最佳匹配
- 红色半透明覆盖层直观展示拟合效果

#### View 4: 结果标注 📊
- 在原图上标注每个文字的检测字号
- 生成字号分布统计报告
- 导出JSON格式的详细数据

---

## 🏗️ 技术架构

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Web)                      │
│  HTML + Vanilla JavaScript + Canvas API                 │
│  - 文件上传                                               │
│  - 结果可视化                                             │
│  - 四视图切换                                             │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP REST API
┌─────────────────┴───────────────────────────────────────┐
│                    Backend (Python)                      │
│  Flask + PaddleOCR + OpenCV + Pillow                    │
├──────────────────────────────────────────────────────────┤
│  📦 Modules:                                             │
│  ├─ image_processor.py    (图像标准化)                   │
│  ├─ ocr_detector.py       (OCR识别)                      │
│  ├─ font_fitter.py        (字号拟合 - 核心算法)          │
│  └─ annotator.py          (结果标注)                     │
└──────────────────────────────────────────────────────────┘
```

### 技术栈

**后端**：
- Python 3.8+
- Flask 3.0 (Web框架)
- PaddleOCR 2.7 (OCR引擎)
- OpenCV 4.8 (图像处理)
- Pillow 10.1 (图像渲染)
- NumPy / SciPy (数值计算)

**前端**：
- 原生 HTML5 + CSS3
- Vanilla JavaScript (无框架依赖)
- Canvas API (图像展示)

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 现代浏览器（Chrome / Safari / Firefox）
- 4GB+ 内存

### 安装步骤

#### 1. 克隆项目

```bash
cd ~/Documents/代码
# 项目已在 字号自动测量器2 目录中
cd 字号自动测量器2
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

**注意**：首次安装PaddleOCR会自动下载模型文件（约100MB），请耐心等待。

#### 3. 启动后端服务

```bash
python app.py
```

服务将在 `http://localhost:9090` 启动。

#### 4. 打开前端界面

使用浏览器打开：

```bash
cd ../frontend
open index.html
```

或者直接在浏览器中打开 `frontend/index.html` 文件。

---

## 📖 使用指南

### 基本流程

1. **上传设计稿**
   点击"选择文件"或直接拖拽图片到上传区域

2. **开始分析**
   点击"开始分析"按钮，等待处理完成

3. **查看结果**
   通过四个视图标签查看不同阶段的结果：
   - **View 1**: 查看标准化后的图片
   - **View 2**: 查看OCR识别结果
   - **View 3**: 查看字号拟合效果（红色半透明覆盖）
   - **View 4**: 查看最终的字号标注结果

4. **分析报告**
   查看统计卡片和字号分布详情

### 最佳实践

✅ **推荐上传750px宽度的设计稿**
虽然工具会自动缩放，但原生750px能获得最佳精度

✅ **确保文字清晰可见**
模糊或过小的文字可能影响识别准确度

✅ **使用PingFang SC字体的设计稿**
拟合算法基于PingFang SC，使用相同字体能获得最佳结果

✅ **避免复杂背景**
纯色或简单渐变背景能提高OCR准确率

---

## 🧮 算法原理

### View 3 核心算法：字号拟合

这是整个工具的**技术核心**，解决了传统OCR无法准确提取字号的问题。

#### 问题定义

OCR只能告诉我们"文字在哪里"，无法告诉我们"字号是多少"。
简单根据边界框高度推测字号是不准确的，因为：
- 不同字符的实际高度不同
- 行高、基线位置影响边界框大小
- 字体的度量标准（font-size）与视觉高度不完全一致

#### 解决方案：像素重合度拟合

**算法流程**：

```
1. 输入：
   - 原图中的文字区域 (从OCR获取)
   - 文字内容 (从OCR获取)

2. 预处理：
   - 将文字区域转为灰度图
   - 二值化处理，提取文字像素

3. 二分搜索（粗略阶段）：
   For font_size in [8, 12, 16, 20, ..., 100]:  // 步长4px
       a. 使用候选字号渲染文字
       b. 尝试不同的基线偏移 (-h/2 到 h/2)
       c. 计算渲染结果与原图的IoU
       d. 记录最佳IoU及对应参数

4. 精细搜索：
   在最佳字号±4px范围内，步长0.5px重复搜索

5. 输出：
   - fitted_font_size: 最佳字号
   - baseline_offset: 基线偏移
   - fit_quality: 拟合质量 (IoU值)
```

**IoU (Intersection over Union) 计算**：

```python
IoU = 交集像素数 / 并集像素数
    = (渲染文字 ∩ 原图文字) / (渲染文字 ∪ 原图文字)
```

**算法复杂度**：
- 时间复杂度：O(n * m * k)
  n = 字号搜索次数，m = 基线搜索次数，k = 像素比较
- 实际性能：单个文字约0.5-2秒（取决于文字长度）

**优化策略**：
1. 先粗后精的两阶段搜索减少计算量
2. 扩展区域确保不遗漏基线变化
3. 自适应阈值应对不同背景

---

## 📡 API文档

### POST /api/process

完整处理流程（一次性完成View 1-4）

**请求**：
```http
POST /api/process
Content-Type: multipart/form-data

Body:
  image: [图片文件]
```

**响应**：
```json
{
  "success": true,
  "task_id": "uuid-string",
  "normalization": {
    "original_size": {"width": 1080, "height": 1920},
    "normalized_size": {"width": 750, "height": 1333},
    "scale_factor": 0.694
  },
  "text_regions": [
    {
      "id": "text_0",
      "text": "欢迎使用",
      "bbox": {"x": 100, "y": 200, "width": 120, "height": 30},
      "fitted_font_size": 28.5,
      "fit_quality": 0.87,
      ...
    }
  ],
  "report": {
    "total_texts": 25,
    "fitted_texts": 23,
    "unique_font_sizes": 5,
    "average_font_size": 24.3,
    "font_size_distribution": {"24": 10, "16": 8, "32": 3, ...}
  },
  "images": {
    "normalized": "/api/image/xxx_normalized.jpg",
    "ocr_detection": "/api/image/xxx_ocr_detection.jpg",
    "overlay": "/api/image/xxx_overlay.jpg",
    "annotated": "/api/image/xxx_annotated.jpg"
  }
}
```

### GET /api/image/{filename}

获取处理后的图片

**响应**：图片文件 (image/jpeg)

### GET /api/result/{task_id}

获取处理结果的JSON数据

---

## ❓ 常见问题

### Q1: 为什么拟合结果不准确？

**可能原因**：
1. 设计稿使用的不是PingFang SC字体
2. 图片质量过低或文字模糊
3. 文字过小（小于8px）或过大（大于100px）

**解决方案**：
- 使用高质量原图
- 确认字体类型
- 调整算法的min_size和max_size参数

### Q2: OCR识别不到某些文字？

**可能原因**：
- 文字与背景对比度过低
- 文字过于倾斜
- 文字被遮挡或部分可见

**解决方案**：
- 提高图片对比度
- 使用正视图
- 确保文字完整可见

### Q3: 处理速度慢？

**原因**：
- PaddleOCR初次加载需要下载模型
- 字号拟合算法计算密集

**优化建议**：
- 使用GPU加速（修改`use_gpu=True`）
- 减少文字区域数量
- 调整搜索范围和步长

### Q4: 能否支持其他字体？

**回答**：可以！修改 `font_fitter.py` 中的字体路径即可：

```python
font_fitter = FontFitter(font_path="/path/to/your/font.ttf")
```

---

## 📊 数据结构定义

### View 2 → View 3 数据结构

```json
{
  "id": "text_0",
  "text": "示例文字",
  "confidence": 0.95,
  "bbox": {
    "x": 120.5,
    "y": 300.2,
    "width": 150.0,
    "height": 32.8
  },
  "center": {
    "x": 195.5,
    "y": 316.6
  },
  "polygon": [
    [120.5, 300.2],
    [270.5, 300.2],
    [270.5, 333.0],
    [120.5, 333.0]
  ],
  "fitted_font_size": 28.5,
  "fitted_baseline": 2,
  "fit_quality": 0.873
}
```

**字段说明**：
- `bbox`: OCR检测的边界框（相对于750px宽图片）
- `polygon`: 文字区域的四个顶点坐标
- `fitted_font_size`: 拟合出的字号（像素）
- `fitted_baseline`: 基线偏移（像素）
- `fit_quality`: 拟合质量，范围0-1，越接近1越好

---

## 📂 项目结构

```
字号自动测量器2/
├── backend/                    # 后端服务
│   ├── app.py                 # Flask主应用
│   ├── requirements.txt       # Python依赖
│   ├── utils/                 # 工具模块
│   │   ├── image_processor.py  # View 1: 图像标准化
│   │   ├── ocr_detector.py     # View 2: OCR识别
│   │   ├── font_fitter.py      # View 3: 字号拟合
│   │   └── annotator.py        # View 4: 结果标注
│   ├── uploads/               # 上传文件目录
│   ├── outputs/               # 输出文件目录
│   └── fonts/                 # 字体文件目录
├── frontend/                  # 前端界面
│   ├── index.html            # 主页面
│   └── src/
│       └── app.js            # 前端逻辑
└── docs/                     # 文档目录
    ├── README.md             # 本文档
    ├── ARCHITECTURE.md       # 架构设计文档
    └── ALGORITHM.md          # 算法详解文档
```

---

## 🔧 开发指南

### 调试模式

开启Flask调试模式：

```python
# app.py
app.run(debug=True)
```

查看详细日志输出。

### 自定义配置

修改 `app.py` 中的配置：

```python
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
```

### 扩展功能

1. **添加新字体支持**
   修改 `FontFitter.__init__()` 中的字体路径

2. **调整拟合参数**
   修改 `fit_font_size()` 的参数：
   - `min_size`: 最小字号
   - `max_size`: 最大字号
   - `tolerance`: 收敛容差

3. **启用GPU加速**
   修改 `OCRDetector(use_gpu=True)`

---

## 📄 License

MIT License - 详见 LICENSE 文件

---

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的OCR引擎
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [OpenCV](https://opencv.org/) - 计算机视觉库

---

## 📮 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

**开发者**: PixelPerfect Type Team
**版本**: 1.0.0
**最后更新**: 2024

---

<div align="center">

**⭐ 如果这个项目对你有帮助，欢迎 Star！⭐**

Made with ❤️ by Claude Sonnet 4.5

</div>
