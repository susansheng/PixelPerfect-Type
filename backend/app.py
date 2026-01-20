"""
PixelPerfect Type - 字体验收工具后端服务
Flask API 主入口
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import json

from utils.image_processor import ImageNormalizer
from utils.ocr_detector import OCRDetector
from utils.font_fitter import FontFitter
from utils.annotator import ResultAnnotator

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 前端文件路径
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

# 配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 初始化处理器（全局单例，避免重复初始化PaddleOCR）
ocr_detector = None
font_fitter = None


def get_ocr_detector():
    """懒加载OCR检测器"""
    global ocr_detector
    if ocr_detector is None:
        print("正在初始化 PaddleOCR...")
        ocr_detector = OCRDetector()
        print("PaddleOCR 初始化完成")
    return ocr_detector


def get_font_fitter():
    """懒加载字号拟合器"""
    global font_fitter
    if font_fitter is None:
        font_fitter = FontFitter()
    return font_fitter


@app.route('/')
def index():
    """服务前端主页面"""
    return send_from_directory(FRONTEND_FOLDER, 'index.html')


@app.route('/guide')
def guide():
    """服务使用指南页面"""
    return send_from_directory(FRONTEND_FOLDER, 'guide.html')


@app.route('/src/<path:filename>')
def serve_frontend_src(filename):
    """服务前端src目录下的文件"""
    return send_from_directory(os.path.join(FRONTEND_FOLDER, 'src'), filename)


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "ok",
        "service": "PixelPerfect Type API",
        "version": "1.0.0"
    })


@app.route('/api/process', methods=['POST'])
def process_image():
    """
    完整处理流程：View 1-4 一次性完成

    Returns:
        JSON: 包含所有处理结果的数据
    """
    if 'image' not in request.files:
        return jsonify({"error": "未上传图片"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400

    try:
        # 生成唯一ID
        task_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 保存上传的文件（先保存为临时文件）
        temp_path = os.path.join(UPLOAD_FOLDER, f"{task_id}_temp{os.path.splitext(file.filename)[1]}")
        file.save(temp_path)

        # 转换为RGB并保存为JPG（处理RGBA等模式）
        from PIL import Image
        img = Image.open(temp_path)
        if img.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        original_path = os.path.join(UPLOAD_FOLDER, f"{task_id}_original.jpg")
        img.save(original_path, 'JPEG', quality=95)

        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # ============ View 1: 图像标准化 ============
        print(f"[{task_id}] View 1: 图像标准化...")
        normalizer = ImageNormalizer()
        normalized_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_normalized.jpg")
        normalization_result = normalizer.normalize(original_path, normalized_path)
        print(f"[{task_id}] 标准化完成: {normalization_result['scale_factor']:.3f}x")

        # ============ View 2: OCR识别 ============
        print(f"[{task_id}] View 2: OCR文字识别...")
        detector = get_ocr_detector()
        text_regions = detector.detect_texts(normalized_path)
        print(f"[{task_id}] 识别到 {len(text_regions)} 个文本区域")

        # 保存预处理后的图片（如果存在）
        if hasattr(detector, 'preprocessed_img') and detector.preprocessed_img is not None:
            preprocessed_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_preprocessed.jpg")
            import cv2
            # preprocessed_img是RGB格式，转换为BGR保存
            preprocessed_bgr = cv2.cvtColor(detector.preprocessed_img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(preprocessed_path, preprocessed_bgr)
            print(f"[{task_id}] 保存预处理后的图片: {preprocessed_path}")
            # 后续使用预处理后的图片
            working_image_path = preprocessed_path
        else:
            working_image_path = normalized_path

        # 保存OCR可视化结果
        ocr_vis_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_ocr_detection.jpg")
        detector.visualize_detection(normalized_path, text_regions, ocr_vis_path)

        # ============ View 3: 字号拟合 ============
        print(f"[{task_id}] View 3: 字号拟合...")
        fitter = get_font_fitter()

        for idx, region in enumerate(text_regions):
            print(f"[{task_id}] 拟合 {idx+1}/{len(text_regions)}: {region['text'][:20]}...")

            try:
                fit_result = fitter.fit_font_size(
                    working_image_path,  # 使用预处理后的图片（如果存在）
                    region['text'],
                    region['bbox'],
                    min_size=8,
                    max_size=100
                )

                # 更新区域数据
                region['fitted_font_size'] = fit_result['font_size']
                region['fitted_baseline'] = fit_result['baseline_offset']
                region['fit_quality'] = fit_result['fit_quality']

                print(f"[{task_id}]   -> {fit_result['font_size']}px (质量: {fit_result['fit_quality']:.3f})")

            except Exception as e:
                print(f"[{task_id}] 拟合失败: {str(e)}")
                region['fitted_font_size'] = None
                region['fit_quality'] = 0.0

        # 渲染红色半透明覆盖层
        overlay_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_overlay.jpg")
        fitter.render_overlay(working_image_path, text_regions, overlay_path)

        # ============ View 4: 结果标注 ============
        print(f"[{task_id}] View 4: 结果标注...")
        annotator = ResultAnnotator()
        annotated_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_annotated.jpg")
        annotator.annotate_image(working_image_path, text_regions, annotated_path)

        # 生成分析报告
        report = annotator.generate_report(text_regions)

        # 保存JSON结果
        result_json_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_result.json")
        with open(result_json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "task_id": task_id,
                "timestamp": timestamp,
                "normalization": normalization_result,
                "text_regions": text_regions,
                "report": report
            }, f, ensure_ascii=False, indent=2)

        print(f"[{task_id}] 处理完成！")

        # 返回结果
        return jsonify({
            "success": True,
            "task_id": task_id,
            "normalization": normalization_result,
            "text_regions": text_regions,
            "report": report,
            "images": {
                "normalized": f"/api/image/{task_id}_normalized.jpg",
                "ocr_detection": f"/api/image/{task_id}_ocr_detection.jpg",
                "overlay": f"/api/image/{task_id}_overlay.jpg",
                "annotated": f"/api/image/{task_id}_annotated.jpg"
            }
        })

    except Exception as e:
        import traceback
        import sys
        error_msg = str(e)
        stack_trace = traceback.format_exc()

        # 详细打印错误
        print("\n" + "=" * 60, flush=True)
        print("❌ 处理错误:", flush=True)
        print("=" * 60, flush=True)
        print(f"错误类型: {type(e).__name__}", flush=True)
        print(f"错误信息: {error_msg}", flush=True)
        print("\n完整堆栈:", flush=True)
        print(stack_trace, flush=True)
        print("=" * 60 + "\n", flush=True)
        sys.stdout.flush()
        sys.stderr.flush()

        return jsonify({
            "success": False,
            "error": error_msg,
            "error_type": type(e).__name__
        }), 500


@app.route('/api/image/<filename>', methods=['GET'])
def get_image(filename):
    """获取处理后的图片"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/jpeg')
    else:
        return jsonify({"error": "文件不存在"}), 404


@app.route('/api/result/<task_id>', methods=['GET'])
def get_result(task_id):
    """获取处理结果的JSON数据"""
    result_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_result.json")
    if os.path.exists(result_path):
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "结果不存在"}), 404


if __name__ == '__main__':
    print("=" * 60)
    print("  🎨 PixelPerfect Type - 字体验收工具")
    print("=" * 60)
    print("✨ 服务已启动！")
    print("")
    print("📍 访问地址: http://localhost:9090")
    print("")
    print("💡 使用说明:")
    print("   1. 在浏览器中打开上面的地址")
    print("   2. 上传UI设计稿（JPG/PNG格式）")
    print("   3. 点击'开始分析'按钮")
    print("   4. 查看四个视图的分析结果")
    print("")
    print("🛑 按 Ctrl+C 停止服务")
    print("=" * 60)
    print("")

    app.run(
        host='0.0.0.0',
        port=9090,
        debug=True
    )
