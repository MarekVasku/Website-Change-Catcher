"""Tests for job models and key generation."""

from watcher.models import Job


def test_job_normalization():
    """Test text normalization for key generation."""
    job1 = Job(
        title="Test Job",
        city="Praha",
        date="26.1.2026",
        day_of_week="Po",
        time_range="06:00 - 14:00",
        duration_hours="8",
        wage_czk_per_h="180 Kč/h",
        raw_text="Test Job Praha 26.1.2026 Po 06:00 - 14:00 (8h) 180 Kč/h",
    )

    job2 = Job(
        title="Test  Job",  # Extra space
        city="Praha",
        date="26.1.2026",
        day_of_week="Po",
        time_range="06:00 - 14:00",
        duration_hours="8",
        wage_czk_per_h="180 Kč/h",
        raw_text="Test  Job Praha 26.1.2026 Po 06:00 - 14:00 (8h) 180 Kč/h",
    )

    # Same jobs should have same key
    key1 = job1.compute_key()
    key2 = job2.compute_key()
    assert key1 == key2


def test_job_key_stability():
    """Test that job keys are stable across calls."""
    job = Job(
        title="Warehouse Worker",
        city="Brno",
        date="15.2.2026",
        day_of_week="Po",
        time_range="08:00 - 16:00",
        duration_hours="8",
        wage_czk_per_h="200 Kč/h",
        raw_text="Warehouse Worker Brno 15.2.2026 Po 08:00 - 16:00 (8h) 200 Kč/h",
    )

    key1 = job.compute_key()
    key2 = job.compute_key()
    assert key1 == key2
    assert len(key1) == 16  # First 16 chars of SHA256


def test_job_key_different_jobs():
    """Test that different jobs have different keys."""
    job1 = Job(
        title="Job A",
        city="Praha",
        date="26.1.2026",
        day_of_week="Po",
        time_range="06:00 - 14:00",
        duration_hours="8",
        wage_czk_per_h="180 Kč/h",
        raw_text="Job A Praha 26.1.2026 Po 06:00 - 14:00 (8h) 180 Kč/h",
    )

    job2 = Job(
        title="Job B",
        city="Praha",
        date="26.1.2026",
        day_of_week="Po",
        time_range="06:00 - 14:00",
        duration_hours="8",
        wage_czk_per_h="180 Kč/h",
        raw_text="Job B Praha 26.1.2026 Po 06:00 - 14:00 (8h) 180 Kč/h",
    )

    key1 = job1.compute_key()
    key2 = job2.compute_key()
    assert key1 != key2
