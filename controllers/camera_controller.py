from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage
import cv2
from ultralytics import YOLO
import numpy as np

class CaptureIpCameraFramesWorker(QThread):
    ImageUpdated = pyqtSignal(QImage)
    CountUpdated = pyqtSignal(int)
    RoiCountUpdated = pyqtSignal(int)

    def __init__(self, url, camera_id) -> None:
        super(CaptureIpCameraFramesWorker, self).__init__()
        self.url = url
        self.camera_id = camera_id
        self.__thread_active = True
        self.fps = 0
        self.__thread_pause = False
        self.model = YOLO(r'C:\Intern\PeopleDetected_ThienPhuocCompany\assets\model\bestyolo5.pt')
        self.roi_points = np.array([[300, 110], [900, 250], [900, 500], [130, 220]], np.int32)
        # Thêm các ngưỡng cho detection
        self.conf_threshold = 0.1  # Ngưỡng confidence
        self.iou_threshold = 0.4  # Ngưỡng IoU cho NMS

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
                        # Thực hiện detection với các ngưỡng đã thiết lập
                        results = self.model(frame, conf=self.conf_threshold, iou=self.iou_threshold)
                        
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
                        
                        roi_count = 0
                        
                        # Vẽ các boxes đã được lọc
                        for box_info in filtered_boxes:
                            x1, y1, x2, y2 = box_info['box']
                            center_x, center_y = box_info['center']
                            conf = box_info['conf']
                            
                            if self.point_in_roi((center_x, center_y)):
                                roi_count += 1
                            
                            # Vẽ bounding box
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            # Vẽ điểm trung tâm
                            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                            # Hiển thị confidence score
                            cv2.putText(frame, f'{conf:.2f}', (x1, y1-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        if self.camera_id == 1:
                            cv2.polylines(frame, [self.roi_points], True, (255, 0, 0), 2)
                            self.RoiCountUpdated.emit(roi_count)

                        height, width, channels = frame.shape
                        bytes_per_line = width * channels
                        cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                        qt_rgb_image_scaled = qt_rgb_image.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
                        self.ImageUpdated.emit(qt_rgb_image_scaled)
                    else:
                        break
        cap.release()
        self.quit()

    def stop(self) -> None:
        self.__thread_active = False

    def pause(self) -> None:
        self.__thread_pause = True

    def unpause(self) -> None:
        self.__thread_pause = False
