from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.utils import platform
from kivy.storage.jsonstore import JsonStore
import cv2
import numpy as np
import os
from datetime import datetime

class CrackDetectionMobile(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.current_img = None
        self.current_result = None
        self.video_cap = None
        self.store = JsonStore('crack_detection.json')
        self.init_ui()
        self.setup_storage()

    def setup_storage(self):
        # 确保存储目录存在
        if platform == 'android':
            from android.storage import app_storage_path
            self.storage_path = app_storage_path()
        else:
            self.storage_path = os.path.expanduser('~/crack_detection')
        
        os.makedirs(self.storage_path, exist_ok=True)

    def init_ui(self):
        # 顶部标题
        title = Label(
            text='道路裂缝检测系统',
            size_hint_y=None,
            height=50,
            font_size='20sp'
        )
        self.add_widget(title)

        # 图片显示区域
        self.img_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=300
        )
        
        self.original_img = Image(
            size_hint=(1, 0.5)
        )
        self.result_img = Image(
            size_hint=(1, 0.5)
        )
        
        self.img_container.add_widget(self.original_img)
        self.img_container.add_widget(self.result_img)
        self.add_widget(self.img_container)

        # 参数设置区域
        params_layout = GridLayout(
            cols=2,
            size_hint_y=None,
            height=100,
            spacing=5
        )
        
        params_layout.add_widget(Label(text='检测精度:'))
        self.precision_input = TextInput(
            text='0.25',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        params_layout.add_widget(self.precision_input)
        
        params_layout.add_widget(Label(text='最大面积比:'))
        self.area_input = TextInput(
            text='0.70',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        params_layout.add_widget(self.area_input)
        
        self.add_widget(params_layout)

        # 操作按钮区域
        buttons_layout = GridLayout(
            cols=2,
            size_hint_y=None,
            height=120,
            spacing=5
        )
        
        btn_open_img = Button(
            text='打开图片',
            on_press=self.open_image
        )
        btn_camera = Button(
            text='摄像头检测',
            on_press=self.open_camera
        )
        btn_detect = Button(
            text='开始检测',
            on_press=self.detect_crack
        )
        btn_save = Button(
            text='保存结果',
            on_press=self.save_result
        )
        
        buttons_layout.add_widget(btn_open_img)
        buttons_layout.add_widget(btn_camera)
        buttons_layout.add_widget(btn_detect)
        buttons_layout.add_widget(btn_save)
        
        self.add_widget(buttons_layout)

        # 结果显示区域
        self.result_text = TextInput(
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=100
        )
        self.add_widget(self.result_text)

    def open_image(self, instance):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
            
            from android.storage import primary_external_storage_path
            from jnius import autoclass
            
            # 使用Android的MediaStore API
            Intent = autoclass('android.content.Intent')
            MediaStore = autoclass('android.provider.MediaStore')
            Intent.createChooser = autoclass('android.content.Intent').createChooser
            
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            
            # 启动图片选择器
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            activity.startActivityForResult(intent, 1)
            
            # 在activity_result中处理选择结果
            def on_activity_result(request_code, result_code, intent):
                if request_code == 1 and result_code == -1:  # RESULT_OK
                    uri = intent.getData()
                    if uri:
                        # 读取选择的图片
                        input_stream = activity.getContentResolver().openInputStream(uri)
                        from PIL import Image as PILImage
                        img = PILImage.open(input_stream)
                        img = np.array(img)
                        self.current_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                        self.display_image(self.current_img, self.original_img)
                        self.result_text.text += "图片已加载\n"
            
            activity.bind(on_activity_result=on_activity_result)
        else:
            # 在桌面平台上使用文件对话框
            from tkinter import filedialog
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
            )
            if file_path:
                self.current_img = cv2.imread(file_path)
                self.display_image(self.current_img, self.original_img)
                self.result_text.text += "图片已加载\n"

    def open_camera(self, instance):
        self.video_cap = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update_camera, 1.0/30.0)

    def update_camera(self, dt):
        if self.video_cap is not None and self.video_cap.isOpened():
            ret, frame = self.video_cap.read()
            if ret:
                self.current_img = frame
                result, img_with_box = self.mock_detect(frame)
                self.current_result = result
                self.display_image(img_with_box, self.original_img)
                self.display_image(result, self.result_img)

    def detect_crack(self, instance):
        if self.current_img is not None:
            result, img_with_box = self.mock_detect(self.current_img)
            self.current_result = result
            self.display_image(img_with_box, self.original_img)
            self.display_image(result, self.result_img)
            self.result_text.text += "检测完成\n"
        else:
            self.result_text.text += "请先加载图片或打开摄像头\n"

    def save_result(self, instance):
        if self.current_result is not None:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
                
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"crack_detection_{timestamp}.jpg"
                filepath = os.path.join(self.storage_path, filename)
                
                # 保存图片
                cv2.imwrite(filepath, self.current_result)
                self.result_text.text += f"结果已保存到: {filepath}\n"
                
                # 保存到媒体库
                from android.storage import MediaStore
                MediaStore.Images.Media.insertImage(
                    activity.getContentResolver(),
                    filepath,
                    filename,
                    "Crack Detection Result"
                )
            else:
                # 在桌面平台上使用文件对话框
                from tkinter import filedialog
                import tkinter as tk
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".jpg",
                    filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
                )
                if file_path:
                    cv2.imwrite(file_path, self.current_result)
                    self.result_text.text += f"结果已保存到: {file_path}\n"
        else:
            self.result_text.text += "没有可保存的检测结果\n"

    def display_image(self, cv_img, image_widget):
        # 将OpenCV图像转换为Kivy纹理
        buf = cv2.flip(cv_img, 0)
        buf = buf.tostring()
        texture = Texture.create(size=(cv_img.shape[1], cv_img.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        image_widget.texture = texture

    def mock_detect(self, img):
        # 这里用OpenCV做简单处理模拟检测，你可以替换为深度学习模型推理
        result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = cv2.Canny(result, 100, 200)
        result_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        img_with_box = img.copy()
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 100
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

class CrackDetectionApp(App):
    def build(self):
        return CrackDetectionMobile()

if __name__ == '__main__':
    CrackDetectionApp().run() 