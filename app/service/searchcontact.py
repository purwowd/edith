from fastapi import HTTPException
from dotenv import load_dotenv
import os
import sqlite3
from app.service.PullAll_service import DB_PATH

load_dotenv()

def get_db_path():
    # Pastikan environment OUTPUT_DIR sudah didefinisikan, jika tidak gunakan "./" sebagai default
    output_dir = os.getenv("OUTPUT_DIR", "./")
    return os.path.join(output_dir, "device_data.db")

WORDLIST_FILE = os.getenv("WORDLIST_FILE")

def load_wordlist():
    try:
        with open(WORDLIST_FILE, "r", encoding="utf-8") as file:
            words = [line.strip() for line in file.readlines()]
        return words
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Wordlist file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading wordlist: {str(e)}")
    
def search_contact():
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

    