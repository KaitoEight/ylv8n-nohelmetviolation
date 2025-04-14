from ultralytics import YOLO # type: ignore

# Load mô hình YOLOv8 Nano
model = YOLO('yolov8n.pt')

# Huấn luyện mô hình
model.train(
    data='dataset.yaml',  # Đường dẫn đến file YAML
    epochs=20,            # 20 epochs để có kết quả tốt hơn
    imgsz=640,            # Kích thước ảnh
    batch=16               # Batch size nhỏ để test trên CPU
)

#chup man hinh luu bien so xe + link image -> lam sao lay duoc bien so xe? : ocr 
#triger 