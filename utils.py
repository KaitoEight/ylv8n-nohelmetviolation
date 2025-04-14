import pandas as pd
import logging
import os
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import requests
import cloudinary.uploader
import json

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_logger(log_file='traffic_violation.log'):
    """Thiết lập logger với file và console output."""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
def upload_to_cloudinary(image_path):
    """Upload ảnh lên Cloudinary với retry."""
    try:
        response = cloudinary.uploader.upload(image_path)
        logger.info(f"Uploaded to Cloudinary: {response['secure_url']}")
        return response['secure_url']
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
def send_image_to_api(image_url, api_url):
    """Gửi URL đến API với retry."""
    payload = {"image_url": image_url}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        logger.info(f"API response: {response_json}")
        return response_json.get("license_plate", "unknown")
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise

def update_csv(timestamp, license_plate, image_path, csv_path):
    """Ghi hoặc cập nhật CSV."""
    columns = ["Thời gian vi phạm", "Biển số xe", "Đường dẫn hình ảnh"]
    try:
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
        logger.info(f"Updated CSV: {timestamp} - {license_plate}")
    except Exception as e:
        logger.error(f"Failed to update CSV: {e}")