import PyInstaller.__main__
import os
import sys
import PyQt5

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

print("开始打包过程...")
print(f"当前工作目录: {current_dir}")

# 获取PyQt5插件路径
qt_plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
print(f"Qt插件路径: {qt_plugin_path}")

# 确保必要的目录存在
required_dirs = ['src', 'dataset', 'results']
for dir_name in required_dirs:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f"创建目录: {dir_name}")

# 定义图标路径（如果有的话）
# icon_path = os.path.join(current_dir, 'icon.ico')

# 定义需要打包的文件和资源
PyInstaller.__main__.run([
    'ui_main.py',  # 主程序文件
    '--name=智能道路裂缝检测系统',  # 应用名称
    '--windowed',  # 使用GUI模式
    '--noconfirm',  # 不询问确认
    '--clean',  # 清理临时文件
    # f'--icon={icon_path}',  # 应用图标
    '--add-data=src;src',  # 添加源代码目录
    '--add-data=dataset;dataset',  # 添加数据集目录
    '--add-data=results;results',  # 添加结果目录
    # f'--add-data={qt_plugin_path};PyQt5/Qt5/plugins',  # 添加Qt插件（已注释）
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=cv2',
    '--hidden-import=numpy',
    '--onefile',  # 打包成单个文件
    '--log-level=DEBUG',  # 添加详细日志
])

print("打包过程完成！") 