import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog
import os


CONFIG_FILE = "config.json"

def save_config(data):
    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file)

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

class TelegramSettingsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("Telegram Settings")
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()

        self.label_token = QLabel("Bot Token:")
        layout.addWidget(self.label_token)
        self.input_token = QLineEdit()
        layout.addWidget(self.input_token)
        self.checkbox_token = QCheckBox("Lưu Token")
        layout.addWidget(self.checkbox_token)

        self.label_chat_id = QLabel("Chat ID:")
        layout.addWidget(self.label_chat_id)
        self.input_chat_id = QLineEdit()
        layout.addWidget(self.input_chat_id)
        self.checkbox_chat_id = QCheckBox("Lưu Chat ID")
        layout.addWidget(self.checkbox_chat_id)

        self.btn_confirm = QPushButton("Xác nhận")
        self.btn_confirm.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_confirm)

        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.clicked.connect(self.close)
        layout.addWidget(self.btn_cancel)

        self.btn_help = QPushButton("Hướng dẫn lấy Token và Chat ID")
        self.btn_help.clicked.connect(self.open_notepad)
        layout.addWidget(self.btn_help)

        self.warning= QLabel("⚠️ Khi thay đổi 1 trong 2 hãy khởi động lại ứng dụng")
        layout.addWidget(self.warning)
        self.warning.setStyleSheet("QLabel{font-size: 15px; color: red;}")
        
        
        self.setLayout(layout)
        self.load_saved_data()

    def save_settings(self):
        config = load_config()
        if self.checkbox_token.isChecked():
            config["token"] = self.input_token.text()
        else:
            config.pop("token", None)

        if self.checkbox_chat_id.isChecked():
            config["chat_id"] = self.input_chat_id.text()
        else:
            config.pop("chat_id", None)

        save_config(config)
        print("tele_page:",self.input_chat_id.text() )
        self.close()

    def load_saved_data(self):
        config = load_config()
        if "token" in config:
            self.input_token.setText(config["token"])
            self.checkbox_token.setChecked(True)
        if "chat_id" in config:
            self.input_chat_id.setText(config["chat_id"])
            self.checkbox_chat_id.setChecked(True)

    def open_notepad(self):
        """Mở hướng dẫn lấy Token và ID Telegram trong Notepad"""
        guide_text = """Cách lấy Token & ID Telegram:

1. Mở Telegram và tìm bot: @BotFather
2. Gõ /newbot và làm theo hướng dẫn để lấy Token.
3. Để lấy Chat ID, tìm bot: @userinfobot, gõ /start.
4. Nhập tên Bot của bạn lên thanh tìm kiếm, chọn và nhấn /start 
5. Bot sẽ gửi lại Chat ID của bạn.

Lưu lại Token và ID để sử dụng!"""
                
        guide_path = "telegram_guide.txt"
        with open(guide_path, "w", encoding="utf-8") as file:
            file.write(guide_text)
        os.system(f'notepad.exe {guide_path}')

def run_gui():
    if not QApplication.instance():  # Kiểm tra xem có QApplication đang chạy không
            app = QApplication(sys.argv)
    else:
        app = QApplication.instance()  # Dùng instance hiện tại
        
    window = TelegramSettingsGUI()
    window.show()
        
    if not QApplication.instance():  # Chỉ chạy exec nếu chưa có event loop
        app.exec()
