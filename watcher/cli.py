"""CLI interface for the watcher."""

import os
import sys
import time
from pathlib import Path

import typer
from dotenv import load_dotenv

from watcher.diff import compute_diff
from watcher.fetch import fetch_url
from watcher.notify import send_notification
from watcher.parse import parse_html
from watcher.store import JobStore

# Load .env from project root (not shared, in .gitignore)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = typer.Typer(invoke_without_command=True)


def get_config() -> dict:
    """Load configuration from environment variables."""
    return {
        "watch_url": os.getenv("WATCH_URL", "https://brigoska.cz/cs/mista"),
        "check_interval_minutes": int(os.getenv("CHECK_INTERVAL_MINUTES", "30")),
        "state_db_path": os.getenv("STATE_DB_PATH", "./state.db"),
    }


@app.callback()
def main(
    ctx: typer.Context,
    once: bool = typer.Option(False, "--once", help="Run once and exit"),
):
    """Run the watcher service."""
    if ctx.invoked_subcommand is not None:
        return
    config = get_config()
    store = JobStore(config["state_db_path"])

    def check_once() -> bool:
        """Perform a single check cycle. Returns True if changes were found."""
        print(f"Fetching {config['watch_url']}...")
        html = fetch_url(config["watch_url"])

        if not html:
            print("ERROR: Failed to fetch URL. Skipping update.")
            return False

        print("Parsing HTML...")
        new_jobs_list = parse_html(html)
        print(f"Found {len(new_jobs_list)} job listings")

        # Convert to dict keyed by job_key
        new_jobs = {}
        for job in new_jobs_list:
            if not job.job_key:
                job.job_key = job.compute_key()
            new_jobs[job.job_key] = job

        # Get old jobs
        old_jobs = store.get_all_jobs()

        # Compute diff
        diff = compute_diff(old_jobs, new_jobs)

        # Update store with new jobs FIRST (before filtering notifications)
        store.upsert_jobs(new_jobs_list)

        # Filter out already-notified changes
        new_to_notify = [j for j in diff.new if not store.was_notified(j.job_key, "new")]
        removed_to_notify = [j for j in diff.removed if not store.was_notified(j.job_key, "removed")]
        changed_to_notify = [
            (old, new)
            for old, new in diff.changed
            if not store.was_notified(new.job_key, "changed")
        ]

        # Create filtered diff
        filtered_diff = type(diff)()
        filtered_diff.new = new_to_notify
        filtered_diff.removed = removed_to_notify
        filtered_diff.changed = changed_to_notify

        # Print summary
        print(f"Changes detected: +{len(diff.new)} new, -{len(diff.removed)} removed, ~{len(diff.changed)} changed")
        print(
            f"To notify: +{len(new_to_notify)} new, "
            f"-{len(removed_to_notify)} removed, ~{len(changed_to_notify)} changed"
        )

        # Send notification only for NEW jobs
        if new_to_notify:
            # Create a diff with only new jobs for the email
            new_only_diff = type(diff)()
            new_only_diff.new = new_to_notify
            new_only_diff.removed = []
            new_only_diff.changed = []
            print("Sending email notification for new jobs...")
            if send_notification(new_only_diff, config["watch_url"]):
                print("Email sent successfully")

                # Mark as notified
                for job in new_to_notify:
                    store.mark_notified(job.job_key, "new")
            else:
                print("ERROR: Failed to send email")
        else:
            print("No new jobs to notify")
        # Mark removed/changed as notified without sending email
        for job in removed_to_notify:
            store.mark_notified(job.job_key, "removed")
        for old, new in changed_to_notify:
            store.mark_notified(new.job_key, "changed")

        return len(new_to_notify) > 0 or len(removed_to_notify) > 0 or len(changed_to_notify) > 0

    if once:
        check_once()
        store._close_connection()
    else:
        while True:
            try:
                check_once()
                print(f"Waiting {config['check_interval_minutes']} minutes until next check...")
                time.sleep(config["check_interval_minutes"] * 60)
            except KeyboardInterrupt:
                print("\nStopping watcher...")
                sys.exit(0)


if __name__ == "__main__":
    app()
