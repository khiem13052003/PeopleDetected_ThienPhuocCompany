from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from controllers.camera_controller import CaptureIpCameraFramesWorker, CameraEventHandler, CameraWorkerManager

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user = "hoatuoitt"
        self.pwd = "Thienphuoc2025"
        self.ip1 = "10.0.0.90"
        self.ip2 = "10.0.0.91"
        self.url_1 = f"rtsp://{self.user}:{self.pwd}@{self.ip1}:554/Streaming/Channels/102"
        self.url_2 = f"rtsp://{self.user}:{self.pwd}@{self.ip2}:554/Streaming/Channels/102"
        
        # Dictionary to keep the state of a camera
        self.list_of_cameras_state = {}
        
        # Khởi tạo camera worker manager
        self.camera_manager = CameraWorkerManager(self.url_1, self.url_2)
        
        # Setup UI elements
        self.setup_cameras()
        self.setup_labels()
        self.setup_ui()
        # Initialize workers
        self.setup_workers()

    def setup_cameras(self):
        # Camera 1
        self.camera_1 = QLabel()
        self.camera_1.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.camera_1.setScaledContents(True)
        self.camera_1.installEventFilter(self)
        self.camera_1.setObjectName("Camera_1")
        self.list_of_cameras_state["Camera_1"] = "Normal"

        self.QScrollArea_1 = QScrollArea()
        self.QScrollArea_1.setBackgroundRole(QPalette.ColorRole.Dark)
        self.QScrollArea_1.setWidgetResizable(True)
        self.QScrollArea_1.setWidget(self.camera_1)

        # Camera 2
        self.camera_2 = QLabel()
        self.camera_2.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.camera_2.setScaledContents(True)
        self.camera_2.installEventFilter(self)
        self.camera_2.setObjectName("Camera_2")
        self.list_of_cameras_state["Camera_2"] = "Normal"

        self.QScrollArea_2 = QScrollArea()
        self.QScrollArea_2.setBackgroundRole(QPalette.ColorRole.Dark)
        self.QScrollArea_2.setWidgetResizable(True)
        self.QScrollArea_2.setWidget(self.camera_2)

    def setup_labels(self):
        self.count_label_1 = QLabel("Camera 1: 0 người")
        self.count_label_1.setStyleSheet("QLabel { color: red; font-size: 30px; }")
        
        self.count_label_2 = QLabel("Camera 2: 0 người")
        self.count_label_2.setStyleSheet("QLabel { color: red; font-size: 30px; }")
        
        self.roi_count_label = QLabel("Số người không làm: 0")
        self.roi_count_label.setStyleSheet("QLabel { color: blue; font-size: 30px; }")

    def setup_workers(self):
        # Tạo dictionary chứa các callback functions
        callbacks = {
            'show_camera1': self.ShowCamera1,
            'show_camera2': self.ShowCamera2,
            'update_count1': self.UpdateCount1,
            'update_count2': self.UpdateCount2,
            'update_roi_count': self.UpdateRoiCount
        }
        # Setup workers thông qua manager
        self.camera_manager.setup_workers(callbacks)

    def setup_ui(self):
        self.setWindowTitle("IP Camera System")
        
        # Main widget and layout
        self.widget = QWidget(self)
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add widgets to layout
        self.grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        self.grid_layout.addWidget(self.count_label_1, 1, 0)
        self.grid_layout.addWidget(self.roi_count_label, 2, 0)
        self.grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        self.grid_layout.addWidget(self.count_label_2, 1, 1)

        # Set layout
        self.widget.setLayout(self.grid_layout)
        self.setCentralWidget(self.widget)
        
        # Window settings
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'black';}")

    # Thêm các method từ camera_controller.py
    @pyqtSlot(QImage)
    def ShowCamera1(self, frame: QImage) -> None:
        self.camera_1.setPixmap(QPixmap.fromImage(frame))

    @pyqtSlot(QImage)
    def ShowCamera2(self, frame: QImage) -> None:
        self.camera_2.setPixmap(QPixmap.fromImage(frame))

    @pyqtSlot(int)
    def UpdateCount1(self, count: int) -> None:
        self.count_label_1.setText(f"Camera 1: {count} người")

    @pyqtSlot(int)
    def UpdateCount2(self, count: int) -> None:
        self.count_label_2.setText(f"Camera 2: {count} người")

    @pyqtSlot(int)
    def UpdateRoiCount(self, count: int) -> None:
        self.roi_count_label.setText(f"Số người không làm: {count}")

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if CameraEventHandler.handle_double_click(self, source, event):
            return True
        return super().eventFilter(source, event)

    def closeEvent(self, event) -> None:
        try:
            self.camera_manager.stop_workers()
        except Exception as e:
            print(f"Error closing threads: {e}")
        finally:
            event.accept()






