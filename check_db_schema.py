
import sqlite3
from pathlib import Path

db_path = Path("backend/chat_history.db")
if not db_path.exists():
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("PRAGMA table_info(sessions)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Sessions table columns: {columns}")
    
    cursor = conn.execute("PRAGMA table_info(messages)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Messages table columns: {columns}")
    conn.close()
