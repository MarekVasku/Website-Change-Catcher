"""Job listing data."""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    """A job listing with all its details."""

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
        """Clean up whitespace and special chars for consistent key generation."""
        text = f"{self.title} {self.city} {self.date} {self.day_of_week} {self.time_range} {self.wage_czk_per_h}"
        text = text.replace("\u00a0", " ")  # Replace non-breaking spaces
        text = re.sub(r"\s+", " ", text)     # Collapse whitespace
        return text.strip()

    def compute_key(self) -> str:
        """Generate a unique key from the job details."""
        normalized = self.normalize_text()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
