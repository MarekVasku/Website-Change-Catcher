"""Email notification via SMTP."""

import os
import smtplib
from email.mime.text import MIMEText

from watcher.diff import JobDiff


def send_notification(diff: JobDiff, url: str) -> bool:
    """
    Send email notification about job changes.

    Args:
        diff: JobDiff object with changes
        url: URL being monitored

    Returns:
        True if email was sent successfully, False otherwise
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO", "")

    if not all([smtp_host, smtp_user, smtp_pass, email_from, email_to]):
        return False

    # Build email body
    body_parts = []

    if diff.new:
        body_parts.append("=== NEW JOBS ===\n")
        for job in diff.new:
            body_parts.append(f"Title: {job.title}")
            body_parts.append(f"Location: {job.city}")
            body_parts.append(f"Date: {job.date}")
            body_parts.append(f"Day of week: {getattr(job, 'day_of_week', '') or '-'}")
            body_parts.append(f"Time: {job.time_range}")
            body_parts.append(f"Duration: {job.duration_hours}h")
            body_parts.append(f"Wage: {job.wage_czk_per_h}")
            body_parts.append(f"Raw: {job.raw_text[:200]}")
            body_parts.append("")

    if diff.removed:
        body_parts.append("=== REMOVED JOBS ===\n")
        for job in diff.removed:
            body_parts.append(f"Title: {job.title}")
            body_parts.append(f"Location: {job.city}")
            body_parts.append(f"Date: {job.date}")
            body_parts.append(f"Day of week: {getattr(job, 'day_of_week', '') or '-'}")
            body_parts.append(f"Time: {job.time_range}")
            body_parts.append(f"Wage: {job.wage_czk_per_h}")
            body_parts.append("")

    if diff.changed:
        body_parts.append("=== CHANGED JOBS ===\n")
        for old_job, new_job in diff.changed:
            body_parts.append(f"Title: {old_job.title} -> {new_job.title}")
            body_parts.append(f"Location: {old_job.city} -> {new_job.city}")
            body_parts.append(f"Date: {old_job.date} -> {new_job.date}")
            old_dow = getattr(old_job, 'day_of_week', '') or '-'
            new_dow = getattr(new_job, 'day_of_week', '') or '-'
            body_parts.append(f"Day of week: {old_dow} -> {new_dow}")
            body_parts.append(f"Time: {old_job.time_range} -> {new_job.time_range}")
            body_parts.append(f"Duration: {old_job.duration_hours}h -> {new_job.duration_hours}h")
            body_parts.append(f"Wage: {old_job.wage_czk_per_h} -> {new_job.wage_czk_per_h}")
            body_parts.append("")

    if not body_parts:
        return False  # No changes to notify

    # Add footer
    from datetime import datetime
    body_parts.append(f"\n---\nChecked at: {datetime.now().isoformat()}")
    body_parts.append(f"URL: {url}")

    body = "\n".join(body_parts)

    # Build subject
    subject = (
        f"[Website Change Catcher] Update: "
        f"+{len(diff.new)} new / "
        f"-{len(diff.removed)} removed / "
        f"~{len(diff.changed)} changed"
    )

    # Parse comma-separated recipients
    recipients = [addr.strip() for addr in email_to.split(",") if addr.strip()]

    # Create message
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = ", ".join(recipients)

    # Send email (strip spaces from app password)
    smtp_pass = smtp_pass.replace(" ", "")
    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(email_from, recipients, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(email_from, recipients, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
