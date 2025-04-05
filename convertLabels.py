import os
import xml.etree.ElementTree as ET

# Đường dẫn thư mục
xml_dir = "dataset/annotations"  # Thư mục chứa file XML
img_dir = "dataset/images"       # Thư mục chứa ảnh
output_dir = "dataset/labels"    # Thư mục để lưu file .txt
os.makedirs(output_dir, exist_ok=True)

# Danh sách class và ánh xạ sang ID (sửa lỗi chữ hoa/thường)
classes = ["With Helmet", "Without Helmet"]
class_to_id = {name.lower(): idx for idx, name in enumerate(classes)}

# Hàm chuyển đổi tọa độ
def convert_coordinates(size, box):
    dw = 1.0 / size[0]  # Chuẩn hóa theo chiều rộng
    dh = 1.0 / size[1]  # Chuẩn hóa theo chiều cao
    x = (box[0] + box[1]) / 2.0  # Tâm x
    y = (box[2] + box[3]) / 2.0  # Tâm y
    w = box[1] - box[0]          # Chiều rộng
    h = box[3] - box[2]          # Chiều cao
    return x * dw, y * dh, w * dw, h * dh

# Xử lý từng file XML
for xml_file in os.listdir(xml_dir):
    if not xml_file.endswith(".xml"):
        continue

    xml_path = os.path.join(xml_dir, xml_file)
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Kiểm tra kích thước ảnh
        size = root.find("size")
        if size is None:
            print(f"[⚠] Bỏ qua {xml_file} (thiếu thẻ <size>)")
            continue

        img_width = int(size.find("width").text)
        img_height = int(size.find("height").text)

        # Tạo file .txt tương ứng
        txt_file = os.path.join(output_dir, xml_file.replace(".xml", ".txt"))
        with open(txt_file, "w") as f:
            found_object = False  # Kiểm tra xem có object nào không
            
            for obj in root.findall("object"):
                class_name = obj.find("name").text.strip().lower()
                if class_name not in class_to_id:
                    print(f"[⚠] Bỏ qua object '{class_name}' trong {xml_file} (không thuộc danh sách classes)")
                    continue
                
                class_id = class_to_id[class_name]

                # Lấy tọa độ bounding box
                bndbox = obj.find("bndbox")
                xmin = float(bndbox.find("xmin").text)
                xmax = float(bndbox.find("xmax").text)
                ymin = float(bndbox.find("ymin").text)
                ymax = float(bndbox.find("ymax").text)

                # Chuyển đổi sang định dạng YOLO
                x, y, w, h = convert_coordinates((img_width, img_height), (xmin, xmax, ymin, ymax))

                # Ghi vào file .txt
                f.write(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                found_object = True  # Có ít nhất một object hợp lệ
            
            if not found_object:
                print(f"[⚠] Bỏ qua {xml_file} (không có object hợp lệ)")

    except Exception as e:
        print(f"[❌] Lỗi khi xử lý {xml_file}: {e}")

print("✅ Chuyển đổi hoàn tất!")
