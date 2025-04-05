import os
import random
import shutil

def split_dataset(image_dir, label_dir, output_dir, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    """
    Sắp xếp ngẫu nhiên dataset thành train, val, test theo tỉ lệ.
    
    Parameters:
    - image_dir: Đường dẫn đến thư mục chứa ảnh (ví dụ: 'dataset/images')
    - label_dir: Đường dẫn đến thư mục chứa nhãn (ví dụ: 'dataset/labels')
    - output_dir: Đường dẫn đến thư mục đầu ra (ví dụ: 'dataset_split')
    - train_ratio: Tỉ lệ cho tập train (mặc định 0.8)
    - val_ratio: Tỉ lệ cho tập val (mặc định 0.1)
    - test_ratio: Tỉ lệ cho tập test (mặc định 0.1)
    """
    
    # Kiểm tra tổng tỉ lệ
    if train_ratio + val_ratio + test_ratio != 1.0:
        raise ValueError("Tổng tỉ lệ train + val + test phải bằng 1.0")

    # Lấy danh sách file ảnh
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    random.shuffle(image_files)  # Xáo trộn ngẫu nhiên

    # Tính số lượng file cho từng tập
    total_files = len(image_files)
    train_count = int(total_files * train_ratio)
    val_count = int(total_files * val_ratio)
    test_count = total_files - train_count - val_count  # Đảm bảo tổng bằng 100%

    # Chia danh sách file
    train_files = image_files[:train_count]
    val_files = image_files[train_count:train_count + val_count]
    test_files = image_files[train_count + val_count:]

    # Tạo thư mục đầu ra
    splits = {'train': train_files, 'val': val_files, 'test': test_files}
    for split in splits:
        os.makedirs(os.path.join(output_dir, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, split, 'labels'), exist_ok=True)

    # Sao chép file ảnh và nhãn vào thư mục tương ứng
    for split, files in splits.items():
        for img_file in files:
            # Sao chép file ảnh
            src_img = os.path.join(image_dir, img_file)
            dst_img = os.path.join(output_dir, split, 'images', img_file)
            shutil.copy(src_img, dst_img)

            # Sao chép file nhãn (nếu tồn tại)
            label_file = img_file.rsplit('.', 1)[0] + '.txt'
            src_label = os.path.join(label_dir, label_file)
            dst_label = os.path.join(output_dir, split, 'labels', label_file)
            if os.path.exists(src_label):
                shutil.copy(src_label, dst_label)

    print(f"Đã chia dataset thành công:")
    print(f"- Train: {len(train_files)} files")
    print(f"- Val: {len(val_files)} files")
    print(f"- Test: {len(test_files)} files")

# Sử dụng hàm
image_dir = 'pedestrians/pedestrian_data/images'  # Đường dẫn đến thư mục ảnh
label_dir = 'pedestrians/pedestrian_data/labels'  # Đường dẫn đến thư mục nhãn
output_dir = 'dataset'  # Đường dẫn đến thư mục đầu ra

split_dataset(image_dir, label_dir, output_dir, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1)