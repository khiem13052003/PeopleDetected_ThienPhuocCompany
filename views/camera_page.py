from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import QtCore
import cv2
from ultralytics import YOLO
import sys
import numpy as np
from controllers.camera_controller import CaptureIpCameraFramesWorker, CameraController
from PyQt6.QtCore import QDateTime

class TimerWidget(QWidget):
    def __init__(self, camera_controller, parent=None):
        super(TimerWidget, self).__init__(parent)
        self.camera_controller = camera_controller
        self.setFixedSize(250, 700)
        #create layout
        layout= QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        
       
        #create widgets
        self.start_label= QLabel("Thời gian bắt đầu:")
        self.start_label.setStyleSheet("QLabel{color: white; font-size: 15px;}")

        self.start_time_edit= QDateTimeEdit()
        self.start_time_edit.setDateTime(QDateTime.currentDateTime())

        self.end_label= QLabel("Thời gian kết thúc:")
        self.end_label.setStyleSheet("QLabel{color: white; font-size: 15px;}")

        self.end_time_edit= QDateTimeEdit()
        self.end_time_edit.setDateTime(QDateTime.currentDateTime().addSecs(300))

        self.gap_time= QLabel("khoảng thời gian giữa 2 lần đếm: ")
        self.gap_time.setStyleSheet("QLabel{color: white; font-size: 15px;}")
        self.gap_time_edit= QTimeEdit()
        self.gap_time_edit.setTime(QTime(0, 0, 5))
        self.gap_time_edit.setDisplayFormat("HH:mm:ss")

        self.number_people_label= QLabel("Số người mong muốn: ")
        self.number_people_label.setStyleSheet("QLabel{color: white; font-size: 15px;}")
        self.number_people_edit= QLineEdit()
        self.number_people_edit.setPlaceholderText("Nhập số người")
        self.number_people_edit.setValidator(QIntValidator())

        self.delete_button= QPushButton("Hủy thông tin")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setStyleSheet("QPushButton#deleteButton{color: white; font-size: 15px;}")

        self.submit_button= QPushButton("Xác nhận")
        self.submit_button.setStyleSheet("QPushButton{color: white; font-size: 15px;}")
        self.submit_button.clicked.connect(self.submit_info)
        
        self.result_text= QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("QTextEdit{color: white; font-size: 15px;}")
        
        self.save_path_edit= QLineEdit()
        self.save_path_edit.setObjectName('savePathEdit')
        self.save_path_edit.setPlaceholderText("Nhập đường dẫn lưu file")
 
        self.browse_button=QPushButton("📂")
        self.browse_button.setObjectName('browseButton')
        self.browse_button.setStyleSheet("QPushButton#browseButton{font-size: 15px; background-color: #FFFFFF;}")
        self.browse_button.clicked.connect(self.browse_file)
        
        self.save_csv_button= QPushButton("Lưu file csv")
        self.save_csv_button.setObjectName('saveCSVButton')
        self.save_csv_button.setStyleSheet("QPushButton#saveCSVButton{color: black; font-size: 15px;}")
        self.save_csv_button.clicked.connect(self.save_csv)

        self.msg_box= QMessageBox()
        self.msg_box.setWindowTitle("Cảnh báo")
        self.msg_box.setText("File hôm nay đã được lưu")
        self.msg_box.setInformativeText("Bạn có muốn lưu lại file mới ?")
        self.msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        self.msg_box.button(QMessageBox.StandardButton.Ok).setText("Tiếp tục")
        self.msg_box.button(QMessageBox.StandardButton.Cancel).setText("Hủy")

       
        path_layout=QHBoxLayout()
        path_layout.addWidget(self.save_path_edit)
        path_layout.addWidget(self.browse_button)
        
        #add widgets to layout
        layout.addWidget(self.start_label)
        layout.addWidget(self.start_time_edit)
        layout.addWidget(self.end_label)
        layout.addWidget(self.end_time_edit)
        layout.addWidget(self.gap_time)
        layout.addWidget(self.gap_time_edit)
        layout.addWidget(self.number_people_label)
        layout.addWidget(self.number_people_edit)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.result_text)
        layout.addLayout(path_layout)
        layout.addWidget(self.save_csv_button)

        #set layout
        self.setLayout(layout)
        self.hide()

        # set window flags
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: white;
                min-width: 600px;
                min-height: 200px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 6px 20px;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        
        
        #set stylesheet for the widget
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
                border: 2px solid none;
                border-radius: 10px;
            }
            QPushButton {
                color: white;
                background-color: #2196F3;
                border: none;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton#deleteButton{
                color: white;
                background-color:  #F44336;  
                border: none;
                padding: 5px;
                border-radius: 5px;    
            }   
            QPushButton#saveCSVButton{
                color: black;
                background-color:    #FFFFFF;
                border: 1px solid black;
                padding: 5px;
                border-radius: 5px;       
              
            }
            QDateTimeEdit {
                color: white;
                background-color: #424242;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 4px;
                min-height: 35px;
                font-size: 16px;
            }
            QDateTimeEdit::up-button, QDateTimeEdit::down-button {
                width: 30px;
                height: 17px;
                border: 1px solid #666;
                background-color: #555;
            }
            QDateTimeEdit::up-button:hover, QDateTimeEdit::down-button:hover {
                background-color: #666;
            }
            QDateTimeEdit::up-arrow {
                image: url(assets/icons/angle-small-up.png);
                width: 12px;
                height: 12px;
            }
            QDateTimeEdit::down-arrow {
                image: url(assets/icons/angle-small-down.png);
                width: 12px;
                height: 12px;
            }
            QLineEdit {
                color: white;
                background-color: #424242;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit#savePathEdit{
                color: white;
                background-color: #424242;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 4px;
            }
            QTimeEdit {
                color: white;
                background-color: #424242;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 4px;
            }
            QTextEdit{
                color: white;
                background-color: #8a8a8a;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 4px;
                font-size: 16px;
                height: 300px;
           }
        """)

        # Kết nối các nút với controller
        self.submit_button.clicked.connect(self.submit_info)
        self.delete_button.clicked.connect(self.delete_info)

    
    def submit_info(self):
        self.camera_controller.handle_submit_info(self)

    def delete_info(self):
        self.camera_controller.handle_delete_info(self)

    def browse_file(self):
        self.camera_controller.browse_file(self)
    
    def save_csv(self):
        self.camera_controller.save_csv(self)
    
    
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

        # Khởi tạo camera_controller trước
        self.camera_controller = CameraController(self)
        
        # Setup UI elements
        self.setup_cameras()
        self.setup_labels()
        
        # Truyền camera_controller vào TimerWidget
        self.timer_widget = TimerWidget(self.camera_controller, self)
        
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
        
        self.roi_count_label_1 = QLabel("ROI Camera 1: 0 người")
        self.roi_count_label_1.setStyleSheet("QLabel { color: blue; font-size: 30px; }")
        
        self.roi_count_label_2 = QLabel("ROI Camera 2: 0 người")
        self.roi_count_label_2.setStyleSheet("QLabel { color: blue; font-size: 30px; }")
        now = QDateTime.currentDateTime()
        self.date_time_label = QLabel(f"Time: {now.toString('dd/MM/yyyy hh:mm:ss')}")
        self.date_time_label.setStyleSheet("QLabel { color: white; font-size: 20px; }")
        
    
    def setup_workers(self):
        self.CaptureIpCameraFramesWorker_1 = CaptureIpCameraFramesWorker(self.url_1, camera_id=1)
        self.CaptureIpCameraFramesWorker_1.ImageUpdated.connect(self.ShowCamera1)
        self.CaptureIpCameraFramesWorker_1.CountUpdated.connect(self.UpdateCount1)
        self.CaptureIpCameraFramesWorker_1.RoiCountUpdated.connect(self.UpdateRoiCount1)

        self.CaptureIpCameraFramesWorker_2 = CaptureIpCameraFramesWorker(self.url_2, camera_id=2)
        self.CaptureIpCameraFramesWorker_2.ImageUpdated.connect(self.ShowCamera2)
        self.CaptureIpCameraFramesWorker_2.CountUpdated.connect(self.UpdateCount2)
        self.CaptureIpCameraFramesWorker_2.RoiCountUpdated.connect(self.UpdateRoiCount2)

        # Start camera threads
        
        self.CaptureIpCameraFramesWorker_1.start()
        self.CaptureIpCameraFramesWorker_2.start()

    def __SetupUI(self) -> None:
        
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        grid_layout.addWidget(self.count_label_1, 1, 0)
        grid_layout.addWidget(self.roi_count_label_1, 2, 0)
        grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        grid_layout.addWidget(self.count_label_2, 1, 1) 
        grid_layout.addWidget(self.roi_count_label_2, 2, 1)
        grid_layout.addWidget(self.date_time_label, 3,0,1,2)
        grid_layout.addWidget(self.timer_widget, 0, 2, 1, 2)

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
    def UpdateRoiCount1(self, count: int) -> None:
        self.roi_count_label_1.setText(f"ROI Camera 1: {count} người")

    @pyqtSlot(int)
    def UpdateRoiCount2(self, count: int) -> None:
        self.roi_count_label_2.setText(f"ROI Camera 2: {count} người")

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonDblClick:
            if source in [ self.camera_2]:
                camera_pos= source.mapToGlobal(source.rect().topRight())
                self.timer_widget.move(camera_pos.x() +10 ,camera_pos.y())
                self.timer_widget.show()
                
            return self.camera_controller.handle_double_click(source)
        return super(CameraWindow, self).eventFilter(source, event)
    
    def closeEvent(self, event) -> None:
        self.timer_widget.close()
        self.camera_controller.cleanup()
        if self.CaptureIpCameraFramesWorker_1.isRunning():
            self.CaptureIpCameraFramesWorker_1.quit()
        if self.CaptureIpCameraFramesWorker_2.isRunning():
            self.CaptureIpCameraFramesWorker_2.quit()
        event.accept()


# def main() -> None:
#     # Create a QApplication object. It manages the GUI application's control flow and main settings.
#     # It handles widget specific initialization, finalization.
#     # For any GUI application using Qt, there is precisely one QApplication object
#     app = QApplication(sys.argv)
#     # Create an instance of the class MainWindow.
#     window = CameraWindow()
#     # Show the window.
#     window.show()
#     # Start Qt event loop.
#     sys.exit(app.exec())


# if __name__ == '__main__':
#     main()

