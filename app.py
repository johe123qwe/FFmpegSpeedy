import sys
import ffmpeg
import platform
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QMessageBox, QSlider, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction

root_path = os.path.join(os.path.dirname(__file__))

class FfmpegGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('FFmpeg 转换音频速度v1.1')
        self.setGeometry(100, 100, 400, 250)
        self.setWindowIcon(QIcon(os.path.join(root_path, 'src', 'logo.png')))  # 设置窗口图标

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Input file selection
        self.input_label = QLabel('导入文件:', self)
        layout.addWidget(self.input_label)

        self.input_path = QLineEdit(self)
        self.input_path.setFixedHeight(28)
        self.input_path.setAcceptDrops(True)
        self.input_path.dragEnterEvent = self.dragEnterEvent
        self.input_path.dropEvent = self.dropEvent
        layout.addWidget(self.input_path)

        self.input_button = QPushButton('浏览', self)
        self.input_button.setIcon(QIcon(os.path.join(root_path, 'src', 'file.png')))
        self.input_button.clicked.connect(self.browse_input_file)
        layout.addWidget(self.input_button)

        # Audio speed setting
        self.speed_label = QLabel('音频速度 (0.5 - 2.0):', self)
        layout.addWidget(self.speed_label)

        self.speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(97)  # Set default value to 0.97
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.update_speed_label)

        self.speed_value_label = QLabel('0.97', self)

        self.speed_layout.addWidget(self.speed_slider)
        self.speed_layout.addWidget(self.speed_value_label)

        layout.addLayout(self.speed_layout)

        # Output file selection
        self.output_label = QLabel('导出文件:', self)
        layout.addWidget(self.output_label)

        self.output_path = QLineEdit(self)
        self.output_path.setFixedHeight(28)
        layout.addWidget(self.output_path)

        self.output_button = QPushButton('浏览', self)
        self.output_button.setIcon(QIcon(os.path.join(root_path, 'src', 'file.png')))
        self.output_button.clicked.connect(self.browse_output_file)
        layout.addWidget(self.output_button)

        # Codec selection
        self.codec_label = QLabel('音频编码:', self)
        layout.addWidget(self.codec_label)

        self.codec_combo = QComboBox(self)
        self.codec_combo.addItems(['pcm_s16le', 'aac', 'mp3'])
        self.codec_combo.currentIndexChanged.connect(self.update_output_extension)
        layout.addWidget(self.codec_combo)

        # Process button
        self.process_button = QPushButton('转换', self)
        self.process_button.setIcon(QIcon(os.path.join(root_path, 'src', 'conversion.png')))
        self.process_button.clicked.connect(self.process_audio)
        layout.addWidget(self.process_button)

        # Create menu bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu('帮助')

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self.input_path.setText(urls[0].toLocalFile())
            self.set_output_path()

    def browse_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Audio Files (*.mp3 *.wav *.aac *.flac)')
        if file_name:
            self.input_path.setText(file_name)
            self.set_output_path()

    def browse_output_file(self):
        codec = self.codec_combo.currentText()
        ext_map = {
            'pcm_s16le': 'wav',
            'aac': 'aac',
            'mp3': 'mp3'
        }
        ext = ext_map.get(codec, 'wav')
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', f'Audio Files (*.{ext})', options=options)
        if file_name:
            self.output_path.setText(file_name)

    def set_output_path(self):
        input_file = self.input_path.text()
        if input_file:
            base, _ = os.path.splitext(input_file)
            codec = self.codec_combo.currentText()
            ext_map = {
                'pcm_s16le': 'wav',
                'aac': 'aac',
                'mp3': 'mp3'
            }
            ext = ext_map.get(codec, 'wav')
            speed_value = self.speed_slider.value() / 100
            if speed_value < 1.0:
                output_file = f"{base}-拉慢.{ext}"
            else:
                output_file = f"{base}-加速.{ext}"
            self.output_path.setText(output_file)

    def update_output_extension(self):
        self.set_output_path()

    def update_speed_label(self):
        speed_value = self.speed_slider.value() / 100
        self.speed_value_label.setText(f"{speed_value:.2f}")
        self.set_output_path()

    def process_audio(self):
        input_file = self.input_path.text()
        output_file = self.output_path.text()
        speed = self.speed_slider.value() / 100
        codec = self.codec_combo.currentText()

        if not input_file or not output_file:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if os.path.exists(output_file):
            reply = QMessageBox.question(self, "文件已存在", f"{output_file} 文件已存在。是否覆盖？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        try:
            if getattr(sys, 'frozen', False):
                # The application is frozen
                ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg')
            else:
                # The application is not frozen
                if platform.system() == 'Windows':
                    ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'ffmpeg.exe')
                elif platform.system() == 'Darwin':
                    ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'ffmpeg')

            ffmpeg.input(input_file).output(output_file, **{
                'filter:a': f'atempo={speed}',
                'c:a': codec
            }).overwrite_output().run(cmd=ffmpeg_path)
            QMessageBox.information(self, "成功", "已经转换")
        except Exception as e:
            QMessageBox.critical(self, "Processing Error", f"Error processing audio: {e}")

    def show_about_dialog(self):
        QMessageBox.about(self, "关于", "v1.1 这个程序是用来转换音频速度的工具。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FfmpegGui()
    ex.show()
    sys.exit(app.exec())
