import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut, QIcon, QFont
from controllers.auth_controller import AuthController
from PyQt6.QtCore import QTimer
import os

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.setWindowTitle("Đăng nhập")
        self.setWindowIcon(QIcon( r'C:\Intern\PeopleDetected_ThienPhuocCompany\assets\icons\desktop_icon.png'))
        self.setGeometry(100, 100, 400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()

        # Tạo layout cho logo   
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap()#r'C:\Intern\PeopleDetected_ThienPhuocCompany\assets\icons\desktop_icon.png')
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
        # Gán QShortcut cho phím Enter (Return)
        self.shortcut = QShortcut(QKeySequence("Return"), self)
        self.shortcut.activated.connect(self.login)

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

        result = self.auth_controller.handle_login(username, password)
        
        if result['success']:
            QTimer.singleShot(1000, self.switch_to_camera)
        else:
            QMessageBox.warning(
                self,
                "Lỗi",
                result['message'],
                QMessageBox.StandardButton.Ok
            )

    def switch_to_camera(self):
        # Chuyển sang trang camera
        from views.camera_page import CameraWindow
        self.camera_window = CameraWindow()
        self.camera_window.show()
        self.close()
        