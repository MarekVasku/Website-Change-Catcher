"""Compare old and new job sets."""

from typing import Dict, List, Tuple

from watcher.models import Job


class JobDiff:
    """Changes between job sets."""

    def __init__(self):
        self.new: List[Job] = []
        self.removed: List[Job] = []
        self.changed: List[Tuple[Job, Job]] = []  # (old, new)


def compute_diff(old_jobs: Dict[str, Job], new_jobs: Dict[str, Job]) -> JobDiff:
    """Find what's new, removed, or changed between job sets."""
    diff = JobDiff()

    old_keys = set(old_jobs.keys())
    new_keys = set(new_jobs.keys())

    # New jobs
    for key in new_keys - old_keys:
        diff.new.append(new_jobs[key])

    # Removed jobs
    for key in old_keys - new_keys:
        diff.removed.append(old_jobs[key])

    # Changed jobs (same key but different content)
    for key in old_keys & new_keys:
        old_job = old_jobs[key]
        new_job = new_jobs[key]

        old_dow = getattr(old_job, "day_of_week", "") or ""
        new_dow = getattr(new_job, "day_of_week", "") or ""

        if (
            old_job.title != new_job.title
            or old_job.city != new_job.city
            or old_job.date != new_job.date
            or old_dow != new_dow
            or old_job.time_range != new_job.time_range
            or old_job.duration_hours != new_job.duration_hours
            or old_job.wage_czk_per_h != new_job.wage_czk_per_h
        ):
            diff.changed.append((old_job, new_job))

    return diff
