import cv2
from ultralytics import YOLO

# Load mô hình đã huấn luyện
model = YOLO('runs/detect/train4/weights/best.pt')

# Mở file video
video_path = 'videohd.mp4'  # Thay bằng đường dẫn tới file video của bạn
cap = cv2.VideoCapture(video_path)

# Kiểm tra xem video có mở được không
if not cap.isOpened():
    print("Không thể mở file video. Kiểm tra đường dẫn!")
    exit()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Đã hết video hoặc lỗi đọc frame.")
        break

    # Phát hiện đối tượng với ngưỡng conf
    results = model(frame, conf=0.3)  # Ngưỡng conf=0.6 như bạn đã chọn

    riders = []
    with_helmets = []
    without_helmets = []
    pedestrians = []

    # Phân loại đối tượng
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = box.conf[0]
            cls = box.cls[0]
            label = f"{model.names[int(cls)]} {conf:.2f}"

            if cls == 2:  # Rider
                riders.append((x1, y1, x2, y2))
                color = (255, 255, 0)  # Vàng
            elif cls == 0:  # With Helmet
                with_helmets.append((x1, y1, x2, y2))
                color = (0, 255, 0)  # Xanh
            elif cls == 1:  # Without Helmet
                without_helmets.append((x1, y1, x2, y2))
                color = (0, 0, 255)  # Đỏ
            elif cls == 4:  # Pedestrian
                pedestrians.append((x1, y1, x2, y2))
                color = (255, 0, 255)  # Tím
            else:  # Number Plate
                color = (255, 0, 0)  # Xanh dương

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Logic phát hiện vi phạm
    for rider in riders:
        rx1, ry1, rx2, ry2 = rider
        has_helmet = False
        for wh in with_helmets:
            wx1, wy1, wx2, wy2 = wh
            if wx1 >= rx1 and wx2 <= rx2 and wy1 >= ry1 and wy2 <= ry2:
                has_helmet = True
                break
        
        if not has_helmet:
            for woh in without_helmets:
                wx1, wy1, wx2, wy2 = woh
                if wx1 >= rx1 and wx2 <= rx2 and wy1 >= ry1 and wy2 <= ry2:
                    cv2.putText(frame, "VI PHAM!", (int(rx1), int(ry1) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    break
        else:
            cv2.putText(frame, "HOP LE", (int(rx1), int(ry1) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Người đi bộ luôn hợp lệ
    for ped in pedestrians:
        px1, py1, px2, py2 = ped
        cv2.putText(frame, "HOP LE", (int(px1), int(py1) - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Hiển thị frame
    cv2.imshow('Video Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Nhấn 'q' để thoát
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()