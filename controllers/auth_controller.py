from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

def login(widget: QWidget,username, password):
    # Kiểm tra các trường input không được để trống
    if username == "hoatuoitt" and password == "Thienphuoc2025":
        print("Đăng nhập thành công!")
        from views.camera_page import CameraWindow
        camera_window = CameraWindow()
        camera_window.show()
        widget.close()
    else:
        print ('Tên đăng nhập hoặc mật khẩu không đúng')

