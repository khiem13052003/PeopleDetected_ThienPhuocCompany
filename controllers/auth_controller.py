from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from views.camera_page import CameraWindow
import sqlite3
from PyQt6.QtCore import QTimer
class AuthController:
    def __init__(self):
        # Thông tin đăng nhập cố định
        self.VALID_USERNAME = 'hoatuoitt'
        self.VALID_PASSWORD = 'Thienphuoc2025'

    def login(self, username, password):
        try:
            if username == self.VALID_USERNAME and password == self.VALID_PASSWORD:
                return {
                    'success': True,
                    'user': {
                        'username': username,
                        'role': 'admin'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Tên đăng nhập hoặc mật khẩu không đúng'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi đăng nhập: {str(e)}'
            }

def login(widget: QWidget, username: str, password: str):
    # # Kiểm tra các trường input không được để trống
    if not username or not password:
        QMessageBox.warning(widget, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
        return False
        
    if username == "hoatuoitt" and password == "Thienphuoc2025":
        print("Đăng nhập thành công!")
        widget.hide()  
        camera_window = CameraWindow()
        camera_window.show()
        # Đảm bảo widget login được đóng đúng cách
       # Ẩn widget trước
        return True
    else:
        QMessageBox.warning(widget, "Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")
        print('Tên đăng nhập hoặc mật khẩu không đúng')
        return False

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