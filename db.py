# --- db.py ---
import sqlite3

DB_NAME = "babyllm.db"

# Initialize the database schema

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            prompts_used INTEGER DEFAULT 0,
            is_subscribed INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            query TEXT,
            answer TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# --- User management ---
def get_user_by_email(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(email, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (email, name, prompts_used, is_subscribed) 
        VALUES (?, ?, 0, 0)
    """, (email, name))
    conn.commit()
    conn.close()

def increment_prompt_count(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET prompts_used = prompts_used + 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def get_prompt_count(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT prompts_used FROM users WHERE email = ?", (email,))
    count = cursor.fetchone()
    conn.close()
    return count[0] if count else 0

def update_subscription(email, subscribed=True):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_subscribed = ? WHERE email = ?", (int(subscribed), email))
    conn.commit()
    conn.close()

def is_user_subscribed(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_subscribed FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return bool(result[0]) if result else False

# --- Chat history ---
def get_chat_history(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT query, answer, timestamp FROM chat_history WHERE email = ? ORDER BY id DESC", (email,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_chat(email, query, answer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (email, query, answer) 
        VALUES (?, ?, ?)
    """, (email, query, answer))
    conn.commit()
    conn.close()