# PixelPerfect Type - 项目结构

```
字号自动测量器2/
│
├── 📄 README.md                    # 主文档（7000+字）
├── 📄 PROJECT_SUMMARY.md           # 项目总结
├── 🚀 start.sh                     # 快速启动脚本
│
├── 📁 backend/                     # 后端服务
│   ├── 🐍 app.py                  # Flask主应用（220行）
│   ├── 📋 requirements.txt        # Python依赖
│   │
│   ├── 📁 utils/                  # 核心模块
│   │   ├── __init__.py           # 包初始化
│   │   ├── image_processor.py    # View 1: 图像标准化（88行）
│   │   ├── ocr_detector.py       # View 2: OCR识别（107行）
│   │   ├── font_fitter.py        # View 3: 字号拟合（280行）⭐核心
│   │   └── annotator.py          # View 4: 结果标注（145行）
│   │
│   ├── 📁 uploads/                # 上传文件存储
│   ├── 📁 outputs/                # 处理结果输出
│   └── 📁 fonts/                  # 字体文件目录
│
├── 📁 frontend/                   # 前端界面
│   ├── 🌐 index.html             # 主页面（360行）
│   └── 📁 src/
│       └── app.js                # 前端逻辑（280行）
│
└── 📁 docs/                       # 文档目录
    ├── 📘 QUICKSTART.md          # 快速开始指南
    ├── 📗 ARCHITECTURE.md        # 技术架构详解（4000+字）
    └── 📙 ALGORITHM.md           # 核心算法详解（5000+字）
```

---

## 文件说明

### 📄 根目录

| 文件 | 说明 |
|------|------|
| `README.md` | 完整的项目文档，包含安装、使用、API等所有信息 |
| `PROJECT_SUMMARY.md` | 项目总结，包含技术栈、性能指标、未来规划 |
| `start.sh` | 一键启动脚本，自动创建虚拟环境并安装依赖 |

---

### 🐍 后端模块

#### `backend/app.py`
Flask API主入口，提供3个核心接口：
- `POST /api/process` - 完整处理流程
- `GET /api/image/{filename}` - 获取图片
- `GET /api/result/{task_id}` - 获取JSON结果

#### `backend/utils/image_processor.py`
**View 1: 图像标准化**
- 类: `ImageNormalizer`
- 功能: 将任意尺寸图片缩放到750px宽度
- 关键方法: `normalize(image_path, output_path)`

#### `backend/utils/ocr_detector.py`
**View 2: OCR文字识别**
- 类: `OCRDetector`
- 功能: 使用PaddleOCR识别文字和位置
- 关键方法: `detect_texts(image_path)`

#### `backend/utils/font_fitter.py` ⭐
**View 3: 字号拟合（核心算法）**
- 类: `FontFitter`
- 功能: 通过像素重合度算法拟合字号
- 关键方法:
  - `fit_font_size()` - 主拟合函数
  - `_evaluate_font_size()` - 评估特定字号
  - `_calculate_iou()` - 计算IoU
  - `render_overlay()` - 渲染红色覆盖层

#### `backend/utils/annotator.py`
**View 4: 结果标注**
- 类: `ResultAnnotator`
- 功能: 生成标注图片和统计报告
- 关键方法:
  - `annotate_image()` - 图片标注
  - `generate_report()` - 生成报告

---

### 🌐 前端模块

#### `frontend/index.html`
- 完整的单页面应用
- 包含HTML结构 + CSS样式
- 四视图切换界面
- 统计卡片展示

#### `frontend/src/app.js`
- 类: `PixelPerfectApp`
- 功能:
  - 文件上传（拖拽支持）
  - API调用
  - 结果可视化
  - 视图切换

---

### 📚 文档模块

#### `docs/QUICKSTART.md`
5分钟快速上手指南
- 安装步骤
- 使用流程
- 常见问题

#### `docs/ARCHITECTURE.md`
技术架构详解（4000+字）
- 系统架构设计
- 技术栈选型
- 模块设计
- 数据流转
- 性能优化
- 部署方案

#### `docs/ALGORITHM.md`
核心算法详解（5000+字）
- 问题定义
- 算法原理
- 伪代码
- 复杂度分析
- 实验验证
- 优化策略

---

## 代码统计

### 后端代码

```
image_processor.py:     88 行
ocr_detector.py:       107 行
font_fitter.py:        280 行  ⭐核心
annotator.py:          145 行
app.py:                220 行
─────────────────────────────
总计:                  840 行
```

### 前端代码

```
index.html:            360 行
app.js:                280 行
─────────────────────────────
总计:                  640 行
```

### 文档

```
README.md:            ~700 行 (7000字)
ARCHITECTURE.md:      ~450 行 (4000字)
ALGORITHM.md:         ~550 行 (5000字)
QUICKSTART.md:        ~200 行
PROJECT_SUMMARY.md:   ~300 行
─────────────────────────────
总计:                ~2200 行 (16000+字)
```

---

## 技术债务

### 当前已知问题

1. **性能优化空间**
   - [ ] GPU加速未启用
   - [ ] 单线程处理，可并行化
   - [ ] 无缓存机制

2. **功能限制**
   - [ ] 仅支持PingFang SC字体
   - [ ] 无批量处理
   - [ ] 无导出PDF功能

3. **代码质量**
   - [ ] 缺少单元测试
   - [ ] 缺少错误处理边界case
   - [ ] 日志系统待完善

---

## 扩展点

### 1. 添加新字体

修改 `backend/utils/font_fitter.py`:

```python
font_fitter = FontFitter(
    font_path="/path/to/custom.ttf"
)
```

### 2. 添加新的处理视图

在 `backend/utils/` 创建新模块，在 `app.py` 中集成。

### 3. 修改前端样式

编辑 `frontend/index.html` 中的 `<style>` 部分。

### 4. 添加新的API接口

在 `backend/app.py` 添加新的路由。

---

## 依赖关系

```
Frontend
   │
   │ HTTP API
   ▼
app.py (Flask)
   │
   ├─> ImageNormalizer
   │
   ├─> OCRDetector
   │      │
   │      └─> PaddleOCR
   │
   ├─> FontFitter
   │      │
   │      ├─> Pillow (字体渲染)
   │      ├─> OpenCV (图像处理)
   │      └─> NumPy (数值计算)
   │
   └─> ResultAnnotator
          │
          └─> OpenCV
```

---

## 启动流程

1. 用户执行 `./start.sh`
2. 脚本检查Python环境
3. 创建/激活虚拟环境
4. 安装依赖（首次）
5. 启动Flask服务（端口5000）
6. 用户在浏览器打开 `frontend/index.html`
7. 前端通过AJAX调用API
8. 后端执行四视图处理
9. 返回结果给前端展示

---

## 注意事项

### 首次运行

- PaddleOCR会自动下载模型文件（~100MB）
- 需要网络连接
- 可能需要5-10分钟

### 字体文件

- macOS: 自动使用系统PingFang SC
- Windows/Linux: 需手动配置字体路径

### 浏览器兼容性

- ✅ Chrome 90+
- ✅ Safari 14+
- ✅ Firefox 88+
- ❌ IE不支持

---

## 备份与恢复

### 备份关键文件

```bash
# 备份上传和输出文件
tar -czf backup.tar.gz backend/uploads backend/outputs

# 备份配置
cp backend/requirements.txt backup/
```

### 清理临时文件

```bash
# 清理上传文件
rm -rf backend/uploads/*

# 清理输出文件
rm -rf backend/outputs/*
```

---

<div align="center">

**📁 项目结构清晰 | 🎯 模块职责明确 | 📖 文档完善详尽**

</div>
