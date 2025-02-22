import sqlite3

conn = sqlite3.connect("bot_discord.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS personas (
    user_id INTEGER PRIMARY KEY,
    persona TEXT DEFAULT 'neutre'
);
""")

conn.commit()
conn.close()
print("✅ Base de données initialisée.")