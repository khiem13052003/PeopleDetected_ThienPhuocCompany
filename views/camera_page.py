from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import QtCore
import cv2
from ultralytics import YOLO
import sys
import numpy as np
from controllers.camera_controller import CaptureIpCameraFramesWorker

class CameraWindow(QMainWindow):
    def __init__(self) -> None:
        super(CameraWindow, self).__init__()
        self.user = "hoatuoitt"
        self.pwd = "Thienphuoc2025"
        self.ip1 = "10.0.0.90"
        self.ip2 = "10.0.0.91"
        self.url_1 = f"rtsp://{self.user}:{self.pwd}@{self.ip1}:554/Streaming/Channels/102"
        self.url_2 = f"rtsp://{self.user}:{self.pwd}@{self.ip2}:554/Streaming/Channels/102"
        
        # Dictionary to keep the state of a camera
        self.list_of_cameras_state = {}

        # Setup UI elements
        self.setup_cameras()
        self.setup_labels()
        self.__SetupUI()
        
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
        self.CaptureIpCameraFramesWorker_1 = CaptureIpCameraFramesWorker(self.url_1, camera_id=1)
        self.CaptureIpCameraFramesWorker_1.ImageUpdated.connect(self.ShowCamera1)
        self.CaptureIpCameraFramesWorker_1.CountUpdated.connect(self.UpdateCount1)
        self.CaptureIpCameraFramesWorker_1.RoiCountUpdated.connect(self.UpdateRoiCount)

        self.CaptureIpCameraFramesWorker_2 = CaptureIpCameraFramesWorker(self.url_2, camera_id=2)
        self.CaptureIpCameraFramesWorker_2.ImageUpdated.connect(self.ShowCamera2)
        self.CaptureIpCameraFramesWorker_2.CountUpdated.connect(self.UpdateCount2)

        # Start camera threads
        self.CaptureIpCameraFramesWorker_1.start()
        self.CaptureIpCameraFramesWorker_2.start()

    def __SetupUI(self) -> None:
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        grid_layout.addWidget(self.count_label_1, 1, 0)
        grid_layout.addWidget(self.roi_count_label, 2, 0)
        grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        grid_layout.addWidget(self.count_label_2, 1, 1)

        self.widget = QWidget(self)
        self.widget.setLayout(grid_layout)

        self.setCentralWidget(self.widget)
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'black';}")
        self.setWindowIcon(QIcon(QPixmap("camera_2.png")))
        self.setWindowTitle("IP Camera System")

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
        if event.type() == QEvent.Type.MouseButtonDblClick:
            if source.objectName() == 'Camera_1':
                if self.list_of_cameras_state["Camera_1"] == "Normal":
                    self.QScrollArea_2.hide()
                    self.list_of_cameras_state["Camera_1"] = "Maximized"
                    self.count_label_1.show()
                    self.count_label_2.hide()
                    self.roi_count_label.show()
                else:
                    self.QScrollArea_2.show()
                    self.list_of_cameras_state["Camera_1"] = "Normal"
                    self.count_label_1.show()
                    self.count_label_2.show()
                    self.roi_count_label.show()
            elif source.objectName() == 'Camera_2':
                if self.list_of_cameras_state["Camera_2"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.list_of_cameras_state["Camera_2"] = "Maximized"
                    self.count_label_2.show()
                    self.count_label_1.hide()
                    self.roi_count_label.hide()
                else:
                    self.QScrollArea_1.show()
                    self.list_of_cameras_state["Camera_2"] = "Normal"
                    self.count_label_2.show()
                    self.count_label_1.show()
                    self.roi_count_label.show()
            else:
                return super(CameraWindow, self).eventFilter(source, event)
            return True
        else:
            return super(CameraWindow, self).eventFilter(source, event)

    def closeEvent(self, event) -> None:
        if self.CaptureIpCameraFramesWorker_1.isRunning():
            self.CaptureIpCameraFramesWorker_1.quit()
        if self.CaptureIpCameraFramesWorker_2.isRunning():
            self.CaptureIpCameraFramesWorker_2.quit()
        event.accept()


def main() -> None:
    # Create a QApplication object. It manages the GUI application's control flow and main settings.
    # It handles widget specific initialization, finalization.
    # For any GUI application using Qt, there is precisely one QApplication object
    app = QApplication(sys.argv)
    # Create an instance of the class MainWindow.
    window = CameraWindow()
    # Show the window.
    window.show()
    # Start Qt event loop.
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

