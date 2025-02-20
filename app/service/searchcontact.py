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
        wordlist = load_wordlist()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        results = []
        seen_numbers = set()
        
        for word in wordlist:
            word_lower = word.lower()
            
            # Cari di tabel contacts
            cursor.execute("""
                SELECT name, number FROM contacts WHERE LOWER(name) = ?
            """, (word_lower,))
            matches = cursor.fetchall()
            
            for match in matches:
                if match[1] not in seen_numbers:
                    results.append({"name": match[0], "number": match[1]})
                    seen_numbers.add(match[1])
            
            # Cari di tabel wa_contact
            cursor.execute("""
                SELECT jid, number, raw_contact_id, display_name, given_name, wa_name 
                FROM wa_contact 
                WHERE LOWER(display_name) = ? OR LOWER(given_name) = ? OR LOWER(wa_name) = ?
            """, (word_lower, word_lower, word_lower))
            matches = cursor.fetchall()
            
            for match in matches:
                if match[1] not in seen_numbers:
                    results.append({
                        "jid": match[0],
                        "number": match[1],
                        "raw_contact_id": match[2],
                        "display_name": match[3],
                        "given_name": match[4],
                        "wa_name": match[5],
                    })
                    seen_numbers.add(match[1])
        
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching contacts: {str(e)}")
    