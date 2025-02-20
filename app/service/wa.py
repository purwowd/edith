import os
import sqlite3
import logging
from fastapi import HTTPException
from dotenv import load_dotenv
from app.service.PullAll_service import DB_PATH

load_dotenv()
def get_db_path():
    # Pastikan environment OUTPUT_DIR sudah didefinisikan, jika tidak gunakan "./" sebagai default
    output_dir = os.getenv("OUTPUT_DIR", "./")
    return os.path.join(output_dir, "device_data.db")
# Setup logging
logging.basicConfig(level=logging.INFO)

def wa_contacts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wa_contact")
    data = cursor.fetchall()
    conn.close()
    return data

def msg_jid():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM msg_jid")
    data = cursor.fetchall()
    conn.close()
    return data

def msg_message():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM msg_message")
    data = cursor.fetchall()
    conn.close()
    return data



