from fastapi import FastAPI, HTTPException, requests
import subprocess
import os
import sqlite3
import logging
import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import datetime

app = FastAPI()

load_dotenv()

# Get the absolute path to the static and templates directories
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Mount static files directory
app.mount("/assets", StaticFiles(directory=static_dir), name="assets")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# ADB_PATH = r"C:\\Users\\Lutfizp\\Downloads\\androidkerja\\platform-tools\\adb.exe"
ADB_PATH = os.getenv("ADB_PATH")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
DB_PATH = os.path.join(OUTPUT_DIR, "device_data.db")

#REMOTE_HISTORY_FILE = "/data/data/com.android.chrome/app_chrome/Default/History"
REMOTE_HISTORY_FILE = os.getenv("REMOTE_HISTORY_FILE")
TEMP_HISTORY_FILE = os.getenv("TEMP_HISTORY_FILE")
LOCAL_HISTORY_FILE = os.path.join(OUTPUT_DIR, "History.db")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


logging.basicConfig(level=logging.INFO)

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
        cursor.execute("INSERT INTO device_info (model, brand, manufacturer, android_version) VALUES (?, ?, ?, ?)",
                       (model, brand, manufacturer, android_version))
        conn.commit()
        conn.close()
        logging.info("Device info saved successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save device info: {str(e)}")
    
def save_call_logs():
    try:
        logging.info("Fetching Call Logs data...")

        # Menjalankan perintah ADB untuk mendapatkan data call logs
        call_logs_output = run_adb_command([
            "shell", "content", "query", "--uri", "content://call_log/calls"
        ])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for line in call_logs_output.splitlines():
            if line.startswith("Row:"):
                try:
                    parts = {}
                    for kv in line.split(", ")[1:]:  # Skip "Row: X"
                        if "=" in kv:
                            k, v = kv.split("=", 1)
                            parts[k] = v

                    # Masukkan data ke dalam database jika semua field tersedia
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
                cursor.execute("INSERT OR IGNORE INTO contacts (id, name, number, times_contacted) VALUES (?, ?, ?, ?)",
                               (int(parts.get("_id", 0)), parts.get("name", "NULL"), parts.get("number", "NULL"), parts.get("times_contacted", "NULL")))
        conn.commit()
    except Exception as e:  # Tambahkan blok except untuk menangani error
        print(f"Error saving contacts: {str(e)}")
    finally:
        conn.close()  # Pastikan koneksi database ditutup di blok finally
        
def save_sms():
    try:
        logging.info("Fetching SMS data...")
        # Tambahkan --limit untuk mendapatkan lebih banyak data
        sms_output = run_adb_command([
            "shell", "content", "query",
            "--uri", "content://sms" # Batas jumlah SMS yang ingin diambil
        ])
        
        logging.info(f"SMS Output: {sms_output}")  # Logging output ADB
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for line in sms_output.splitlines():
            if line.startswith("Row:"):
                try:
                    parts = {}
                    for kv in line.split(", ")[1:]:  # Skip "Row: X"
                        if "=" in kv:  # Pastikan ada '=' di dalam string
                            k, v = kv.split("=", 1)  # Pisahkan key dan value
                            parts[k] = v
                    
                    logging.info(f"Parsed SMS Line: {parts}")  # Logging hasil parsing
                    
                    # Simpan data ke database jika semua field tersedia (kecuali _id)
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
        cursor.executemany("INSERT INTO browser_history (url, title, last_visit_time) VALUES (?, ?, ?)", data)
        
        conn.commit()
        conn.close()
        history_conn.close()
        
        logging.info("Browser history merged successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull browser history: {str(e)}")

@app.get("/pull-all")
async def pull_all_data(request: Request):
    create_db()
    save_device_info()
    save_contacts_and_sms()
    save_sms()
    save_call_logs()
    return {"message": "All data saved successfully."}

@app.get("/most-contacted")
async def most_contacts(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT address, COUNT(*) as sms_count
            FROM sms
            GROUP BY address
            ORDER BY sms_count DESC
        """)
        sms_results = cursor.fetchall()

        cursor.execute("""
            SELECT number, COUNT(*) as call_count
            FROM call_logs
            GROUP BY number
            ORDER BY call_count DESC
        """)
        call_results = cursor.fetchall()

        conn.close()

        # Format hasil untuk SMS
        sms_senders = [
            {"address": row[0], "count": row[1], "type": "sms"}
            for row in sms_results
        ]

        # Format hasil untuk panggilan
        call_senders = [
            {"address": row[0], "count": row[1], "type": "call"}
            for row in call_results
        ]

        #  kedua hasil (SMS dan Call)
        combined_results = sms_senders + call_senders
        combined_results = sorted(combined_results, key=lambda x: x["count"], reverse=True)

        return {"contacts": combined_results}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.get("/pull-all rooted")
async def pull_all_data(request: Request):
    create_db()
    save_device_info()
    save_contacts_and_sms()
    pull_browser_history()
    save_sms()
    save_call_logs()
    return {"message": "All data saved successfully."}


def translate_timestamp(last_visit_time):
    # Chrome/WebKit timestamp (microseconds since Jan 1, 1601)
    epoch_start = datetime.datetime(1601, 1, 1)
    converted_time = epoch_start + datetime.timedelta(microseconds=last_visit_time)
    return converted_time.strftime('%Y-%m-%d %H:%M:%S')

@app.get("/browser-history")
async def get_browser_history(request: Request):
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

@app.get("/contacts")
async def get_contacts(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    data = cursor.fetchall()
    conn.close()
    return data

@app.get("/sms")
async def get_sms(request: Request):
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

@app.get("/device-info")
async def get_device_info(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM device_info")
    data = cursor.fetchall()
    conn.close()
    return data

from fastapi import HTTPException

WORDLIST_FILE = "wordlist.txt"

def load_wordlist():
    try:
        with open(WORDLIST_FILE, "r", encoding="utf-8") as file:
            words = [line.strip() for line in file.readlines()]
        return words
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Wordlist file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading wordlist: {str(e)}")
    
@app.get("/search-contact")
async def search_contact(request: Request):
    try:
        # Load wordlist dari file
        wordlist = load_wordlist()
        
        # Buka koneksi ke database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        results = []
        seen_numbers = set()  # Set untuk menyimpan nomor yang sudah ditambahkan
        
        for word in wordlist:
            # Query untuk mencari nama kontak yang cocok secara case-insensitive
            cursor.execute("SELECT name, number FROM contacts WHERE LOWER(name) = ?", (word.lower(),))
            matches = cursor.fetchall()
            
            # Tambahkan hasil ke daftar jika nomor belum ada
            for match in matches:
                if match[1] not in seen_numbers:  
                    results.append({"name": match[0], "number": match[1]})
                    seen_numbers.add(match[1])  # Tandai nomor sebagai sudah dimasukkan
        
        # Tutup koneksi database
        conn.close()
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching contacts: {str(e)}")

    
@app.get("/call-logs")
async def get_call_logs(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM call_logs")
    data = cursor.fetchall()
    conn.close()
    return data

