from PyQt6.QtCore import QThread, pyqtSignal, Qt, QObject, QEvent, QTimer, QDateTime, QTime, QMutex
from PyQt6.QtGui import QImage, QPixmap
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
from datetime import datetime
import asyncio
import telegram
from views.tele_page import TelegramSettingsGUI
from views.Roi_page import ROIDialog
import json

class CaptureIpCameraFramesWorker(QThread):
    ImageUpdated = pyqtSignal(QImage)   
    CountUpdated = pyqtSignal(int)
    RoiCountUpdated = pyqtSignal(int)
    TotalCountUpdated = pyqtSignal(int)

    def __init__(self, url,main_window) -> None:
        super(CaptureIpCameraFramesWorker, self).__init__()
        self.url = url
        self.__thread_active = True
        self.fps = 0
        self.modelPath = r'C:\Intern\PeopleDetected_ThienPhuocCompany\assets\model\bestyolo5.pt'
        self.model = YOLO(self.modelPath)
        self.camera_worker= CameraWorkerManager
        self._pause=False
        self._mutex= QMutex()
        self.roi_mutex = QMutex()  # Thêm mutex mới cho roi_points
        self.current_frame = None  # Thêm thuộc tính để lưu frame hiện tại # Thêm thuộc tính để lưu ROI points
        # self.roi_dialog = ROIDialog
        # if camera_id == 2: 
        # camera_id == 2
        self.roi_points = np.array([[0, 0], [0, 480], [640, 480], [640, 0]], dtype=np.int32)
        # Thêm các ngưỡng cho detection
        self.conf_threshold = 0.2# Ngưỡng confidence
        self.iou_threshold = 0.3 # Ngưỡng IoU cho NMS
        self.camera_controller= CameraController(main_window)
        self.run_model= False
        # self.model_thread= None
    def get_roi_points(self):
        self.roi_mutex.lock()
        points = self.roi_points.copy() if self.roi_points is not None else None
        self.roi_mutex.unlock()
        return points

    def set_roi_points(self, points):
        self.roi_mutex.lock()
        self.roi_points = points
        self.roi_mutex.unlock()

    def point_in_roi(self, point):
        roi_points = self.get_roi_points()
        if roi_points is not None and len(roi_points) > 0:
            return cv2.pointPolygonTest(roi_points, point, False) >= 0
        return False

    
    def open_roi_dialog(self):
        # Lấy frame hiện tại từ camera thông qua camera_controller
        frame = self.camera_controller.get_current_frame()
        if frame is not None:
            # Chuyển frame thành QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Lưu frame tạm thời
            temp_path = "temp_frame.png"
            q_image.save(temp_path, "PNG")
            
            # Mở dialog ROI với main_window làm parent
            roi_dialog = ROIDialog(temp_path, self.camera_controller.main_window)
            result = roi_dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                # Nếu người dùng nhấn "Cập nhật ROI"
                roi_coords = roi_dialog.get_roi_coordinates()
                new_roi_points = np.array(roi_coords, dtype=np.int32)
                self.set_roi_points(new_roi_points)  # Sử dụng method mới để cập nhật ROI
                # print("roi camera controll", self.get_roi_points())  # Sử dụng method mới để đọc ROI
            
            # Xóa file tạm
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return self.get_roi_points()  # Sử dụng method mới để trả về ROI
    # def update_roi(self):
    #     print("roi point hàm update",self.roi_points)
    #     return self.roi_points
    
    def run(self) -> None:
        cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        
        if cap.isOpened():
            while self.__thread_active:
                self._mutex.lock()
                paused = self._pause
                self._mutex.unlock()
            
                if not paused:
                    ret, frame = cap.read()
                    if ret:
                       
                        resized_frame = cv2.resize(frame, (640, 640))
                        if not self.run_model:
                            # Thực hiện detection với các ngưỡng đã thiết lập
                            results = self.model(resized_frame, conf=self.conf_threshold, iou=self.iou_threshold,verbose=False)
                            
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
                            
                            self.CountUpdated.emit(person_count)
                            # self.TotalCountUpdated.emit(self.total_count)
                            
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

                            # Vẽ ROI với mutex protection
                            current_roi = self.get_roi_points()  # Sử dụng method mới để đọc ROI
                            # print("roi_points trong run:", current_roi)
                            if current_roi is not None and len(current_roi) > 0:
                                cv2.polylines(resized_frame, [current_roi], True, (255, 253, 0), 2)
                            
                            # Emit count cho ROI
                            self.RoiCountUpdated.emit(roi_count)

                            height, width, channels = resized_frame.shape
                            bytes_per_line = width * channels
                            cv_rgb_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                            qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                            qt_rgb_image_scaled = qt_rgb_image.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
                            self.ImageUpdated.emit(qt_rgb_image_scaled)

                            # Lưu frame hiện tại
                            self.current_frame = resized_frame.copy()
                        else:
                            break
        cap.release()
        self.quit()

class CameraController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.count_timer = None
        self.timer_start = None 
        self.timer_end = None
        self.target_count = None
        self.total_count = 0
        self.current_period_count = 0  # Thêm biến đếm cho period hiện tại
        self.log_data = []
        self.tele_gui= TelegramSettingsGUI()
        self.setup_datetime_timer() 
        self.bot = None
        self.BOT_TOKEN= None
        self.CHAT_ID= None
        self.chat_id= None
        self.current_frames = {}  # Lưu trữ frame hiện tại cho mỗi camera

    
    def run_bot(self):
        """Lưu Token & Chat ID khi nhấn xác nhận và cập nhật ngay lập tức"""
        self.BOT_TOKEN = str(self.tele_gui.input_token.text())
        self.CHAT_ID = str(self.tele_gui.input_chat_id.text())
    
        print("khởi tạo bot thành công")
        # Cập nhật ngay lập tức mà không cần restart app
        self.bot = telegram.Bot(self.BOT_TOKEN)  # Cập nhật bot mới
        self.chat_id = self.CHAT_ID  # Cập nhật Chat ID mới
        if not self.BOT_TOKEN:
            print("Không có token")
        else:
            print(f"TOken:{self.BOT_TOKEN}\nchat_id:{str(self.tele_gui.input_chat_id.text())}")
    
    def write(self, message):
        """Gửi tin nhắn Telegram"""
        if message.strip():  # Bỏ qua dòng trống
            asyncio.run(self.send_message(message.strip()))
    
    def flush(self):
        """Flush không làm gì cả, nhưng cần có để tương thích với sys.stdout"""
        pass
    
    def setup_datetime_timer(self):
        # Tạo timer để cập nhật datetime
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Cập nhật mỗi 1000ms (1 giây)
    
    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.main_window.date_time_label.setText(f"Time: {now.toString('dd/MM/yyyy hh:mm:ss')}")
        
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

        if end_time <= QDateTime.currentDateTime():
            timer_widget.result_text.setText("Thời gian kết thúc phải lớn hơn thời gian hiện tại")
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
        self.log_data = []
        
        # Reset current_period_count khi bắt đầu period mới
        self.current_period_count = 0
        self.run_bot()
    def check_count(self, timer_widget):
        current_time = QDateTime.currentDateTime()
        
        # Kiểm tra xem có còn trong khoảng thời gian giám sát không
        if current_time < self.timer_start:
            return
        if current_time > self.timer_end:
            self.count_timer.stop()
            timer_widget.result_text.setText("Đã hết thời gian đếm")
            end_time_message = "Đã hết thời gian đếm"
            asyncio.run(self.send_tele(end_time_message))
            return
        
        # Lấy số lượng người hiện tại trong ROI của Camera 2
        roi_count = int(self.main_window.roi_count_label_2.text().split(": ")[1].split()[0])
        total_count= int(self.main_window.count_label_2.text().split(": ")[1].split()[0])
        # Cập nhật total_count cho period hiện tại
        self.current_period_count = total_count
        
        # Định dạng và thêm kết quả
        time_str = current_time.toString("dd/MM/yyyy hh:mm:ss")
        time_data = current_time.toString("hh:mm:ss")
        result_str = f"Thời gian: {time_str} - Số người: {roi_count}\n"
        
        # Lưu dữ liệu với thời gian hiện tại và current_period_count
        self.log_data.append([time_data, roi_count, self.current_period_count])
        
        # Thêm cảnh báo nếu số người không đủ
        if roi_count < self.target_count:
            result_str += f"⚠️ không đủ số người cho phép ({self.target_count})!\n"
            # Gọi phương thức gửi tin nhắn khi không đủ người
            formatted_message = f"{result_str}"
            asyncio.run(self.send_tele(formatted_message))
        else:
            formatted_message_ok = f"{result_str}"
            asyncio.run(self.send_tele(formatted_message_ok))
        # Chèn vào đầu ô văn bản
        current_text = timer_widget.result_text.toPlainText()
        timer_widget.result_text.setText(result_str + current_text)

    # def send_tele(self,message):
    #     asyncio.run(self.send_telegram_async(message))
    async def send_tele(self,message):
        try:
            async with self.bot:
                await self.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn Telegram: {e}")
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
        self.log_data = []
        
        # Reset current_period_count
        self.current_period_count = 0

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
        
        # Kiểm tra điều kiện đầu vào
        if not save_path:
            timer_widget.result_text.setText("không có đường dẫn lưu")
            return
        if not os.path.exists(save_path):
            timer_widget.result_text.setText(" ❌ Đường dẫn không tồn tại")
            return
        if not self.log_data:
            timer_widget.result_text.setText("không có dữ liệu nào")
            return

        # Tạo tên file với định dạng ngày tháng
        file_name = QDateTime.currentDateTime().toString("yyyy-MM-dd") + ".csv"
        file_path = os.path.join(save_path, file_name)

        # Kiểm tra file tồn tại và xác nhận ghi đè
        if os.path.exists(file_path):
            result = timer_widget.msg_box.exec()
            if result != QMessageBox.StandardButton.Ok:
                return

        # Hàm helper để ghi file CSV
        def write_csv_file():
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Time", "People in area", "Total number"])
                for data in self.log_data:
                    if all(item is not None for item in data):
                        writer.writerow([str(item) for item in data])

        try:
            write_csv_file()
            # Reset dữ liệu và UI sau khi lưu thành công
            self.log_data = []
            self.handle_delete_info(timer_widget)
            timer_widget.result_text.setText(" ✅ Lưu file thành công")
        except Exception as e:
            timer_widget.result_text.setText(f" ❌ Lỗi khi lưu file: {str(e)}")

    def handle_double_click(self, source: QObject) -> bool:    
        if source.objectName() == 'Camera_2':
            if self.main_window.list_of_cameras_state["Camera_2"] == "Normal":
                self.main_window.list_of_cameras_state["Camera_2"] = "Maximized"
                self.main_window.count_label_2.show()
                self.main_window.roi_count_label_2.show()
                # self.window.timer_widget.show()
            else:
                self.main_window.list_of_cameras_state["Camera_2"] = "Normal"
                self.main_window.count_label_2.show()
                self.main_window.roi_count_label_2.show()
                self.main_window.timer_widget.hide()
            return True
            
        return False

    def update_total_count(self, count):
        """Cập nhật tổng số người đã phát hiện"""
        self.total_count = count

    def get_current_frame(self):
        """Lấy frame hiện tại của camera"""
        # if camera_id == 1:
        #     return self.main_window.CaptureIpCameraFramesWorker_1.current_frame
        return self.main_window.CaptureIpCameraFramesWorker_2.current_frame

    def update_frame_with_roi(self, q_image):
        """Cập nhật frame với ROI mới"""
        # if camera_id == 1:
        #     self.main_window.camera_1.setPixmap(QPixmap.fromImage(q_image))
        self.main_window.camera_2.setPixmap(QPixmap.fromImage(q_image))

class CameraWorkerManager:
    def __init__(self, url_2):
        self.url_2 = url_2
        self.worker_2 = None

    def setup_workers(self, ui_callbacks):
        """
        Khởi tạo và cấu hình camera workers
        ui_callbacks: dict chứa các callback functions từ UI
        """

        # Setup worker cho camera 2
        self.worker_2 = CaptureIpCameraFramesWorker(self.url_2, camera_id=2)
        self.worker_2.ImageUpdated.connect(ui_callbacks['show_camera2'])
        self.worker_2.CountUpdated.connect(ui_callbacks['update_count2'])
        self.worker_2.RoiCountUpdated.connect(ui_callbacks['update_roi_count'])
        self.worker_2.TotalCountUpdated.connect(ui_callbacks['update_total_count'])

        self.worker_2.start()

    def stop_workers(self):
        #Dừng các camera workers
        if self.worker_2:
            self.worker_2.quit()
 

