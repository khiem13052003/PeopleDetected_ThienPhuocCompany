# PeopleDetected_ThienPhuocCompany

Nhận diện, phát hiện người, đếm số người trong 1 khoảng thời gian, 1 khu vực nhất định

Chúng tôi sử dụng mô hình yolov5 với dataset lấy trực tiếp từ frame của camera IP: 10.0.0.91, bao gồm gần 10k tấm hình với size là 640x640, epoch = 100.
Chương trình sử dụng Qt6 để thiết kế GUI.

Hướng dẫn sử dụng:
    Bước 1: Đảm bảo đang bắt mạng Device 
    Bước 2: Đăng nhập vào hệ thống với username : " hoatuoitt ", password là " Thienphuoc2025 "
    Bước 3: Điều chỉnh thời gian người dùng muốn bắt đầu và kết thúc bộ đếm, điều chỉnh khoảng thời gian giữa 2 lần đếm và số người mong muốn có trong khu vực
    Bước 4: Điều chỉnh ROI bằng cách kéo thả 4 nút hoặc chỉnh sửa trực tiếp trên ô nhập tọa độ
    Bước 5: Tạo và thay đổi số token của Bot và ID của người muốn gửi tin nhắn tới trên Telegram theo hướng dẫn có trong chương trình
    Bước 6: chạy chương trình và hệ thống sẽ báo số lượng người và sẽ cảnh báo nếu không có đủ người trong khu vực. 
    Bước 7: Lưu five csv.