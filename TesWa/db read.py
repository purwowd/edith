import configparser
import sqlite3
from sqlite3 import Connection
from typing import List, Optional, Dict
import time

class Message:
    def __init__(self, received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type, latitude,
                 longitude, media_path, sender):
        self.received_timestamp = received_timestamp
        self.remote_resource = remote_resource
        self.key_from_me = key_from_me
        self.data = data
        self.media_caption = media_caption
        self.media_wa_type = media_wa_type
        self.latitude = latitude
        self.longitude = longitude
        self.media_path = media_path
        self.received_timestamp_str = Message.__timestamp_to_str(received_timestamp)
        self.sender = sender

    @staticmethod
    def __timestamp_to_str(timestamp: str) -> str:
        ts = int(timestamp) / 1000.0
        return time.strftime('%d.%m.%Y %H:%M', time.localtime(ts))

    def get_content(self) -> str:
        media_caption = self.media_caption if self.media_caption is not None else ""
        return self.data if self.media_wa_type == 0 else media_caption

    def get_media(self) -> str:
        media = ""
        if self.media_wa_type == 1:
            media = f"[Image] {self.media_path}"
        elif self.media_wa_type == 2:
            media = f"[Audio] {self.media_path}"
        elif self.media_wa_type == 3:
            media = f"[Video] {self.media_path}"
        elif self.media_wa_type == 4:
            media = f"[Contact] {self.media_path} (Download)"
        elif self.media_wa_type == 5:
            media = f"[Location] {self.latitude}, {self.longitude} ({self.media_path if self.media_path else 'Link'})"
        elif self.media_wa_type == 7:
            media = f"[System Message] {self.media_path}"
        elif self.media_wa_type == 9:
            media = f"[Document] {self.media_path}"
        elif self.media_wa_type == 10:
            media = "[Missed Call]"
        elif self.media_wa_type == 13:
            media = "[Animated GIF]"
        elif self.media_wa_type == 14:
            media = f"[Multiple Contacts] {self.media_path}"
        elif self.media_wa_type == 15:
            media = "[Deleted]"
        elif self.media_wa_type == 16:
            media = f"[Live Location] {self.latitude}, {self.longitude} ({self.media_path if self.media_path else 'Link'})"
        elif self.media_wa_type == 20:
            media = "[Sticker]"
        elif self.media_wa_type == 42:
            media = f"[View Once] {self.media_path}"
        else:
            media = f"[Unknown medium] {self.media_path}"
        return media

    def get_sender_name(self) -> str:
        if self.sender:
            return self.sender
        elif self.remote_resource:
            return self.remote_resource.split("@")[0]
        else:
            return self.remote_resource

    def __str__(self):
        direction = ">" if self.key_from_me else "<"
        return f"{direction} {self.received_timestamp_str} - {self.get_content()} {self.get_media()}"


class Chat:
    def __init__(self, key_remote_jid, subject: str, sort_timestamp, name: str, messages: list):
        self.key_remote_jid = key_remote_jid
        self.subject = subject
        self.sort_timestamp = sort_timestamp
        self.name = name
        self.phone_number = key_remote_jid.split("@")[0]
        self.title = self.__get_chat_title()
        self.messages = messages

    def __get_chat_title(self):
        if self.subject is not None:
            return self.subject
        elif self.name is not None:
            return self.name
        else:
            return self.phone_number

    def __str__(self):
        return f"Chat: {self.title}\nMessages:\n" + "\n".join([str(message) for message in self.messages])


def query_messages_from_table_messages(con: Connection, key_remote_jid: str, contacts: Dict[str, Optional[str]]) -> List[Message]:
    cur = con.cursor()
    query = """
        SELECT received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type, latitude, longitude,
        CASE
            WHEN mm.file_path IS NOT NULL THEN mm.file_path
            WHEN mm.media_name IS NOT NULL THEN mm.media_name
            ELSE messages.media_name
        END as media_path
        FROM messages 
        LEFT JOIN message_media AS mm ON mm.message_row_id = messages._id
        WHERE key_remote_jid = ?
        ORDER BY max(receipt_server_timestamp, received_timestamp)
    """
    messages = []
    for row in cur.execute(query, (key_remote_jid,)):
        messages.append(Message(*row, contacts.get(row[1], None)))
    return messages


def query_messages_from_table_message(con: Connection, key_remote_jid: str, contacts: Dict[str, Optional[str]]) -> List[Message]:
    cur = con.cursor()
    query = """
        SELECT m.timestamp, jid, m.from_me, 
        CASE
            WHEN mr.revoked_key_id > 1 THEN '[Deleted]'
            ELSE m.text_data
        END AS text,
        m.message_type, message_location.latitude, message_location.longitude,
        CASE
            WHEN mm.file_path IS NOT NULL THEN mm.file_path
            WHEN mm.media_name IS NOT NULL THEN mm.media_name
            ELSE ""
        END as media_path
        FROM message AS m 
        LEFT JOIN chat_view AS cv ON m.chat_row_id = cv._id
        LEFT JOIN jid ON m.sender_jid_row_id = jid._id
        LEFT JOIN message_revoked AS mr ON m._id = mr.message_row_id
        LEFT JOIN message_media AS mm ON m._id = mm.message_row_id
        LEFT JOIN message_location ON m._id = message_location.message_row_id
        WHERE jid = ?
        ORDER BY m.timestamp
    """
    messages = []
    for row in cur.execute(query, (key_remote_jid,)):
        messages.append(Message(*row, contacts.get(row[1], None)))
    return messages


def query_all_chats(db_path: str, contacts: Dict[str, Optional[str]]) -> List[Chat]:
    chats = []
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Check which table to use: Older databases use the table "messages", newer ones the table "message"
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
    table_messages_exists = cur.fetchone() is not None
    print("[+] Using table 'messages'" if table_messages_exists else "[+] Using table 'message'")

    query = "SELECT jid as key_remote_jid, subject, sort_timestamp FROM chat_view WHERE sort_timestamp IS NOT NULL ORDER BY sort_timestamp DESC"
    for key_remote_jid, subject, sort_timestamp in cur.execute(query):
        if table_messages_exists:
            messages = query_messages_from_table_messages(con, key_remote_jid, contacts)
        else:
            messages = query_messages_from_table_message(con, key_remote_jid, contacts)

        chats.append(Chat(key_remote_jid, subject, sort_timestamp, contacts.get(key_remote_jid, None), messages))
    con.close()
    return chats


def query_contacts(db_path: str) -> Dict[str, Optional[str]]:
    contacts = {}
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for jid, wa_name, display_name in cur.execute("SELECT jid, wa_name, display_name FROM wa_contacts"):
        if display_name:
            contacts[jid] = display_name
        elif wa_name:
            contacts[jid] = wa_name
    con.close()
    return contacts


def main():
    print("### WhatsApp Database Exporter ###")

    db_path = r"C:\Users\Lutfizp\Downloads\whatsapp_data\msgstore.db"
    wa_db_path = r"C:\Users\Lutfizp\Downloads\whatsapp_data\wa.db"

    print("[+] Reading Database")
    contacts = query_contacts(wa_db_path) if wa_db_path else {}
    chats = query_all_chats(db_path, contacts)

    print("[+] Displaying Chats and Messages")
    for chat in chats:
        print(chat)


if __name__ == "__main__":
    main()