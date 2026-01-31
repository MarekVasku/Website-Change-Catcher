"""Data models for job listings."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    """Represents a job listing."""

    title: str
    city: str
    date: str
    day_of_week: str
    time_range: str
    duration_hours: str
    wage_czk_per_h: str
    raw_text: str
    job_key: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    def normalize_text(self) -> str:
        """Normalize text for key generation."""
        import re
        text = f"{self.title} {self.city} {self.date} {self.day_of_week} {self.time_range} {self.wage_czk_per_h}"
        # Remove NBSP and normalize whitespace
        text = text.replace("\u00a0", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def compute_key(self) -> str:
        """Compute stable key for this job.
        comment"""
        import hashlib
        normalized = self.normalize_text()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
