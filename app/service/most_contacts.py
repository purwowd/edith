import os
import sqlite3
from app.service.PullAll_service import DB_PATH
from fastapi import HTTPException


def get_db_path():
    # Pastikan environment OUTPUT_DIR sudah didefinisikan, jika tidak gunakan "./" sebagai default
    output_dir = os.getenv("OUTPUT_DIR", "./")
    return os.path.join(output_dir, "device_data.db")

def most_contacts():
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