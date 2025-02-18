# app/service/sms_service.py

import os
import sqlite3
from app.service.PullAll_service import DB_PATH, datetime

def get_db_path():
    # Pastikan environment OUTPUT_DIR sudah didefinisikan, jika tidak gunakan "./" sebagai default
    output_dir = os.getenv("OUTPUT_DIR", "./")
    return os.path.join(output_dir, "device_data.db")

def translate_timestamp(last_visit_time):
    # Chrome/WebKit timestamp (microseconds since Jan 1, 1601)
    epoch_start = datetime.datetime(1601, 1, 1)
    converted_time = epoch_start + datetime.timedelta(microseconds=last_visit_time)
    return converted_time.strftime('%Y-%m-%d %H:%M:%S')

def get_browser_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, title, last_visit_time FROM browser_history")
    data = cursor.fetchall()
    conn.close()
    
    # Convert timestamps
    history = [
        {
            "id": row[0],
            "url": row[1],
            "title": row[2],
            "last_visit_time": translate_timestamp(row[3])
        }
        for row in data
    ]
    
    return history
