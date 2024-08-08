# main/database.py
import sqlite3
from logging_config import *
from config import config


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
        log_function(f"Created table 'users' if it did not exist.", config["log_levels"]["level1"], config["log_files"]["database"], "database.py", 22)

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
        log_function(f"Created table 'posts' if it did not exist.", config["log_levels"]["level1"], config["log_files"]["database"],"database.py", 34)

        connection.commit()
        log_function(f"Database changes committed successfully.", config["log_levels"]["level1"], config["log_files"]["database"],"database.py", 37)
    except sqlite3.Error as e:
        log_function(f"Database error: {e}", config["log_levels"]["level2"], config["log_files"]["database"],"database.py", 39)
    except Exception as e:
        log_function(f"General error: {e}", config["log_levels"]["level2"], config["log_files"]["database"],"database.py", 41)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        log_function(f"Database connection closed.", config["log_levels"]["level1"], config["log_files"]["database"],"database.py", 47)