"""Tests for diff logic."""

from watcher.diff import compute_diff
from watcher.models import Job


def test_diff_new_jobs():
    """Test detection of new jobs."""
    old_jobs = {}
    new_jobs = {
        "key1": Job(
            title="Job 1",
            city="Praha",
            date="26.1.2026",
            day_of_week="Po",
            time_range="06:00 - 14:00",
            duration_hours="8",
            wage_czk_per_h="180 Kč/h",
            raw_text="Job 1",
            job_key="key1",
        )
    }

    diff = compute_diff(old_jobs, new_jobs)
    assert len(diff.new) == 1
    assert len(diff.removed) == 0
    assert len(diff.changed) == 0
    assert diff.new[0].job_key == "key1"


def test_diff_removed_jobs():
    """Test detection of removed jobs."""
    old_jobs = {
        "key1": Job(
            title="Job 1",
            city="Praha",
            date="26.1.2026",
            day_of_week="Po",
            time_range="06:00 - 14:00",
            duration_hours="8",
            wage_czk_per_h="180 Kč/h",
            raw_text="Job 1",
            job_key="key1",
        )
    }
    new_jobs = {}

    diff = compute_diff(old_jobs, new_jobs)
    assert len(diff.new) == 0
    assert len(diff.removed) == 1
    assert len(diff.changed) == 0
    assert diff.removed[0].job_key == "key1"


def test_diff_changed_jobs():
    """Test detection of changed jobs."""
    old_jobs = {
        "key1": Job(
            title="Job 1",
            city="Praha",
            date="26.1.2026",
            day_of_week="Po",
            time_range="06:00 - 14:00",
            duration_hours="8",
            wage_czk_per_h="180 Kč/h",
            raw_text="Job 1",
            job_key="key1",
        )
    }
    new_jobs = {
        "key1": Job(
            title="Job 1 Updated",
            city="Praha",
            date="26.1.2026",
            day_of_week="Po",
            time_range="06:00 - 14:00",
            duration_hours="8",
            wage_czk_per_h="180 Kč/h",
            raw_text="Job 1 Updated",
            job_key="key1",
        )
    }

    diff = compute_diff(old_jobs, new_jobs)
    assert len(diff.new) == 0
    assert len(diff.removed) == 0
    assert len(diff.changed) == 1
    assert diff.changed[0][0].title == "Job 1"
    assert diff.changed[0][1].title == "Job 1 Updated"


def test_diff_no_changes():
    """Test that identical jobs produce no diff."""
    job = Job(
        title="Job 1",
        city="Praha",
        date="26.1.2026",
        day_of_week="Po",
        time_range="06:00 - 14:00",
        duration_hours="8",
        wage_czk_per_h="180 Kč/h",
        raw_text="Job 1",
        job_key="key1",
    )

    old_jobs = {"key1": job}
    new_jobs = {"key1": job}

    diff = compute_diff(old_jobs, new_jobs)
    assert len(diff.new) == 0
    assert len(diff.removed) == 0
    assert len(diff.changed) == 0


def test_diff_mixed_changes():
    """Test diff with new, removed, and changed jobs."""
    old_jobs = {
        "key1": Job(
            title="Job 1",
            city="Praha",
            date="26.1.2026",
            day_of_week="Po",
            time_range="06:00 - 14:00",
            duration_hours="8",
            wage_czk_per_h="180 Kč/h",
            raw_text="Job 1",
            job_key="key1",
        ),
        "key2": Job(
            title="Job 2",
            city="Brno",
            date="27.1.2026",
            day_of_week="Út",
            time_range="08:00 - 16:00",
            duration_hours="8",
            wage_czk_per_h="200 Kč/h",
            raw_text="Job 2",
            job_key="key2",
        ),
    }

    new_jobs = {
        "key1": Job(
            title="Job 1 Updated",
            city="Praha",
            date="26.1.2026",
            day_of_week="Po",
            time_range="06:00 - 14:00",
            duration_hours="8",
            wage_czk_per_h="180 Kč/h",
            raw_text="Job 1 Updated",
            job_key="key1",
        ),
        "key3": Job(
            title="Job 3",
            city="Ostrava",
            date="28.1.2026",
            day_of_week="St",
            time_range="10:00 - 18:00",
            duration_hours="8",
            wage_czk_per_h="190 Kč/h",
            raw_text="Job 3",
            job_key="key3",
        ),
    }

    diff = compute_diff(old_jobs, new_jobs)
    assert len(diff.new) == 1
    assert len(diff.removed) == 1
    assert len(diff.changed) == 1
    assert diff.new[0].job_key == "key3"
    assert diff.removed[0].job_key == "key2"
    assert diff.changed[0][0].job_key == "key1"
