import os
import sqlite3
from app.service.PullAll_service import DB_PATH
def get_db_path():
    # Pastikan environment OUTPUT_DIR sudah didefinisikan, jika tidak gunakan "./" sebagai default
    output_dir = os.getenv("OUTPUT_DIR", "./")
    return os.path.join(output_dir, "device_data.db")

def get_device_info():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM device_info")
    data = cursor.fetchall()
    conn.close()
    return data