import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from controllers.auth_controller import AuthController

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng nhập")
        self.setGeometry(100, 100, 400, 300)
        self.setup_ui()
        self.auth_controller = AuthController()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Tạo layout cho logo   
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()

        # Tạo layout cho form đăng nhập
        form_layout = QVBoxLayout()
        
        # Tạo trường username
        username_layout = QHBoxLayout()
        username_label = QLabel("Tên đăng nhập:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Tạo trường password
        password_layout = QHBoxLayout()
        password_label = QLabel("Mật khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # Thêm các trường vào form layout
        form_layout.addLayout(username_layout)
        form_layout.addLayout(password_layout)

        # Tạo nút đăng nhập
        login_button = QPushButton("Đăng nhập")
        login_button.setFixedHeight(35)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        login_button.clicked.connect(self.login)

        # Tạo layout cho các widget
        layout.addSpacing(20)
        layout.addLayout(logo_layout)
        layout.addSpacing(20)
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(login_button)
        layout.addStretch()

        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Kiểm tra các trường input không được để trống
        if not username or not password:
            QMessageBox.warning(
                self,
                "Lỗi",
                "Vui lòng nhập đầy đủ thông tin đăng nhập",
                QMessageBox.StandardButton.Ok
            )
            return

        # Thực hiện đăng nhập
        result = self.auth_controller.login(username, password)
        
        if result['success']:
            QMessageBox.information(
                self,
                "Thành công",
                f"Chào mừng {result['user']['username']}!",
                QMessageBox.StandardButton.Ok
            )
            # Sửa lại phần import này
            from views.camera_page import CameraWindow
            self.camera_window = CameraWindow()
            self.camera_window.show()
            self.close()
        else:
            QMessageBox.warning(
                self,
                "Lỗi",
                result['message'],
                QMessageBox.StandardButton.Ok
            )
