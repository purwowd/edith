import os
import sqlite3
import subprocess

def pull_whatsapp_db(adb_path, output_dir):
    try:
        # Buat direktori output jika belum ada
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Path penyimpanan file di PC
        local_wa_db_path = os.path.join(output_dir, "wa.db")
        local_msgstore_db_path = os.path.join(output_dir, "msgstore.db")
        
        # Perintah ADB untuk masuk ke shell dan menggunakan su
        adb_shell_cmd_wa = f'"{adb_path}" shell "su -c \"cp /data/data/com.whatsapp/databases/wa.db /sdcard/wa.db\""'
        adb_shell_cmd_msgstore = f'"{adb_path}" shell "su -c \"cp /data/data/com.whatsapp/databases/msgstore.db /sdcard/msgstore.db\""'
        
        subprocess.run(adb_shell_cmd_wa, shell=True, capture_output=True, text=True)
        subprocess.run(adb_shell_cmd_msgstore, shell=True, capture_output=True, text=True)
        
        # Perintah ADB untuk menarik database WhatsApp
        adb_pull_cmd_wa = f'"{adb_path}" pull /sdcard/wa.db "{local_wa_db_path}"'
        adb_pull_cmd_msgstore = f'"{adb_path}" pull /sdcard/msgstore.db "{local_msgstore_db_path}"'
        
        print("Menarik database WhatsApp...")
        result_wa = subprocess.run(adb_pull_cmd_wa, shell=True, capture_output=True, text=True)
        result_msgstore = subprocess.run(adb_pull_cmd_msgstore, shell=True, capture_output=True, text=True)
        
        if result_wa.returncode == 0 and result_msgstore.returncode == 0:
            print("Database berhasil diunduh ke:", local_wa_db_path, "dan", local_msgstore_db_path)
            return local_wa_db_path, local_msgstore_db_path
        else:
            print("Gagal menarik database:", result_wa.stderr, result_msgstore.stderr)
            return None, None
    except Exception as e:
        print("Terjadi kesalahan:", str(e))
        return None, None

def read_whatsapp_db(db_path):
    try:
        if not os.path.exists(db_path):
            print("File database tidak ditemukan!")
            return
        
        # Koneksi ke database SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Menampilkan daftar tabel
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tabel yang tersedia di database:")
        for table in tables:
            print(table[0])
        
        conn.close()
    except Exception as e:
        print("Terjadi kesalahan saat membaca database:", str(e))

def read_chats(db_path):
    try:
        if not os.path.exists(db_path):
            print("File database tidak ditemukan!")
            return
        
        # Koneksi ke database SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Menampilkan 10 chat terakhir
        print("\nMenampilkan 10 chat terakhir:")
        cursor.execute("SELECT key_remote_jid, data, timestamp FROM messages ORDER BY timestamp DESC LIMIT 10;")
        chats = cursor.fetchall()
        
        for chat in chats:
            print(f"Dari: {chat[0]} | Pesan: {chat[1]} | Waktu: {chat[2]}")
        
        conn.close()
    except Exception as e:
        print("Terjadi kesalahan saat membaca chat:", str(e))

# Path ADB di sistem Anda
ADB_PATH = r"C:\Users\Lutfizp\Downloads\androidkerja\platform-tools\adb.exe"
OUTPUT_DIR = r"C:\Users\Lutfizp\Downloads\whatsapp_data"

db_path_wa, db_path_msgstore = pull_whatsapp_db(ADB_PATH, OUTPUT_DIR)
if db_path_wa:
    read_whatsapp_db(db_path_wa)
if db_path_msgstore:
    read_chats(db_path_msgstore)
