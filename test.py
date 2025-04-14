import cv2
import os
from datetime import datetime
from ultralytics import YOLO
import requests
import cloudinary
import cloudinary.uploader
import pandas as pd
from dotenv import load_dotenv
import threading
import queue

# Load biến môi trường từ .env
load_dotenv()

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET')
)

# Tải mô hình YOLO
model = YOLO('runs/detect/train4/weights/best.pt')

# Đường dẫn API và CSV
api_url = "http://127.0.0.1:5555/license_plate"  # Cập nhật sau khi chạy api.py
csv_path = 'violations.csv'

# Tạo thư mục lưu ảnh vi phạm
output_dir = 'violations'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Hàng đợi để lưu thông tin vi phạm
violation_queue = queue.Queue()

# Hàm kiểm tra giao nhau giữa hai hộp (IoU đơn giản)
def boxes_intersect(box1, box2):
    x1, y1, x2, y2 = box1
    wx1, wy1, wx2, wy2 = box2
    if (x2 < wx1 or wx2 < x1 or y2 < wy1 or wy2 < y1):
        return False
    return True

# Hàm upload ảnh lên Cloudinary
def upload_to_cloudinary(image_path):
    try:
        response = cloudinary.uploader.upload(image_path)
        return response['secure_url']
    except Exception as e:
        print(f"Cloudinary Upload Error: {e}")
        return None

# Hàm gửi URL qua API và nhận biển số xe
def send_image_to_api(image_url, api_url):
    payload = {"image_url": image_url}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            response_json = response.json()
            print(f"API Response: {response_json}")
            return response_json.get("license_plate", "unknown")
        else:
            print(f"Error calling API: {response.status_code} - {response.text}")
            return "unknown"
    except Exception as e:
        print(f"API Call Exception: {e}")
        return "unknown"

# Hàm ghi hoặc cập nhật CSV
def update_csv(timestamp, license_plate, image_path, csv_path):
    columns = ["Thời gian vi phạm", "Biển số xe", "Đường dẫn hình ảnh"]
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=columns)
    else:
        df = pd.read_csv(csv_path)
    
    if "Thời gian vi phạm" in df.columns and timestamp in df["Thời gian vi phạm"].values:
        df.loc[df["Thời gian vi phạm"] == timestamp, "Biển số xe"] = license_plate
        df.loc[df["Thời gian vi phạm"] == timestamp, "Đường dẫn hình ảnh"] = image_path
    else:
        new_row = {"Thời gian vi phạm": timestamp, "Biển số xe": license_plate, "Đường dẫn hình ảnh": image_path}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    df.to_csv(csv_path, index=False)

# Hàm xử lý vi phạm trong luồng riêng
def process_violation_worker():
    while True:
        try:
            # Lấy thông tin vi phạm từ hàng đợi
            timestamp, local_path = violation_queue.get()
            print(f"Đang xử lý vi phạm: {local_path}")

            # Upload lên Cloudinary
            cloudinary_url = upload_to_cloudinary(local_path)
            if cloudinary_url:
                print(f"Uploaded to Cloudinary: {cloudinary_url}")
                # Gọi API nhận diện biển số
                license_plate = send_image_to_api(cloudinary_url, api_url)
                # Cập nhật CSV
                update_csv(timestamp, license_plate, cloudinary_url, csv_path)
                print(f"Cập nhật CSV: Thời gian: {timestamp} - Biển số: {license_plate}")
            else:
                print(f"Upload Cloudinary thất bại cho {local_path}")

            # Đánh dấu nhiệm vụ hoàn thành
            violation_queue.task_done()

        except Exception as e:
            print(f"Error processing violation: {e}")

# Khởi động luồng xử lý vi phạm
threading.Thread(target=process_violation_worker, daemon=True).start()

# Mở webcam hoặc video
video_source = 'video.mp4'  # 0 cho webcam, hoặc 'path/to/video.mp4'
cap = cv2.VideoCapture(video_source)
if not cap.isOpened():
    print("Không thể mở webcam/video. Kiểm tra nguồn!")
    exit()

# Tối ưu độ phân giải
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Biến kiểm soát tần suất lưu vi phạm
last_violation_time = 0
min_interval = 5  # Giây

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không thể đọc frame. Thoát...")
        break

    # Phát hiện đối tượng với YOLO
    results = model(frame, conf=0.3)

    riders = []
    with_helmets = []
    without_helmets = []

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
                color = (255, 255, 0)
            elif cls == 0:  # With Helmet
                with_helmets.append((x1, y1, x2, y2))
                color = (0, 255, 0)
            elif cls == 1:  # Without Helmet
                without_helmets.append((x1, y1, x2, y2))
                color = (0, 0, 255)
            else:
                color = (255, 0, 0)

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Phát hiện vi phạm
    current_time = datetime.now().timestamp()
    violation_detected = False
    for rider in riders:
        rx1, ry1, rx2, ry2 = rider
        has_helmet = False
        for wh in with_helmets:
            if boxes_intersect(rider, wh):
                has_helmet = True
                break
        
        if not has_helmet:
            for woh in without_helmets:
                if boxes_intersect(rider, woh):
                    if current_time - last_violation_time >= min_interval:
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        local_path = os.path.join(output_dir, f'violation_{timestamp}.jpg')
                        cv2.imwrite(local_path, frame)
                        
                        # Ghi vào CSV ngay lập tức với biển số "unknown"
                        update_csv(timestamp, "unknown", local_path, csv_path)
                        print(f"Đã lưu ảnh vi phạm: {local_path}")

                        # Thêm vào hàng đợi để xử lý upload và API
                        violation_queue.put((timestamp, local_path))

                        last_violation_time = current_time
                        violation_detected = True
                    break
        
        if violation_detected:
            break

    # Hiển thị frame
    cv2.imshow('Realtime Detection', frame)
    
    # Thoát nếu nhấn 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()