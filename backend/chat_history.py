"""Chat history storage with SQLite for local and PostgreSQL for production."""
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_PRODUCTION = bool(DATABASE_URL and DATABASE_URL.startswith("postgres"))

# SQLite path for local development
SQLITE_PATH = Path(__file__).parent / "chat_history.db"


class ChatHistoryDB:
    """Chat history database abstraction layer."""

    def __init__(self) -> None:
        """Initialize database connection."""
        if IS_PRODUCTION:
            self._init_postgres()
        else:
            self._init_sqlite()

    def _init_sqlite(self) -> None:
        """Initialize SQLite database."""
        self._is_postgres = False
        self._create_tables_sqlite()

    def _init_postgres(self) -> None:
        """Initialize PostgreSQL database."""
        self._is_postgres = True
        try:
            import psycopg2
            self._pg_pool = None  # Will connect on demand
            self._create_tables_postgres()
        except ImportError:
            print("Warning: psycopg2 not installed, falling back to SQLite")
            self._init_sqlite()

    @contextmanager
    def _get_sqlite_conn(self):
        """Get SQLite connection context manager."""
        conn = sqlite3.connect(str(SQLITE_PATH))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _create_tables_sqlite(self) -> None:
        """Create SQLite tables."""
        with self._get_sqlite_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            # Add title column if it doesn't exist (for existing DBs)
            try:
                conn.execute("ALTER TABLE sessions ADD COLUMN title TEXT")
            except Exception:
                pass  # Column already exists
            
            try:
                conn.execute("ALTER TABLE sessions ADD COLUMN metadata TEXT")
            except Exception as e:
                # Log error to file
                with open("db_migration_error.log", "a") as f:
                    f.write(f"{datetime.now()}: Migration error: {e}\n")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    provider TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            # Add provider column to messages if missing
            try:
                conn.execute("ALTER TABLE messages ADD COLUMN provider TEXT")
            except Exception:
                pass

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id, created_at)
            """)

    def _create_tables_postgres(self) -> None:
        """Create PostgreSQL tables."""
        import psycopg2
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                # Add title column if missing
                cur.execute("""
                    ALTER TABLE sessions ADD COLUMN IF NOT EXISTS title TEXT
                """)
                cur.execute("""
                    ALTER TABLE sessions ADD COLUMN IF NOT EXISTS metadata JSONB
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        provider TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                # Add provider column if missing
                cur.execute("""
                    ALTER TABLE messages ADD COLUMN IF NOT EXISTS provider TEXT
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_session 
                    ON messages(session_id, created_at)
                """)

    def create_session(self, metadata: Optional[Dict] = None) -> str:
        """Create a new chat session.
        
        Returns:
            Session ID (UUID string).
        """
        session_id = str(uuid.uuid4())
        
        if self._is_postgres:
            import psycopg2
            import json
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO sessions (id, metadata) VALUES (%s, %s)",
                        (session_id, json.dumps(metadata) if metadata else None)
                    )
        else:
            import json
            with self._get_sqlite_conn() as conn:
                conn.execute(
                    "INSERT INTO sessions (id, metadata) VALUES (?, ?)",
                    (session_id, json.dumps(metadata) if metadata else None)
                )
        
        return session_id

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        provider: Optional[str] = None
    ) -> int:
        """Add a message to a session.
        
        Args:
            session_id: Session ID.
            role: 'user' or 'assistant'.
            content: Message content.
            provider: LLM provider used (for assistant messages).
            
        Returns:
            Message ID.
        """
        if self._is_postgres:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO messages (session_id, role, content, provider) 
                           VALUES (%s, %s, %s, %s) RETURNING id""",
                        (session_id, role, content, provider)
                    )
                    msg_id = cur.fetchone()[0]
                    cur.execute(
                        "UPDATE sessions SET updated_at = NOW() WHERE id = %s",
                        (session_id,)
                    )
        else:
            with self._get_sqlite_conn() as conn:
                cursor = conn.execute(
                    """INSERT INTO messages (session_id, role, content, provider, created_at) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (session_id, role, content, provider, datetime.now())
                )
                msg_id = cursor.lastrowid
                conn.execute(
                    "UPDATE sessions SET updated_at = ? WHERE id = ?",
                    (datetime.now(), session_id)
                )
        
        return msg_id

    def get_session_messages(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get messages for a session (most recent first, then reversed).
        
        Args:
            session_id: Session ID.
            limit: Maximum number of messages to return.
            
        Returns:
            List of message dicts with role, content, provider, created_at.
        """
        if self._is_postgres:
            import psycopg2
            import psycopg2.extras
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(
                        """SELECT role, content, provider, created_at 
                           FROM messages 
                           WHERE session_id = %s 
                           ORDER BY created_at DESC 
                           LIMIT %s""",
                        (session_id, limit)
                    )
                    messages = [dict(row) for row in cur.fetchall()]
        else:
            with self._get_sqlite_conn() as conn:
                try:
                    cursor = conn.execute(
                        """SELECT role, content, provider, created_at 
                        FROM messages 
                        WHERE session_id = ? 
                        ORDER BY created_at DESC 
                        LIMIT ?""",
                        (session_id, limit)
                    )
                    messages = [dict(row) for row in cursor.fetchall()]
                except Exception as e:
                    with open("db_msg_error.log", "a") as f:
                        f.write(f"{datetime.now()}: Msg query error: {e}\n")
                    # Fallback
                    cursor = conn.execute(
                        """SELECT role, content 
                        FROM messages 
                        WHERE session_id = ? 
                        ORDER BY id DESC 
                        LIMIT ?""",
                        (session_id, limit)
                    )
                    messages = []
                    for row in cursor.fetchall():
                        d = dict(row)
                        d['provider'] = None
                        d['created_at'] = None
                        messages.append(d)
        
        # Return in chronological order
        return list(reversed(messages))

    def get_context_for_llm(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get conversation context formatted for LLM.
        
        Args:
            session_id: Session ID.
            limit: Maximum number of message pairs to include.
            
        Returns:
            List of {"role": "user"|"assistant", "content": "..."} dicts.
        """
        messages = self.get_session_messages(session_id, limit=limit * 2)
        return [{"role": m["role"], "content": m["content"]} for m in messages]

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        if self._is_postgres:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM sessions WHERE id = %s", (session_id,))
                    return cur.fetchone() is not None
        else:
            with self._get_sqlite_conn() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
                )
                return cursor.fetchone() is not None

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions.
        
        Returns:
            List of session dicts with id, created_at, updated_at.
        """
        if self._is_postgres:
            import psycopg2
            import psycopg2.extras
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(
                        """SELECT id, title, created_at, updated_at, metadata 
                           FROM sessions 
                           ORDER BY updated_at DESC 
                           LIMIT %s""",
                        (limit,)
                    )
                    return [dict(row) for row in cur.fetchall()]
        else:
            with self._get_sqlite_conn() as conn:
                try:
                    cursor = conn.execute(
                        """SELECT id, title, created_at, updated_at, metadata 
                        FROM sessions 
                        ORDER BY updated_at DESC 
                        LIMIT ?""",
                        (limit,)
                    )
                    return [dict(row) for row in cursor.fetchall()]
                except Exception as e:
                    with open("db_query_error.log", "a") as f:
                        f.write(f"{datetime.now()}: List sessions error: {e}\n")
                    # Fallback for old schema if migration failed?
                    cursor = conn.execute(
                        """SELECT id, title, created_at, updated_at 
                        FROM sessions 
                        ORDER BY updated_at DESC 
                        LIMIT ?""",
                        (limit,)
                    )
                    results = []
                    for row in cursor.fetchall():
                        d = dict(row)
                        d['metadata'] = None # patch
                        results.append(d)
                    return results

    def update_title(self, session_id: str, title: str) -> None:
        """Update the title of a session.
        
        Args:
            session_id: Session ID.
            title: New title (will be truncated to 50 chars).
        """
        title = title[:50] if title else "New Chat"
        
        if self._is_postgres:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE sessions SET title = %s WHERE id = %s",
                        (title, session_id)
                    )
        else:
            with self._get_sqlite_conn() as conn:
                conn.execute(
                    "UPDATE sessions SET title = ? WHERE id = ?",
                    (title, session_id)
                )

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages.
        
        Args:
            session_id: Session ID to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        if not self.session_exists(session_id):
            return False
            
        if self._is_postgres:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
                    cur.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
        else:
            with self._get_sqlite_conn() as conn:
                conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        
        return True


    def get_session_subject(self, session_id: str) -> Optional[str]:
        """Get the subject for a session.
        
        Args:
            session_id: Session ID.
            
        Returns:
            Subject string or None.
        """
        import json
        metadata_json = None
        
        if self._is_postgres:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT metadata FROM sessions WHERE id = %s", (session_id,))
                    row = cur.fetchone()
                    if row:
                        metadata_json = row[0]
        else:
            with self._get_sqlite_conn() as conn:
                cursor = conn.execute(
                    "SELECT metadata FROM sessions WHERE id = ?", (session_id,)
                )
                row = cursor.fetchone()
                if row:
                    metadata_json = row[0]
                    
        if not metadata_json:
            return None
            
        if isinstance(metadata_json, str):
            try:
                metadata = json.loads(metadata_json)
            except json.JSONDecodeError:
                return None
        else:
            metadata = metadata_json
            
        return metadata.get("subject")

    def update_session_metadata(self, session_id: str, key: str, value: Any) -> bool:
        """Update a specific key in session metadata.
        
        Args:
            session_id: Session ID.
            key: Metadata key to update.
            value: New value.
            
        Returns:
            True if updated, False if session not found.
        """
        import json
        
        # 1. Get current metadata
        current_metadata = {}
        if self._is_postgres:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT metadata FROM sessions WHERE id = %s", (session_id,))
                    row = cur.fetchone()
                    if not row:
                        return False
                    current_metadata = row[0] if row[0] else {}
                    
                    # Update dict
                    if isinstance(current_metadata, str):
                        try:
                            current_metadata = json.loads(current_metadata)
                        except:
                            current_metadata = {}
                            
                    current_metadata[key] = value
                    
                    # Save back
                    cur.execute(
                        "UPDATE sessions SET metadata = %s, updated_at = NOW() WHERE id = %s",
                        (json.dumps(current_metadata), session_id)
                    )
        else:
            with self._get_sqlite_conn() as conn:
                cursor = conn.execute(
                    "SELECT metadata FROM sessions WHERE id = ?", (session_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return False
                current_metadata_json = row[0]
                
                try:
                    current_metadata = json.loads(current_metadata_json) if current_metadata_json else {}
                except:
                    current_metadata = {}
                    
                current_metadata[key] = value
                
                conn.execute(
                    "UPDATE sessions SET metadata = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (json.dumps(current_metadata), session_id)
                )
                
        return True

    def get_session_metadata(self, session_id: str) -> Dict[str, Any]:
        """Get full session metadata."""
        import json
        
        if self._is_postgres:
            import psycopg2
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT metadata FROM sessions WHERE id = %s", (session_id,))
                    row = cur.fetchone()
                    if not row:
                        return {}
                    meta = row[0]
                    if isinstance(meta, str):
                        try:
                            return json.loads(meta)
                        except:
                            return {}
                    return meta if meta else {}
        else:
            with self._get_sqlite_conn() as conn:
                cursor = conn.execute(
                    "SELECT metadata FROM sessions WHERE id = ?", (session_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return {}
                try:
                    return json.loads(row[0]) if row[0] else {}
                except:
                    return {}


# Singleton instance
_db_instance: Optional[ChatHistoryDB] = None


def get_db() -> ChatHistoryDB:
    """Get the database singleton."""
    global _db_instance
    if _db_instance is None:
        _db_instance = ChatHistoryDB()
    return _db_instance
