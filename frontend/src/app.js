/**
 * PixelPerfect Type - 前端应用逻辑
 */

const API_BASE_URL = 'http://localhost:9090';

class PixelPerfectApp {
    constructor() {
        this.selectedFile = null;
        this.currentResult = null;

        this.initElements();
        this.bindEvents();
    }

    initElements() {
        // 上传相关
        this.uploadSection = document.getElementById('uploadSection');
        this.fileInput = document.getElementById('fileInput');
        this.selectFileBtn = document.getElementById('selectFileBtn');
        this.fileName = document.getElementById('fileName');
        this.processBtn = document.getElementById('processBtn');

        // 进度相关
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');

        // 结果相关
        this.resultsSection = document.getElementById('resultsSection');
        this.messageArea = document.getElementById('messageArea');
        this.statsGrid = document.getElementById('statsGrid');

        // 视图切换
        this.tabs = document.querySelectorAll('.tab');
        this.viewContents = document.querySelectorAll('.view-content');

        // 图片元素
        this.normalizedImage = document.getElementById('normalizedImage');
        this.ocrImage = document.getElementById('ocrImage');
        this.overlayImage = document.getElementById('overlayImage');
        this.annotatedImage = document.getElementById('annotatedImage');
        this.fontSizeList = document.getElementById('fontSizeList');
    }

    bindEvents() {
        // 文件选择
        this.selectFileBtn.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // 拖拽上传
        this.uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadSection.classList.add('dragging');
        });

        this.uploadSection.addEventListener('dragleave', () => {
            this.uploadSection.classList.remove('dragging');
        });

        this.uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadSection.classList.remove('dragging');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.handleFileSelect(file);
            }
        });

        // 处理按钮
        this.processBtn.addEventListener('click', () => {
            this.processImage();
        });

        // 视图切换
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchView(tab.dataset.view);
            });
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            this.showMessage('请选择图片文件！', 'error');
            return;
        }

        this.selectedFile = file;
        this.fileName.textContent = `已选择: ${file.name}`;
        this.processBtn.style.display = 'inline-block';

        // 显示预览
        const reader = new FileReader();
        reader.onload = (e) => {
            this.normalizedImage.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    async processImage() {
        if (!this.selectedFile) {
            this.showMessage('请先选择图片！', 'error');
            return;
        }

        // 重置UI
        this.messageArea.innerHTML = '';
        this.resultsSection.style.display = 'none';
        this.progressSection.style.display = 'block';
        this.processBtn.disabled = true;

        // 创建FormData
        const formData = new FormData();
        formData.append('image', this.selectedFile);

        try {
            // 模拟进度更新
            this.updateProgress(10, 'View 1: 图像标准化中...');

            setTimeout(() => {
                this.updateProgress(30, 'View 2: OCR文字识别中...');
            }, 500);

            // 发送请求
            const response = await fetch(`${API_BASE_URL}/api/process`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status}`);
            }

            this.updateProgress(60, 'View 3: 字号拟合中...');

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || '处理失败');
            }

            this.updateProgress(90, 'View 4: 生成结果标注...');

            // 保存结果
            this.currentResult = result;

            // 延迟显示结果，让用户看到完整进度
            setTimeout(() => {
                this.updateProgress(100, '处理完成！');
                setTimeout(() => {
                    this.displayResults(result);
                }, 500);
            }, 500);

        } catch (error) {
            console.error('处理错误:', error);
            this.showMessage(`处理失败: ${error.message}`, 'error');
            this.progressSection.style.display = 'none';
            this.processBtn.disabled = false;
        }
    }

    updateProgress(percent, text) {
        this.progressFill.style.width = `${percent}%`;
        this.progressText.innerHTML = `<span class="spinner"></span>${text}`;
    }

    displayResults(result) {
        this.progressSection.style.display = 'none';
        this.resultsSection.style.display = 'block';
        this.processBtn.disabled = false;

        // 显示统计信息
        this.displayStats(result.report);

        // 加载图片
        this.normalizedImage.src = `${API_BASE_URL}${result.images.normalized}`;
        this.ocrImage.src = `${API_BASE_URL}${result.images.ocr_detection}`;
        this.overlayImage.src = `${API_BASE_URL}${result.images.overlay}`;
        this.annotatedImage.src = `${API_BASE_URL}${result.images.annotated}`;

        // 显示字号列表
        this.displayFontSizeList(result.report);

        // 显示成功消息
        this.showMessage('分析完成！检测到 ' + result.report.fitted_texts + ' 个文本区域', 'success');

        // 滚动到结果区域
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    displayStats(report) {
        const stats = [
            {
                label: '文本总数',
                value: report.total_texts
            },
            {
                label: '成功拟合',
                value: report.fitted_texts
            },
            {
                label: '不同字号',
                value: report.unique_font_sizes
            },
            {
                label: '平均字号',
                value: report.average_font_size ? `${report.average_font_size}px` : 'N/A'
            },
            {
                label: '最常用字号',
                value: report.most_common_size ? `${report.most_common_size}px` : 'N/A'
            },
            {
                label: '字号范围',
                value: report.min_font_size ? `${report.min_font_size} - ${report.max_font_size}px` : 'N/A'
            }
        ];

        this.statsGrid.innerHTML = stats.map(stat => `
            <div class="stat-card">
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            </div>
        `).join('');
    }

    displayFontSizeList(report) {
        if (!report.font_size_distribution) {
            this.fontSizeList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">暂无数据</p>';
            return;
        }

        const sortedSizes = Object.entries(report.font_size_distribution)
            .sort((a, b) => b[1] - a[1]);

        this.fontSizeList.innerHTML = `
            <h3 style="padding: 15px; background: #f9f9f9; margin-bottom: 10px;">字号分布统计</h3>
            ${sortedSizes.map(([size, count]) => `
                <div class="font-size-item">
                    <div>
                        <span class="font-size-value">${size}px</span>
                        <span style="color: #999; margin-left: 10px; font-size: 0.9em;">
                            ${((count / report.fitted_texts) * 100).toFixed(1)}%
                        </span>
                    </div>
                    <span class="font-size-count">${count} 处</span>
                </div>
            `).join('')}
        `;
    }

    switchView(viewId) {
        // 切换tab激活状态
        this.tabs.forEach(tab => {
            if (tab.dataset.view === viewId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // 切换内容显示
        this.viewContents.forEach(content => {
            if (content.id === viewId) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    showMessage(text, type = 'info') {
        const className = type === 'error' ? 'error-message' : 'success-message';
        this.messageArea.innerHTML = `<div class="${className}">${text}</div>`;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new PixelPerfectApp();
});
