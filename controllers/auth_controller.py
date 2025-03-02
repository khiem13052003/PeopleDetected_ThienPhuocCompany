from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from views.camera_page import CameraWindow

class AuthController:
    def __init__(self):
        # Thông tin đăng nhập cố định
        self.VALID_USERNAME = 'hoatuoitt'
        self.VALID_PASSWORD = 'Thienphuoc2025'

    def validate_login_input(self, username, password):
        if not username or not password:
            return {'success': False, 'message': "Vui lòng nhập đầy đủ thông tin đăng nhập"}
        return {'success': True}

    def login(self, username, password):
        if username == self.VALID_USERNAME and password == self.VALID_PASSWORD:
            return {'success': True, 'user': {'username': username, 'role': 'admin'}}
        return {'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng'}

    def handle_login(self, username, password):
        validation_result = self.validate_login_input(username, password)
        if not validation_result['success']:
            return validation_result
        return self.login(username, password)

def login(widget: QWidget, username: str, password: str):
    auth = AuthController()
    result = auth.handle_login(username, password)

    if not result['success']:
        QMessageBox.warning(widget, "Lỗi", result['message'])
        return False

    print("Đăng nhập thành công!")
    widget.hide()  
    camera_window = CameraWindow()
    camera_window.show()
    return True

