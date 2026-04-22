# Made by Yodahe Wondimu
# Provides methods to insert events and summarize stored data.

import os
import sqlite3
import threading
from datetime import datetime, timezone

class Storage:
    def __init__(self, db_path = os.path.join(os.path.dirname(__file__), "filefly.db")):
        print("USING DATABASE AT:", os.path.abspath(db_path))
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                event_type TEXT,
                extension TEXT,
                size INTEGER,
                stabilization_time REAL,
                processing_time REAL,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def insert_event(self, path, event_type, extension, size, stabilization_time, processing_time=None):
        with self.lock:
            self.conn.execute("""
                INSERT INTO events 
                (path, event_type, extension, size, stabilization_time, processing_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                path,
                event_type,
                extension,
                size,
                stabilization_time,
                processing_time,
                datetime.now(timezone.utc).isoformat()
            ))
            self.conn.commit()

    def summary(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM events")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT extension, COUNT(*)
            FROM events
            GROUP BY extension
            ORDER BY COUNT(*) DESC
        """)
        ext_counts = cursor.fetchall()

        cursor.execute("""
            SELECT event_type, COUNT(*)
            FROM events
            GROUP BY event_type
            ORDER BY COUNT(*) DESC
        """)
        event_counts = cursor.fetchall()

        cursor.execute("""
            SELECT extension, AVG(stabilization_time)
            FROM events
            GROUP BY extension
        """)
        avg_stab_by_ext = cursor.fetchall()

        cursor.execute("""
            SELECT AVG(stabilization_time)
            FROM events
        """)
        avg_stab_total = cursor.fetchall()

        return {
            "total_events": total,
            "extension_counts": ext_counts,
            "event_counts": event_counts,
            "avg_stabilization_by_extension": avg_stab_by_ext,
            "avg_stabilization_total": avg_stab_total
        }