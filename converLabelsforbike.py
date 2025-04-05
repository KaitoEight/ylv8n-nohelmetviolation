import os
import xml.etree.ElementTree as ET

# Đường dẫn đến thư mục chứa file XML và ảnh
xml_dir = 'dataset2/annotations'
img_dir = 'dataset2/images'
output_dir = 'dataset2/labels'

# Tạo thư mục output nếu chưa có
os.makedirs(output_dir, exist_ok=True)

# Danh sách class
classes = ['With Helmet', 'Without Helmet']

# Hàm chuyển đổi tọa độ
def convert_coordinates(size, box):
    dw = 1.0 / size[0]  # width
    dh = 1.0 / size[1]  # height
    x = (box[0] + box[1]) / 2.0  # x_center = (xmin + xmax) / 2
    y = (box[2] + box[3]) / 2.0  # y_center = (ymin + ymax) / 2
    w = box[1] - box[0]          # width = xmax - xmin
    h = box[3] - box[2]          # height = ymax - ymin
    x = x * dw  # Chuẩn hóa
    y = y * dh
    w = w * dw
    h = h * dh
    return (x, y, w, h)

# Xử lý từng file XML
for xml_file in os.listdir(xml_dir):
    if xml_file.endswith('.xml'):
        tree = ET.parse(os.path.join(xml_dir, xml_file))
        root = tree.getroot()
        
        # Lấy kích thước ảnh
        size = root.find('size')
        width = int(size.find('width').text)
        height = int(size.find('height').text)
        
        # Tạo file .txt tương ứng
        txt_file = os.path.join(output_dir, xml_file.replace('.xml', '.txt'))
        with open(txt_file, 'w') as f:
            for obj in root.findall('object'):
                cls_name = obj.find('name').text
                cls_id = classes.index(cls_name)  # 0 hoặc 1
                bndbox = obj.find('bndbox')
                box = [
                    float(bndbox.find('xmin').text),
                    float(bndbox.find('xmax').text),
                    float(bndbox.find('ymin').text),
                    float(bndbox.find('ymax').text)
                ]
                x, y, w, h = convert_coordinates((width, height), box)
                f.write(f"{cls_id} {x} {y} {w} {h}\n")

print("Chuyển đổi hoàn tất!")