import sqlite3
from config import config, group_chat_id, roles, user_lang, user_media


def setup_database():
    connection = sqlite3.connect(config['database']['path'])
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT,
            chat_id INTEGER UNIQUE,
            status TEXT,
            lang TEXT,
            warns INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            media BLOB,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

# Call the setup_database function to ensure tables are created
setup_database()