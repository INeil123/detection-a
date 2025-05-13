import sys
import cv2
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLineEdit, QFileDialog, QTextEdit, QGridLayout, QMessageBox,
    QMenuBar, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer

# 设置 Qt 插件路径
import PyQt5
qt_plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugin_path

class CrackDetectionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("基于深度学习的道路裂缝检测与分析系统")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()
        self.current_img = None
        self.current_result = None
        self.video_cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.save_dir = "results"
        os.makedirs(self.save_dir, exist_ok=True)

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 顶部菜单栏
        self.menu_bar = QMenuBar()
        file_menu = self.menu_bar.addMenu("文件")
        model_menu = self.menu_bar.addMenu("模型")
        tool_menu = self.menu_bar.addMenu("工具")
        help_menu = self.menu_bar.addMenu("帮助")
        self.layout().setMenuBar(self.menu_bar)

        # 图片显示区
        self.img_label1 = QLabel("原图")
        self.img_label1.setFixedSize(320, 240)
        self.img_label2 = QLabel("检测结果")
        self.img_label2.setFixedSize(320, 240)

        img_layout = QHBoxLayout()
        img_layout.addWidget(self.img_label1)
        img_layout.addWidget(self.img_label2)

        # 参数设置区
        param_group = QGroupBox("参数设置")
        param_layout = QGridLayout()
        param_layout.addWidget(QLabel("检测精度："), 0, 0)
        self.precision_input = QLineEdit("0.25")
        param_layout.addWidget(self.precision_input, 0, 1)
        param_layout.addWidget(QLabel("最大面积比："), 1, 0)
        self.area_input = QLineEdit("0.70")
        param_layout.addWidget(self.area_input, 1, 1)
        param_group.setLayout(param_layout)

        # 检测结果区
        result_group = QGroupBox("检测结果")
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)

        # 右侧折叠面板
        right_panel = QGroupBox("统计图表/参数高级设置")
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # 操作区
        btn_open_img = QPushButton("打开图片")
        btn_open_img.clicked.connect(self.open_image)
        btn_open_video = QPushButton("打开视频")
        btn_open_video.clicked.connect(self.open_video)
        btn_camera = QPushButton("摄像头检测")
        btn_camera.clicked.connect(self.open_camera)
        btn_detect = QPushButton("开始检测")
        btn_detect.clicked.connect(self.detect_crack)
        btn_save = QPushButton("保存结果")
        btn_save.clicked.connect(self.save_result)

        op_layout = QHBoxLayout()
        op_layout.addWidget(btn_open_img)
        op_layout.addWidget(btn_open_video)
        op_layout.addWidget(btn_camera)
        op_layout.addWidget(btn_detect)
        op_layout.addWidget(btn_save)

        # 主布局
        main_layout.addLayout(img_layout)
        main_layout.addWidget(param_group)
        main_layout.addWidget(result_group)
        main_layout.addLayout(op_layout)
        main_layout.addWidget(right_panel)

        # 底部状态栏
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("模型版本: v1.0 | 检测耗时: 0ms | 硬件状态: 正常")
        self.layout().addWidget(self.status_bar)

    def open_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.bmp)")
        if file:
            img = cv2.imread(file)
            self.current_img = img
            # 加载图片时也显示检测框
            _, img_with_box = self.mock_detect(img)
            self.show_image(img_with_box, self.img_label1)
            self.result_text.append(f"已加载图片：{file}")

    def open_video(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择视频", "", "Videos (*.mp4 *.avi *.mov)")
        if file:
            self.video_cap = cv2.VideoCapture(file)
            self.result_text.append(f"已加载视频：{file}")
            self.timer.start(30)

    def open_camera(self):
        self.video_cap = cv2.VideoCapture(0)
        self.result_text.append("已打开摄像头")
        self.timer.start(30)

    def next_frame(self):
        if self.video_cap is not None and self.video_cap.isOpened():
            ret, frame = self.video_cap.read()
            if ret:
                self.current_img = frame
                # 实时检测
                result, img_with_box = self.mock_detect(frame)
                self.current_result = result
                self.show_image(img_with_box, self.img_label1)
                self.show_image(result, self.img_label2)
            else:
                self.timer.stop()
                self.video_cap.release()
                self.result_text.append("视频/摄像头结束")

    def detect_crack(self):
        if self.current_img is not None:
            result, img_with_box = self.mock_detect(self.current_img)
            self.current_result = result
            self.show_image(img_with_box, self.img_label1)
            self.show_image(result, self.img_label2)
            self.result_text.append("检测完成")
        else:
            QMessageBox.warning(self, "提示", "请先加载图片、视频或摄像头帧！")

    def save_result(self):
        if self.current_result is not None:
            path, _ = QFileDialog.getSaveFileName(self, "保存检测结果", self.save_dir, "Images (*.png *.jpg *.bmp)")
            if path:
                cv2.imwrite(path, self.current_result)
                self.result_text.append(f"检测结果已保存：{path}")
        else:
            QMessageBox.warning(self, "提示", "没有可保存的检测结果！")

    def show_image(self, img, label):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(label.width(), label.height())
        label.setPixmap(pixmap)

    def mock_detect(self, img):
        # 这里用OpenCV做简单处理模拟检测，你可以替换为深度学习模型推理
        result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = cv2.Canny(result, 100, 200)
        # 生成三通道分割结果
        result_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        # 在原图上也画框
        img_with_box = img.copy()
        # 绘制检测框和标签（增加面积过滤）
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 100  # 面积阈值，可根据实际图片调整
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(result_color, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.rectangle(img_with_box, (x, y), (x+w, y+h), (0, 255, 0), 2)
            label = f"{int(area)} px"
            cv2.putText(result_color, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(img_with_box, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return result_color, img_with_box

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CrackDetectionUI()
    window.show()
    sys.exit(app.exec_())