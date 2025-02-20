# app/service/sms_service.py

import os
import sqlite3
from app.service.PullAll_service import DB_PATH
from app.service.browserhistory import translate_timestamp
def get_db_path():
    # Pastikan environment OUTPUT_DIR sudah didefinisikan, jika tidak gunakan "./" sebagai default
    output_dir = os.getenv("OUTPUT_DIR", "./")
    return os.path.join(output_dir, "device_data.db")


def sms():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, address, body, date, type FROM sms")
    rows = cursor.fetchall()
    conn.close()
    
    sms_list = []
    for row in rows:
        sms_list.append({
            "id": row[0],
            "address": row[1],
            "body": row[2],
            "date": row[3],
            "type": row[4]
        })
    
    return sms_list
