from PyQt6.QtCore import QThread, pyqtSignal, Qt, QObject, QEvent, QTimer, QDateTime, QTime
from PyQt6.QtGui import QImage
import cv2
from ultralytics import YOLO
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys
import os
import matplotlib.pyplot as plt
import csv
class CaptureIpCameraFramesWorker(QThread):
    ImageUpdated = pyqtSignal(QImage)
    CountUpdated = pyqtSignal(int)
    RoiCountUpdated = pyqtSignal(int)
    TotalCountUpdated = pyqtSignal(int)

    def __init__(self, url, camera_id) -> None:
        super(CaptureIpCameraFramesWorker, self).__init__()
        self.total_count = 0
        self.url = url
        self.camera_id = camera_id
        self.__thread_active = True
        self.fps = 0
        self.__thread_pause = False
        self.modelPath = r'C:\Intern\PeopleDetected_ThienPhuocCompany\assets\model\bestyolo5.pt'
        self.model = YOLO(self.modelPath)
        if camera_id == 1:
            self.roi_points = np.array([[430, 250], [900, 400], [270, 700], [280, 450]], np.int32)
        else:  # camera_id == 2
            self.roi_points = np.array([[330, 110], [430, 130], [520, 375], [110, 310]], np.int32)
        # Thêm các ngưỡng cho detection
        self.conf_threshold = 0.2# Ngưỡng confidence
        self.iou_threshold = 0.3 # Ngưỡng IoU cho NMS

    
    # def submit_info(self):
    #     self.start_time = self.start_time_edit.dateTime()
    #     self.end_time = self.end_time_edit.dateTime()
    #     self.number_people = self.number_people_edit.text()
    #     self.gap_time = self.gap_time_edit.Time()
    
    
    def point_in_roi(self, point):
        return cv2.pointPolygonTest(self.roi_points, point, False) >= 0

    def run(self) -> None:
        cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        
        if cap.isOpened():
            while self.__thread_active:
                if not self.__thread_pause:
                    ret, frame = cap.read()
                    if ret:
                       
                        resized_frame = cv2.resize(frame, (640, 640))
                        # Thực hiện detection với các ngưỡng đã thiết lập
                        results = self.model(resized_frame, conf=self.conf_threshold, iou=self.iou_threshold)
                        
                        # Lọc các boxes có confidence cao và đã qua NMS
                        filtered_boxes = []
                        for result in results:
                            boxes = result.boxes
                            for box in boxes:
                                # Lấy confidence score
                                conf = float(box.conf)
                                # Chỉ xử lý các box có confidence cao hơn ngưỡng
                                if conf > self.conf_threshold:
                                    x1, y1, x2, y2 = box.xyxy[0]
                                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                                    filtered_boxes.append({
                                        'box': (x1, y1, x2, y2),
                                        'conf': conf,
                                        'center': (int((x1 + x2) / 2), int((y1 + y2) / 2))
                                    })

                        # Cập nhật số lượng người (sau khi đã lọc)
                        person_count = len(filtered_boxes)
                        self.total_count += person_count
                        self.CountUpdated.emit(person_count)
                        self.TotalCountUpdated.emit(self.total_count)
                        
                        roi_count = 0
                        
                        # Vẽ các boxes đã được lọc
                        for box_info in filtered_boxes:
                            x1, y1, x2, y2 = box_info['box']
                            center_x, center_y = box_info['center']
                            conf = box_info['conf']
                            
                            if self.point_in_roi((center_x, center_y)):
                                roi_count += 1
                            
                            # Vẽ bounding box
                            cv2.rectangle(resized_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            # Vẽ điểm trung tâm
                            cv2.circle(resized_frame, (center_x, center_y), 5, (0, 0, 255), -1)
                            # Hiển thị confidence score
                            cv2.putText(resized_frame, f'{conf:.2f}', (x1, y1-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Vẽ ROI
                        cv2.polylines(resized_frame, [self.roi_points], True, (0, 0, 0), 1)
                        
                        # Emit count cho ROI
                        self.RoiCountUpdated.emit(roi_count)

                        height, width, channels = resized_frame.shape
                        bytes_per_line = width * channels
                        cv_rgb_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                        qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                        qt_rgb_image_scaled = qt_rgb_image.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
                        self.ImageUpdated.emit(qt_rgb_image_scaled)
                    else:
                        break
        cap.release()
        self.quit()

class CameraController:
    def __init__(self, window):
        self.window = window
        self.count_timer = None
        self.timer_start = None
        self.timer_end = None
        self.target_count = None
        self.total_count = 0
        self.setup_datetime_timer()
        
    def setup_datetime_timer(self):
        # Tạo timer để cập nhật datetime
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Cập nhật mỗi 1000ms (1 giây)
    
    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.window.date_time_label.setText(f"Time: {now.toString('dd/MM/yyyy hh:mm:ss')}")
        
    def handle_submit_info(self, timer_widget):
        # Lấy giá trị từ các ô input
        start_time = timer_widget.start_time_edit.dateTime()
        end_time = timer_widget.end_time_edit.dateTime()
        gap_time = timer_widget.gap_time_edit.time()
        target_count = timer_widget.number_people_edit.text()

        # Kiểm tra dữ liệu đầu vào
        if not target_count:
            timer_widget.result_text.setText("Vui lòng nhập số người mong muốn")
            return

        if start_time >= end_time:
            timer_widget.result_text.setText("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc")
            return

        # Chuyển đổi gap_time sang giây
        gap_seconds = gap_time.hour() * 3600 + gap_time.minute() * 60 + gap_time.second()
        
        # Xóa kết quả cũ
        timer_widget.result_text.clear()
        #Đổi tên nut submit
        timer_widget.submit_button.setText("Reset")
        # Dừng timer cũ nếu đang chạy
        if self.count_timer and self.count_timer.isActive():
            self.count_timer.stop()
        
        # Tạo và khởi động bộ đếm thời gian mới
        self.count_timer = QTimer()
        self.count_timer.timeout.connect(lambda: self.check_count(timer_widget))
        
        # Lưu các tham số
        self.timer_start = start_time
        self.timer_end = end_time
        self.target_count = int(target_count)
        self.timer_widget = timer_widget
        
        # Khởi động timer với khoảng thời gian đã chỉ định
        self.count_timer.start(gap_seconds * 1000)
        self.log_data=[]

    def check_count(self, timer_widget, now=None):
        current_time = QDateTime.currentDateTime()
        
        # Kiểm tra xem có còn trong khoảng thời gian giám sát không
        if current_time < self.timer_start:
            return
        if current_time > self.timer_end:
            self.count_timer.stop()
            return
        
        # Lấy số lượng người hiện tại trong ROI của Camera 2
        roi_count = int(self.window.roi_count_label_2.text().split(": ")[1].split()[0])
        
        # Định dạng và thêm kết quả
        time_str = current_time.toString("dd/MM/yyyy hh:mm:ss")
        time_data=current_time.toString("hh:mm:ss")
        result_str = f"Thời gian: {time_str} - Số người: {roi_count}\n"
        total_count = self.total_count
        # Lưu dữ liệu với thời gian hiện tại thay vì None
        self.log_data.append([time_data, roi_count, total_count])
        
        # Thêm cảnh báo nếu số người vượt quá giới hạn
        if roi_count < self.target_count:
            result_str += f"⚠️ khong du số người cho phép ({self.target_count})!\n"
        
        # Chèn vào đầu ô văn bản
        current_text = timer_widget.result_text.toPlainText()
        timer_widget.result_text.setText(result_str + current_text)

    def handle_delete_info(self, timer_widget):
        # Dừng timer nếu đang chạy
        if self.count_timer and self.count_timer.isActive():
            self.count_timer.stop()
        
        # Xóa tất cả các ô input
        timer_widget.start_time_edit.setDateTime(QDateTime.currentDateTime())
        timer_widget.end_time_edit.setDateTime(QDateTime.currentDateTime().addSecs(300))
        timer_widget.gap_time_edit.setTime(QTime(0, 0, 5))
        timer_widget.number_people_edit.clear()
        timer_widget.result_text.clear()
        timer_widget.submit_button.setText("xác nhận")
        self.log_data=[]    
   
    def cleanup(self):
        if self.datetime_timer.isActive():
            self.datetime_timer.stop()
        if self.count_timer and self.count_timer.isActive():
            self.count_timer.stop()
    
    def browse_file(self, timer_widget):
        """Mở hộp thoại chọn thư mục"""
        folder_path = QFileDialog.getExistingDirectory(timer_widget, "Chọn thư mục")
        if folder_path:
            timer_widget.save_path_edit.setText(folder_path)
    
    def save_csv(self, timer_widget):
        """Lưu dữ liệu vào file CSV"""
        save_path = timer_widget.save_path_edit.text()
        save_data = self.log_data
        
        if not timer_widget.result_text.toPlainText():
            timer_widget.result_text.setText("không có dữ liệu nào")
            return
        if not save_path:
            timer_widget.result_text.setText("không có đường dẫn lưu")
            return
        if not os.path.exists(save_path):
            timer_widget.result_text.setText(" ❌ Đường dẫn không tồn tại")
            return
        
        file_name = os.path.join(save_path, QDateTime.currentDateTime().toString("yyyy-MM-dd") + ".csv")
        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "People in area", "Total number"])
            for data in save_data:
                if all(item is not None for item in data):  # Kiểm tra không có giá trị None
                    writer.writerow([str(item) for item in data])  # Chuyển tất cả thành string
        
        self.log_data = []  # Reset log data sau khi lưu
        timer_widget.result_text.setText(" ✅ Lưu file thành công")
    
    def handle_double_click(self, source: QObject) -> bool:
        if source.objectName() == 'Camera_1':
            if self.window.list_of_cameras_state["Camera_1"] == "Normal":
                self.window.QScrollArea_2.hide()
                self.window.list_of_cameras_state["Camera_1"] = "Maximized"
                self.window.count_label_1.show()
                self.window.count_label_2.hide()
                self.window.roi_count_label_1.show()
                self.window.roi_count_label_2.hide()
                self.window.timer_widget.hide()
            else:
                self.window.QScrollArea_2.show()
                self.window.list_of_cameras_state["Camera_1"] = "Normal"
                self.window.count_label_1.show()
                self.window.count_label_2.show()
                self.window.roi_count_label_1.show()
                self.window.roi_count_label_2.show()
                self.window.timer_widget.hide()
            return True
            
        elif source.objectName() == 'Camera_2':
            if self.window.list_of_cameras_state["Camera_2"] == "Normal":
                self.window.QScrollArea_1.hide()
                self.window.list_of_cameras_state["Camera_2"] = "Maximized"
                self.window.count_label_2.show()
                self.window.count_label_1.hide()
                self.window.roi_count_label_2.show()
                self.window.roi_count_label_1.hide()
                # self.window.timer_widget.show()
            else:
                self.window.QScrollArea_1.show()
                self.window.list_of_cameras_state["Camera_2"] = "Normal"
                self.window.count_label_2.show()
                self.window.count_label_1.show()
                self.window.roi_count_label_2.show()
                self.window.roi_count_label_1.show()
                self.window.timer_widget.hide()
            return True
            
        return False

    def update_total_count(self, count):
        """Cập nhật tổng số người đã phát hiện"""
        self.total_count = count

class CameraWorkerManager:
    def __init__(self, url_1, url_2):
        self.url_1 = url_1
        self.url_2 = url_2
        self.worker_1 = None
        self.worker_2 = None

    def setup_workers(self, ui_callbacks):
        """
        Khởi tạo và cấu hình camera workers
        ui_callbacks: dict chứa các callback functions từ UI
        """
        # Setup worker cho camera 1
        self.worker_1 = CaptureIpCameraFramesWorker(self.url_1, camera_id=1)
        self.worker_1.ImageUpdated.connect(ui_callbacks['show_camera1'])
        self.worker_1.CountUpdated.connect(ui_callbacks['update_count1'])
        self.worker_1.RoiCountUpdated.connect(ui_callbacks['update_roi_count'])
        # self.worker_1.TotalCountUpdated.connect(ui_callbacks['update_total_count'])

        # Setup worker cho camera 2
        self.worker_2 = CaptureIpCameraFramesWorker(self.url_2, camera_id=2)
        self.worker_2.ImageUpdated.connect(ui_callbacks['show_camera2'])
        self.worker_2.CountUpdated.connect(ui_callbacks['update_count2'])
        self.worker_2.RoiCountUpdated.connect(ui_callbacks['update_roi_count'])
        self.worker_2.TotalCountUpdated.connect(ui_callbacks['update_total_count'])

        # Khởi động threads
        self.worker_1.start()
        self.worker_2.start()

    def stop_workers(self):
        """Dừng các camera workers"""
        if self.worker_1:
            self.worker_1.quit()
        if self.worker_2:
            self.worker_2.quit()


