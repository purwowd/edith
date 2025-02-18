# app/service/pullall_service.py

import os
import subprocess
import sqlite3
import logging
import datetime
from fastapi import HTTPException

# Konfigurasi environment
ADB_PATH = os.getenv("ADB_PATH")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
DB_PATH = os.path.join(OUTPUT_DIR, "device_data.db")

REMOTE_HISTORY_FILE = os.getenv("REMOTE_HISTORY_FILE")
TEMP_HISTORY_FILE = os.getenv("TEMP_HISTORY_FILE")
LOCAL_HISTORY_FILE = os.path.join(OUTPUT_DIR, "History.db")

def run_adb_command(command):
    try:
        result = subprocess.run(
            [ADB_PATH] + command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ADB command failed: {e.stderr}")

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            brand TEXT,
            manufacturer TEXT,
            android_version TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT,
            body TEXT,
            date INTEGER,
            type INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            number TEXT,
            times_contacted INTEGER 
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS browser_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            last_visit_time INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            formatted_number TEXT,
            number TEXT,
            date INTEGER,
            duration INTEGER,
            type INTEGER,
            name TEXT,
            normalized_number TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_device_info():
    try:
        model = run_adb_command(["shell", "getprop", "ro.product.model"]).strip()
        brand = run_adb_command(["shell", "getprop", "ro.product.brand"]).strip()
        manufacturer = run_adb_command(["shell", "getprop", "ro.product.manufacturer"]).strip()
        android_version = run_adb_command(["shell", "getprop", "ro.build.version.release"]).strip()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO device_info (model, brand, manufacturer, android_version) VALUES (?, ?, ?, ?)",
            (model, brand, manufacturer, android_version)
        )
        conn.commit()
        conn.close()
        logging.info("Device info saved successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save device info: {str(e)}")

def save_call_logs():
    try:
        logging.info("Fetching Call Logs data...")
        call_logs_output = run_adb_command(["shell", "content", "query", "--uri", "content://call_log/calls"])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for line in call_logs_output.splitlines():
            if line.startswith("Row:"):
                try:
                    parts = {}
                    for kv in line.split(", ")[1:]:
                        if "=" in kv:
                            k, v = kv.split("=", 1)
                            parts[k] = v
                    cursor.execute(
                        """
                        INSERT INTO call_logs (formatted_number, number, date, duration, type, name, normalized_number) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            parts.get("formatted_number", "NULL"),
                            parts.get("number", "NULL"),
                            int(parts.get("date", 0)),
                            int(parts.get("duration", 0)),
                            int(parts.get("type", 0)),
                            parts.get("name", "NULL"),
                            parts.get("normalized_number", "NULL")
                        )
                    )
                except Exception as e:
                    logging.error(f"Error processing call log line: {line}. Error: {str(e)}")
        conn.commit()
        conn.close()
        logging.info("Call Logs data saved successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save Call Logs data: {str(e)}")

def save_contacts_and_sms():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        contacts_output = run_adb_command(["shell", "content", "query", "--uri", "content://contacts/phones"])
        for line in contacts_output.splitlines():
            if line.startswith("Row:"):
                parts = {k: v for k, v in (kv.split("=") for kv in line.split(", ")[1:])}
                cursor.execute(
                    "INSERT OR IGNORE INTO contacts (id, name, number, times_contacted) VALUES (?, ?, ?, ?)",
                    (
                        int(parts.get("_id", 0)),
                        parts.get("name", "NULL"),
                        parts.get("number", "NULL"),
                        parts.get("times_contacted", "NULL")
                    )
                )
        conn.commit()
    except Exception as e:
        logging.error(f"Error saving contacts: {str(e)}")
    finally:
        conn.close()

def save_sms():
    try:
        logging.info("Fetching SMS data...")
        sms_output = run_adb_command(["shell", "content", "query", "--uri", "content://sms"])
        logging.info(f"SMS Output: {sms_output}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for line in sms_output.splitlines():
            if line.startswith("Row:"):
                try:
                    parts = {}
                    for kv in line.split(", ")[1:]:
                        if "=" in kv:
                            k, v = kv.split("=", 1)
                            parts[k] = v
                    logging.info(f"Parsed SMS Line: {parts}")
                    if all(key in parts for key in ["address", "body", "date", "type"]):
                        cursor.execute(
                            "INSERT OR IGNORE INTO sms (address, body, date, type) VALUES (?, ?, ?, ?)",
                            (
                                parts["address"],
                                parts["body"],
                                int(parts["date"]),
                                int(parts["type"])
                            )
                        )
                    else:
                        logging.warning(f"Skipping incomplete SMS data: {parts}")
                except Exception as e:
                    logging.error(f"Error processing SMS line: {line}. Error: {str(e)}")
        conn.commit()
        conn.close()
        logging.info("SMS data saved successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save SMS data: {str(e)}")

def pull_browser_history():
    try:
        logging.info("Copying browser history to /sdcard/...")
        run_adb_command(["shell", "su", "-c", f"cp {REMOTE_HISTORY_FILE} {TEMP_HISTORY_FILE}"])
        logging.info("Pulling browser history to local machine...")
        run_adb_command(["pull", TEMP_HISTORY_FILE, LOCAL_HISTORY_FILE])
        logging.info("Cleaning up temporary file...")
        run_adb_command(["shell", "su", "-c", f"rm {TEMP_HISTORY_FILE}"])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        history_conn = sqlite3.connect(LOCAL_HISTORY_FILE)
        history_cursor = history_conn.cursor()
        history_cursor.execute("SELECT url, title, last_visit_time FROM urls")
        data = history_cursor.fetchall()
        cursor.executemany(
            "INSERT INTO browser_history (url, title, last_visit_time) VALUES (?, ?, ?)",
            data
        )
        conn.commit()
        conn.close()
        history_conn.close()
        logging.info("Browser history merged successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull browser history: {str(e)}")
    
def translate_timestamp(last_visit_time):
    # Chrome/WebKit timestamp (microseconds since Jan 1, 1601)
    epoch_start = datetime.datetime(1601, 1, 1)
    converted_time = epoch_start + datetime.timedelta(microseconds=last_visit_time)
    return converted_time.strftime('%Y-%m-%d %H:%M:%S')

def pull_all_data():
    create_db()
    save_device_info()
    save_contacts_and_sms()
    save_sms()
    save_call_logs()
    return {"message": "All data saved successfully."}

def pull_all_data_rooted():
    create_db()
    save_device_info()
    save_contacts_and_sms()
    pull_browser_history()
    save_sms()
    save_call_logs()
    return {"message": "All data saved successfully."}






