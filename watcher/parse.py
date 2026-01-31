"""HTML parsing to extract job listings."""

import re
from typing import List, Optional

from selectolax.parser import HTMLParser

from watcher.models import Job


def parse_html(html: str) -> List[Job]:
    """
    Parse HTML and extract job listings from the brigoska.cz jobs table.

    Only extracts actual job rows: must have date, time, duration, and wage.
    """
    parser = HTMLParser(html)
    jobs = []

    # Target table rows that look like job listings:
    # Must contain » (bullet), date pattern, and wage (e.g. "181 Kč/h")
    job_row_pattern = re.compile(
        r"».*\d{1,2}\.\d{1,2}\.\d{4}.*\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}.*\(\d+(?:\.\d+)?\s*h\).*\d+\s*Kč"
    )

    for tr in parser.tags("tr"):
        text = tr.text(separator=" ", strip=True) if tr else ""
        if not text or "»" not in text or not re.search(r"\d+\s*Kč\s*/?\s*h", text, re.I):
            continue
        if not job_row_pattern.search(text):
            continue

        job = _parse_job_container(tr)
        if job and _is_valid_job(job):
            jobs.append(job)

    return jobs


def _is_valid_job(job: Job) -> bool:
    """Only include jobs with all required fields (filters out noise)."""
    return bool(
        job.wage_czk_per_h
        and job.date
        and job.time_range
        and job.duration_hours
    )


def _parse_job_container(container) -> Optional[Job]:
    """Parse a single job container element."""
    raw_text = container.text(separator=" ", strip=True)
    if not raw_text or len(raw_text) < 10:
        return None

    # Normalize whitespace
    raw_text = re.sub(r"\s+", " ", raw_text).strip()

    # Try to extract structured fields
    # Pattern: title, location, date/time, wage
    # Example: "Název práce Praha 26.1.2026 Po 06:00 - 14:00 (8h) 180 Kč/h"

    title = ""
    city = ""
    date = ""
    day_of_week = ""
    time_range = ""
    duration_hours = ""
    wage_czk_per_h = ""

    # Extract date and day of week (Czech abbrev: Po, Út, St, Čt, Pá, So, Ne)
    date_match = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})\s+(Po|Út|St|Čt|Pá|So|Ne)\b", raw_text)
    if date_match:
        date = date_match.group(1)
        day_of_week = date_match.group(2)
    else:
        plain_date = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", raw_text)
        if plain_date:
            date = plain_date.group(1)
    if date:
        # Extract time range: HH:MM - HH:MM
        time_match = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", raw_text)
        if time_match:
            time_range = f"{time_match.group(1)} - {time_match.group(2)}"
        # Extract duration: (Nh) or (N h)
        duration_match = re.search(r"\((\d+(?:\.\d+)?)\s*h\)", raw_text)
        if duration_match:
            duration_hours = duration_match.group(1)

    # Extract wage: NNN Kč/h or NNN Kč/h
    wage_match = re.search(r"(\d+)\s*Kč\s*/?\s*h", raw_text, re.IGNORECASE)
    if wage_match:
        wage_czk_per_h = f"{wage_match.group(1)} Kč/h"

    # Try to split title and city
    # Usually the first part is title, second might be city
    parts = raw_text.split()
    if parts:
        # Find where date starts
        date_idx = -1
        for i, part in enumerate(parts):
            if re.match(r"\d{1,2}\.\d{1,2}\.\d{4}", part):
                date_idx = i
                break

        if date_idx > 0:
            # Everything before date is likely title + city (strip » bullet)
            before_date = " ".join(parts[:date_idx]).lstrip("» ").strip()
            # Try to identify city (common Czech cities or location words)
            city_keywords = [
                "Praha", "Brno", "Ostrava", "Plzeň", "Liberec", "Olomouc",
                "České Budějovice", "Hradec Králové", "Ústí nad Labem",
                "Pardubice", "Zlín", "Havířov", "Kladno", "Most", "Opava",
                "Frýdek-Místek", "Karlovy Vary", "Jihlava", "Teplice",
            ]
            for keyword in city_keywords:
                if keyword in before_date:
                    # Split on city
                    city_idx = before_date.find(keyword)
                    title = before_date[:city_idx].strip()
                    city = before_date[city_idx:].strip()
                    break

            if not city:
                # Fallback: assume last word before date is city, rest is title
                words = before_date.split()
                if len(words) > 1:
                    city = words[-1]
                    title = " ".join(words[:-1])
                else:
                    title = before_date

    # If we couldn't parse, use raw text as title
    if not title:
        title = raw_text[:100]  # Limit length

    # Create job object
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
