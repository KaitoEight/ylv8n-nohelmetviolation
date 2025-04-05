import os
import shutil
from xml.etree import ElementTree as ET

def convert_pascal_to_yolo(annotation_dir, image_dir, output_dir):
    # Tạo thư mục đầu ra
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'labels'), exist_ok=True)

    # Class ID cho Pedestrian (giả sử là 4 trong danh sách của bạn)
    class_id = 4

    # Xử lý từng file annotation
    for ann_file in os.listdir(annotation_dir):
        if not ann_file.endswith('.txt'):
            continue

        with open(os.path.join(annotation_dir, ann_file), 'r') as f:
            lines = f.readlines()

        # Lấy kích thước ảnh
        for line in lines:
            if "Image size" in line:
                size = line.split(":")[1].strip().split(" x ")
                width, height = int(size[0]), int(size[1])
                break

        # Tạo file .txt cho YOLO
        txt_file = ann_file.replace('.txt', '.txt')
        img_file = ann_file.replace('.txt', '.png')
        yolo_lines = []

        # Đọc bounding box
        for line in lines:
            if "Bounding box" in line:
                coords = line.split(":")[1].strip().split(" - ")
                xmin, ymin = map(int, coords[0].strip('()').split(', '))
                xmax, ymax = map(int, coords[1].strip('()').split(', '))

                # Chuyển sang định dạng YOLO
                x_center = (xmin + xmax) / 2 / width
                y_center = (ymin + ymax) / 2 / height
                w = (xmax - xmin) / width
                h = (ymax - ymin) / height
                yolo_lines.append(f"{class_id} {x_center} {y_center} {w} {h}")

        # Ghi file .txt
        with open(os.path.join(output_dir, 'labels', txt_file), 'w') as f:
            f.write('\n'.join(yolo_lines))

        # Sao chép ảnh
        shutil.copy(os.path.join(image_dir, img_file), os.path.join(output_dir, 'images', img_file))

# Sử dụng hàm
annotation_dir = 'pedestrians/Annotation'
image_dir = 'pedestrians/PNGImages'
output_dir = 'pedestrians/pedestrian_data'
convert_pascal_to_yolo(annotation_dir, image_dir, output_dir)