# This would go in your ROI_page.py file
import cv2
import numpy as np
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QWidget, QGridLayout,QGroupBox)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QIntValidator
from PyQt6.QtCore import Qt, QPoint

class ROIDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super(ROIDialog, self).__init__(parent)
        self.setWindowTitle("Chỉnh Vùng ROI")
        self.setMinimumSize(900, 700)
        
        # Tải ảnh đã chụp
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            print(f"Lỗi: Không thể tải ảnh từ {image_path}")
            return
            
        # Lấy kích thước thật của ảnh
        self.image_height, self.image_width = self.original_image.shape[:2]
        
        # Khởi tạo các điểm ROI - mặc định ở góc của hình chữ nhật ở trung tâm
        center_x, center_y = self.image_width // 2, self.image_height // 2
        offset_x, offset_y = self.image_width // 4, self.image_height // 4
        
        self.roi_points = [
            QPoint(center_x - offset_x, center_y - offset_y),  # trên-trái
            QPoint(center_x + offset_x, center_y - offset_y),  # trên-phải
            QPoint(center_x + offset_x, center_y + offset_y),  # dưới-phải
            QPoint(center_x - offset_x, center_y + offset_y)   # dưới-trái
        ]
        
        # Biến theo dõi điểm được chọn và kích thước điểm
        self.selected_point = None
        self.point_radius = 8
        
        # Tạo QImage với ROI
        self.q_image = self.update_image_with_roi()
        
        # Tạo layout
        main_layout = QVBoxLayout()
        
        # Widget hiển thị ảnh - chiếm phần lớn không gian
        image_widget = QWidget()
        image_layout = QVBoxLayout()
        
        # Label hiển thị ảnh
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setPixmap(QPixmap.fromImage(self.q_image))
        self.image_label.setScaledContents(True)
        
        # Bật theo dõi chuột
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        
        # Thêm ảnh vào layout với tỷ lệ co giãn lớn
        image_layout.addWidget(self.image_label)
        image_widget.setLayout(image_layout)
        main_layout.addWidget(image_widget, stretch=4)  # Chiếm 80% không gian
        
        # Widget chứa các ô nhập tọa độ - ở dưới ảnh
        coord_widget = QWidget()
        coord_layout = QHBoxLayout()
        
        # Tạo 4 ô nhập liệu cho 4 điểm
        self.point_inputs = []
        labels = ["Điểm 1 (Trên-Trái)", "Điểm 2 (Trên-Phải)", 
                 "Điểm 3 (Dưới-Phải)", "Điểm 4 (Dưới-Trái)"]
        
        for i in range(4):
            point_group = QGroupBox(labels[i])
            point_layout = QVBoxLayout()
            
            # Tạo một ô nhập liệu hiển thị cả X và Y
            coord_input = QLineEdit()
            coord_input.setText(f"{self.roi_points[i].x()}, {self.roi_points[i].y()}")
            
            # Kết nối tín hiệu
            coord_input.textChanged.connect(lambda text, idx=i: self.update_point_from_text(idx, text))
            
            # Lưu trữ tham chiếu
            self.point_inputs.append(coord_input)
            
            # Thêm vào layout
            point_layout.addWidget(coord_input)
            point_group.setLayout(point_layout)
            coord_layout.addWidget(point_group)
        
        coord_widget.setLayout(coord_layout)
        main_layout.addWidget(coord_widget, stretch=1)  # Chiếm 20% không gian
        
        # Buttons
        button_layout = QHBoxLayout()
        
        update_button = QPushButton("Cập Nhật ROI")
        update_button.clicked.connect(self.update_roi)
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(update_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Áp dụng stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #424242;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                color: white;
                background-color: #555;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QGroupBox {
                color: white;
                font-size: 14px;
                border: 1px solid #666;
                border-radius: 4px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 8px 24px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
    
    def update_image_with_roi(self):
        # Tạo một bản sao của ảnh để vẽ ROI
        roi_image = self.original_image.copy()
        
        # Vẽ đa giác ROI
        points = np.array([[p.x(), p.y()] for p in self.roi_points], np.int32)
        points = points.reshape((-1, 1, 2))
        cv2.polylines(roi_image, [points], True, (0, 255, 0), 2)
        
        # Vẽ các điểm góc
        for i, point in enumerate(self.roi_points):
            color = (255, 0, 0) if i == self.selected_point else (0, 0, 255)
            cv2.circle(roi_image, (point.x(), point.y()), self.point_radius, color, -1)
            # Thêm nhãn cho mỗi điểm
            cv2.putText(roi_image, str(i+1), (point.x() - 5, point.y() - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Chuyển sang RGB cho Qt
        rgb_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2RGB)
        
        # Chuyển thành QImage
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        return q_image
    
    def mouse_press_event(self, event):
        # Chuyển đổi vị trí chuột tương đối
        pos = event.position()
        
        # Tính tỷ lệ co giãn
        label_size = self.image_label.size()
        scale_x = self.image_width / label_size.width()
        scale_y = self.image_height / label_size.height()
        
        # Vị trí thực tế trên ảnh
        real_x = int(pos.x() * scale_x)
        real_y = int(pos.y() * scale_y)
        
        # Kiểm tra xem nhấp chuột có gần điểm nào không
        for i, point in enumerate(self.roi_points):
            dx = real_x - point.x()
            dy = real_y - point.y()
            if dx*dx + dy*dy < self.point_radius*self.point_radius:
                self.selected_point = i
                break
    
    def mouse_release_event(self, event):
        self.selected_point = None
    
    def mouse_move_event(self, event):
        if self.selected_point is not None:
            # Chuyển đổi vị trí chuột
            pos = event.position()
            
            # Tính tỷ lệ co giãn
            label_size = self.image_label.size()
            scale_x = self.image_width / label_size.width() 
            scale_y = self.image_height / label_size.height()
            
            # Vị trí thực tế trên ảnh
            real_x = int(pos.x() * scale_x)
            real_y = int(pos.y() * scale_y)
            
            # Giới hạn trong kích thước ảnh
            real_x = max(0, min(real_x, self.image_width - 1))
            real_y = max(0, min(real_y, self.image_height - 1))
            
            # Cập nhật điểm được chọn
            self.roi_points[self.selected_point] = QPoint(real_x, real_y)
            
            # Cập nhật ô nhập liệu
            self.point_inputs[self.selected_point].setText(f"{real_x}, {real_y}")
            
            # Cập nhật ảnh
            self.q_image = self.update_image_with_roi()
            self.image_label.setPixmap(QPixmap.fromImage(self.q_image))
    
    def update_point_from_text(self, point_idx, text):
        # Cập nhật điểm từ ô nhập liệu
        try:
            # Tách giá trị x, y từ chuỗi "x, y"
            coords = text.split(',')
            if len(coords) == 2:
                x = int(coords[0].strip())
                y = int(coords[1].strip())
                
                # Giới hạn trong kích thước ảnh
                x = max(0, min(x, self.image_width - 1))
                y = max(0, min(y, self.image_height - 1))
                
                # Cập nhật điểm
                self.roi_points[point_idx] = QPoint(x, y)
                
                # Cập nhật ảnh
                self.q_image = self.update_image_with_roi()
                self.image_label.setPixmap(QPixmap.fromImage(self.q_image))
        except ValueError:
            # Bỏ qua nếu định dạng không hợp lệ
            pass
    
    def update_roi(self):
        # Chuyển đổi roi_points từ numpy.ndarray sang danh sách QPoint nếu cần
        if isinstance(self.roi_points, np.ndarray):
            if len(self.roi_points.shape) == 2:  # Mảng 2D (4x2)
                temp_points = [QPoint(int(point[0]), int(point[1])) for point in self.roi_points]
            elif len(self.roi_points.shape) == 3:  # Mảng 3D (4x1x2)
                temp_points = [QPoint(int(point[0][0]), int(point[0][1])) for point in self.roi_points]
            self.roi_points = temp_points
            
        # Bây giờ self.roi_points là danh sách QPoint, có thể sử dụng .x() và .y()
        roi_coordinates = [(p.x(), p.y()) for p in self.roi_points]
        print("Đã cập nhật tọa độ ROI:", roi_coordinates)
        self.accept()
    
    def get_roi_coordinates(self):
        return [(p.x(), p.y()) for p in self.roi_points]

class MainApp:
    def __init__(self):
        # Khởi tạo các thành phần khác của ứng dụng
        self.current_roi = None  # Lưu tọa độ ROI hiện tại

    def captureFrame(self):
        # This method will be called from your ControlPanel class
        # It captures the current frame and saves it to disk
        print("Capturing frame for ROI adjustment")
        
        # Access the current frame
        frame = self.camera_page.camera.pixmap()
        
        if frame and not frame.isNull():
            # Convert QPixmap to QImage and save it
            frame.save("captured_frame.png", "PNG")
            print("Frame captured and saved as captured_frame.png")
        else:
            print("Error: Could not capture frame - no frame available")
    
    def openROIDialog(self,image_path):
        roi_dialog= ROIDialog(image_path, self)
        result= roi_dialog.exec()

        if result== QDialog.DialogCode.Accepted:
            self.current_roi= roi_dialog.get_roi_coordinates()
            print("Roi đã được cập nhật:", self.current_roi)

            self.applyROIToCurrentFrame()
    
    def applyROIToCurrentFrame(self):
        if not self.current_roi:
            print('No ROI')
            return
        
        current_frame= self.camera_page.camera.pixmap()
        if current_frame is None or current_frame.isNull():
            print("No Frame")
            return
        
        # Chuyển đổi QPixmap thành OpenCV image
        qimg = current_frame.toImage()
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.constBits()
        # Tạo một mảng numpy từ dữ liệu QImage
        img = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        
        # Tạo một bản sao để vẽ ROI
        img_with_roi = img.copy()
        
        # Vẽ ROI trên frame
        points = np.array(self.current_roi, np.int32)
        points = points.reshape((-1, 1, 2))
        cv2.polylines(img_with_roi, [points], True, (0, 255, 0), 2)
        
        # Chuyển đổi trở lại thành QPixmap để hiển thị
        bytes_per_line = img_with_roi.strides[0]
        qimg_with_roi = QImage(img_with_roi.data, width, height, bytes_per_line, QImage.Format.Format_ARGB32)
        pixmap_with_roi = QPixmap.fromImage(qimg_with_roi)
        
        # Cập nhật frame trong camera_page
        self.camera_page.camera.setPixmap(pixmap_with_roi)
        
        # Lưu thông tin ROI để xử lý tiếp (nếu cần)
        self.saveROISettings()
    
    # def saveROISettings(self):
    #     # Lưu cài đặt ROI để sử dụng trong quá trình xử lý hình ảnh sau này
    #     # Ví dụ: lưu vào file cấu hình hoặc cơ sở dữ liệu
    #     if self.current_roi:
    #         # Ví dụ lưu vào biến cấu hình
    #         self.config_settings.roi_coordinates = self.current_roi
            
    #         # Nếu bạn muốn lưu vào file:
    #         # import json
    #         # with open('roi_settings.json', 'w') as f:
    #         #    json.dump(self.current_roi, f)