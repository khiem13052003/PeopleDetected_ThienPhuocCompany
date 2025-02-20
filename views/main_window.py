from PyQt6.QtWidgets import QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng Desktop")
        self.setGeometry(100, 100, 800, 600)
        self.label = QLabel("Xin chào!", self)