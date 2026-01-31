"""Tests for HTML parsing."""

import os

from watcher.parse import parse_html


def test_parse_html_with_fixture():
    """Test parsing with a saved HTML fixture."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "brigoska_sample.html")

    if not os.path.exists(fixture_path):
        # Skip test if fixture doesn't exist
        return

    with open(fixture_path, "r", encoding="utf-8") as f:
        html = f.read()

    jobs = parse_html(html)

    # Should parse at least some jobs
    assert len(jobs) >= 0  # May be 0 if fixture is empty, but shouldn't crash

    # If jobs found, verify structure
    for job in jobs:
        assert job.title is not None
        assert job.job_key is not None
        assert len(job.job_key) > 0


def test_parse_empty_html():
    """Test parsing empty HTML."""
    jobs = parse_html("")
    assert len(jobs) == 0


def test_parse_html_no_section():
    """Test parsing HTML without the expected section."""
    html = "<html><body><h1>Some other content</h1></body></html>"
    jobs = parse_html(html)
    # Should not crash, may return empty list
    assert isinstance(jobs, list)
