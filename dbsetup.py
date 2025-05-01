# --- dbsetup.py (migrate.py) ---
import sqlite3

conn = sqlite3.connect("babyllm.db")
cursor = conn.cursor()

# --- Drop old chat_history table (for schema change) ---
cursor.execute("DROP TABLE IF EXISTS chat_history")

# --- Create users table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    name TEXT,
    prompts_used INTEGER DEFAULT 0,
    is_subscribed INTEGER DEFAULT 0
)
''')

# --- Create chat_history table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    query TEXT,
    answer TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

print("✅ Tables ensured.")

conn.commit()
conn.close()
