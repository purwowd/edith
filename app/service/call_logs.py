import os
import sqlite3
from app.service.PullAll_service import DB_PATH
from app.service.browserhistory import translate_timestamp
def get_db_path():
    # Pastikan environment OUTPUT_DIR sudah didefinisikan, jika tidak gunakan "./" sebagai default
    output_dir = os.getenv("OUTPUT_DIR", "./")
    return os.path.join(output_dir, "device_data.db")

def get_call_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, number, date, duration, type, name, normalized_number FROM call_logs")
    data = cursor.fetchall()
    conn.close()

def get_call_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM call_logs")
    data = cursor.fetchall()
    conn.close()
    return data
    
    return data