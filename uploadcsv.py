import os
import csv
import cloudinary
import cloudinary.uploader

# Load biến môi trường Cloudinary (từ .env hoặc gán trực tiếp)
cloudinary.config(
  cloud_name = "dfclgysp0",
  api_key = "232176167698962",
  api_secret = "c9-ntcdMy-b9IHK4p7HPyoGeXxI"
)

# Thư mục chứa ảnh
violation_folder = "violations"
csv_file = "./react-fe/public/uploaded_images.csv"

# Đọc danh sách file đã có trong CSV để tránh trùng lặp
existing_files = set()
if os.path.exists(csv_file):
    with open(csv_file, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_files.add(row['fileName'])

# Lặp qua ảnh trong thư mục và upload ảnh chưa có
new_rows = []
for file_name in os.listdir(violation_folder):
    if file_name.endswith(".jpg") and file_name not in existing_files:
        file_path = os.path.join(violation_folder, file_name)
        print(f"Đang upload: {file_path}")

        try:
            upload_result = cloudinary.uploader.upload(file_path, folder="violations")
            image_url = upload_result['secure_url']
            # Lấy ngày từ tên file: "violation_2025-04-10_15-30-20.jpg"
            date_part = file_name.split('_')[1]  # 2025-04-10
            new_rows.append({
                "fileName": file_name,
                "url": image_url,
                "timestamp": date_part
            })
        except Exception as e:
            print(f"Lỗi khi upload ảnh {file_name}: {e}")

# Ghi vào CSV
fieldnames = ["fileName", "url", "timestamp"]
file_exists = os.path.exists(csv_file)

with open(csv_file, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
    for row in new_rows:
        writer.writerow(row)

print("✅ Đã cập nhật CSV thành công.")
