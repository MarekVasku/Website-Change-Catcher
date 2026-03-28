"""Parse HTML to extract job listings."""

import re
from typing import List, Optional

from selectolax.parser import HTMLParser

from watcher.models import Job


def parse_html(html: str) -> List[Job]:
    """
    Parse brigoska.cz HTML and extract job listings.

    Only returns valid job rows with date, time, duration, and wage.
    """
    parser = HTMLParser(html)
    jobs = []

    # Pattern to match job rows: must have bullet, date, time, duration, and wage
    job_pattern = re.compile(
        r"».*\d{1,2}\.\d{1,2}\.\d{4}.*\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}.*\(\d+(?:\.\d+)?\s*h\).*\d+\s*Kč"
    )

    for tr in parser.tags("tr"):
        text = tr.text(separator=" ", strip=True) if tr else ""
        if not text or "»" not in text or not re.search(r"\d+\s*Kč\s*/?\s*h", text, re.I):
            continue
        if not job_pattern.search(text):
            continue

        job = _parse_job_row(tr)
        if job and _is_valid_job(job):
            jobs.append(job)

    return jobs


def _is_valid_job(job: Job) -> bool:
    """Check if job has all required fields and is a weekend job."""
    day = (job.day_of_week or "").strip().lower()
    is_weekend = day in {"so", "ne"}
    return bool(
        job.wage_czk_per_h
        and job.date
        and job.time_range
        and job.duration_hours
        and is_weekend
    )


def _parse_job_row(row) -> Optional[Job]:
    """Parse a job row from the HTML table."""
    raw_text = row.text(separator=" ", strip=True)
    if not raw_text or len(raw_text) < 10:
        return None

    raw_text = re.sub(r"\s+", " ", raw_text).strip()

    # Extract date and day of week (Czech: Po, Út, St, Čt, Pá, So, Ne)
    date = ""
    day_of_week = ""
    date_match = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})\s+(Po|Út|St|Čt|Pá|So|Ne)\b", raw_text)
    if date_match:
        date = date_match.group(1)
        day_of_week = date_match.group(2)
    else:
        plain_date = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", raw_text)
        if plain_date:
            date = plain_date.group(1)

    # Extract time range (HH:MM - HH:MM)
    time_range = ""
    if date:
        time_match = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", raw_text)
        if time_match:
            time_range = f"{time_match.group(1)} - {time_match.group(2)}"

    # Extract duration (Nh)
    duration_hours = ""
    duration_match = re.search(r"\((\d+(?:\.\d+)?)\s*h\)", raw_text)
    if duration_match:
        duration_hours = duration_match.group(1)

    # Extract wage (NNN Kč/h)
    wage_czk_per_h = ""
    wage_match = re.search(r"(\d+)\s*Kč\s*/?\s*h", raw_text, re.IGNORECASE)
    if wage_match:
        wage_czk_per_h = f"{wage_match.group(1)} Kč/h"

    # Extract title and city
    title = ""
    city = ""
    parts = raw_text.split()
    if parts:
        # Find index of first date pattern in parts list
        date_idx = next((i for i, part in enumerate(parts) if re.match(r"\d{1,2}\.\d{1,2}\.\d{4}", part)), -1)

        if date_idx > 0:
            # Everything before date is title + city
            before_date = " ".join(parts[:date_idx]).lstrip("» ").strip()

            # Try to find Czech city names
            city_keywords = [
                "Praha", "Brno", "Ostrava", "Plzeň", "Liberec", "Olomouc",
                "České Budějovice", "Hradec Králové", "Ústí nad Labem",
                "Pardubice", "Zlín", "Havířov", "Kladno", "Most", "Opava",
                "Frýdek-Místek", "Karlovy Vary", "Jihlava", "Teplice",
            ]
            for keyword in city_keywords:
                if keyword in before_date:
                    city_idx = before_date.find(keyword)
                    title = before_date[:city_idx].strip()
                    city = before_date[city_idx:].strip()
                    break

            # Fallback: last word is city, rest is title
            if not city:
                words = before_date.split()
                if len(words) > 1:
                    city = words[-1]
                    title = " ".join(words[:-1])
                else:
                    title = before_date

    if not title:
        title = raw_text[:100]

    job = Job(
        title=title or "Unknown",
        city=city or "Unknown",
        date=date or "",
        day_of_week=day_of_week or "",
        time_range=time_range or "",
        duration_hours=duration_hours or "",
        wage_czk_per_h=wage_czk_per_h or "",
        raw_text=raw_text,
    )
    job.job_key = job.compute_key()

    return job
