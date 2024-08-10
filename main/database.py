# main/database.py
import sqlite3
from config import config
import logging

logger = logging.getLogger(__name__)

def setup_database():
    try:
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
        logger.info("Created table 'users' if it did not exist.")

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
        logger.info("Created table 'posts' if it did not exist.")

        connection.commit()
        logger.info("Database changes committed successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}", exc_info=1)
    except Exception as e:
        logger.error(f"General error: {e}", exc_info=1)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        logger.info(f"Database connection closed.")