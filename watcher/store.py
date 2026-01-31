"""SQLite storage for job state."""

import sqlite3
from datetime import datetime
from typing import Dict, List

from watcher.models import Job


class JobStore:
    """Manages job state in SQLite database."""

    def __init__(self, db_path: str):
        """Initialize store with database path."""
        self.db_path = db_path
        self._init_db()

    def _close_connection(self):
        """Explicitly close and flush the database connection."""
        # Open and close to ensure all writes are flushed
        conn = sqlite3.connect(self.db_path)
        conn.commit()
        conn.close()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_key TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                city TEXT NOT NULL,
                date TEXT,
                day_of_week TEXT,
                time_range TEXT,
                duration_hours TEXT,
                wage_czk_per_h TEXT,
                raw_text TEXT NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL
            )
        """)
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN day_of_week TEXT")
        except sqlite3.OperationalError:
            pass  # column already exists (new DB or migrated)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_key TEXT NOT NULL,
                change_type TEXT NOT NULL,
                notified_at TIMESTAMP NOT NULL,
                FOREIGN KEY (job_key) REFERENCES jobs(job_key)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_job_key 
            ON notifications(job_key)
        """)
        conn.commit()
        conn.close()

    def upsert_jobs(self, jobs: List[Job]) -> None:
        """Insert or update jobs in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.utcnow()

        for job in jobs:
            if not job.job_key:
                job.job_key = job.compute_key()

            # Check if job exists
            cursor.execute("SELECT first_seen FROM jobs WHERE job_key = ?", (job.job_key,))
            row = cursor.fetchone()

            if row:
                # Update existing job
                cursor.execute("""
                    UPDATE jobs SET
                        title = ?,
                        city = ?,
                        date = ?,
                        day_of_week = ?,
                        time_range = ?,
                        duration_hours = ?,
                        wage_czk_per_h = ?,
                        raw_text = ?,
                        last_seen = ?
                    WHERE job_key = ?
                """, (
                    job.title,
                    job.city,
                    job.date,
                    job.day_of_week or "",
                    job.time_range,
                    job.duration_hours,
                    job.wage_czk_per_h,
                    job.raw_text,
                    now,
                    job.job_key,
                ))
            else:
                # Insert new job
                cursor.execute("""
                    INSERT INTO jobs (
                        job_key, title, city, date, day_of_week, time_range,
                        duration_hours, wage_czk_per_h, raw_text,
                        first_seen, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.job_key,
                    job.title,
                    job.city,
                    job.date,
                    job.day_of_week or "",
                    job.time_range,
                    job.duration_hours,
                    job.wage_czk_per_h,
                    job.raw_text,
                    now,
                    now,
                ))

        conn.commit()
        conn.close()

    def get_all_jobs(self) -> Dict[str, Job]:
        """Retrieve all jobs from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()

        jobs = {}
        for row in rows:
            # Parse timestamps from SQLite (stored as ISO format strings)
            first_seen = None
            last_seen = None
            if row["first_seen"]:
                try:
                    first_seen = datetime.fromisoformat(row["first_seen"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass
            if row["last_seen"]:
                try:
                    last_seen = datetime.fromisoformat(row["last_seen"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            job = Job(
                job_key=row["job_key"],
                title=row["title"],
                city=row["city"],
                date=row["date"] or "",
                day_of_week=row["day_of_week"] if row["day_of_week"] else "",
                time_range=row["time_range"] or "",
                duration_hours=row["duration_hours"] or "",
                wage_czk_per_h=row["wage_czk_per_h"] or "",
                raw_text=row["raw_text"],
                first_seen=first_seen,
                last_seen=last_seen,
            )
            jobs[job.job_key] = job

        conn.close()
        return jobs

    def mark_notified(self, job_key: str, change_type: str) -> None:
        """Mark that a notification was sent for a job change."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (job_key, change_type, notified_at)
            VALUES (?, ?, ?)
        """, (job_key, change_type, datetime.utcnow()))
        conn.commit()
        conn.close()

    def was_notified(self, job_key: str, change_type: str) -> bool:
        """Check if a notification was already sent for this change."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM notifications
            WHERE job_key = ? AND change_type = ?
        """, (job_key, change_type))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
