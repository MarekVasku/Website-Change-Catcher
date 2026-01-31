# Release Notes

## v1.0.0 — First Stable Release

**Release Date:** January 31, 2026

### Summary
First stable release of Website Change Catcher — a small, reliable monitor that checks brigoska.cz and sends email notifications for new job postings.

### Highlights
- ✅ Scheduled checks every 30 minutes via GitHub Actions (UTC)
- ✅ Email notifications for newly discovered job listings
- ✅ State persistence across runs using GitHub Actions cache to avoid duplicate notifications
- ✅ Robust fetch with retries and anti-bot headers
- ✅ HTML parsing tuned for brigoska.cz job table
- ✅ SQLite-backed store with notification de-duplication
- ✅ Test suite included — all tests passing

### What's New

#### Code Quality & Refactoring
- Production-ready refactor: removed debug prints and unused code
- Simplified day_of_week access in store.py
- Removed unused `_connection` attribute from JobStore
- Cleaned up malformed code structures

#### Bug Fixes
- Fixed duplicate-notification bug by persisting state and updating DB before notification filtering
- Added explicit DB flush/close to ensure state is saved before CI cache save

#### CI/CD Improvements
- Replaced `pylint` with `ruff` for faster linting (0.14.14)
- Workflow now triggers on:
  - Every 30 minutes (scheduled)
  - Push to `main` (for testing)
  - Manual `workflow_dispatch`
- Documented cron alternatives in workflow comments
- Switched from artifacts to cache for state persistence

### Usage

#### Setup
Configure repository secrets in Repository → Settings → Secrets:
```
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASS
EMAIL_FROM
EMAIL_TO
```

#### Run Locally
```bash
uv pip install --system -e .
uv run python -m watcher --once
```

#### How It Works
1. **fetch**: Download HTML from brigoska.cz with retries and anti-bot headers
2. **parse**: Extract job listings from HTML table
3. **diff**: Compare with previous state (new/removed/changed jobs)
4. **notify**: Send email for NEW jobs only
5. **store**: Save state to SQLite; persist via GitHub Actions cache

### Technical Details

**Architecture:**
- Entry: `watcher/cli.py` (Typer CLI)
- Fetch: `watcher/fetch.py` (httpx with backoff)
- Parse: `watcher/parse.py` (selectolax)
- Diff: `watcher/diff.py` (change detection)
- Notify: `watcher/notify.py` (SMTP email)
- Store: `watcher/store.py` (SQLite + notification de-dupe)
- Models: `watcher/models.py` (Job dataclass with stable key generation)

**Dependencies:**
- Python 3.11 (constrained: `>=3.11,<3.12`)
- httpx, selectolax, typer, python-dotenv, pytest, ruff

**Testing:**
- Unit tests for diff, models, parsing
- Fixture-based HTML parsing tests
- Run: `uv run pytest tests/ -v`

### Upgrade Guide

If coming from an earlier version:

1. Pull latest: `git pull origin main`
2. Ensure secrets are set in GitHub repository settings
3. The workflow now runs on push — push the latest code to test immediately
4. State persists via cache; no action needed

### Known Limitations

- Monitors only brigoska.cz (hardcoded in parser)
- SMTP only; no other notification channels
- Email deduplication per job per change type (new/removed/changed)

### Notes for Operators

- **Timezone:** Cron uses UTC. Edit `.github/workflows/watcher.yml` to change schedule.
- **Testing:** Push to `main` to trigger an immediate run.
- **Manual run:** Click "Run workflow" in GitHub Actions → "watcher" → Run.
- **State:** `state.db` is cached per run and restored on the next job.

### Checklist for Release

- [x] All tests passing
- [x] Refactored and cleaned
- [x] Workflow tested on push
- [x] State persistence working (cache-based)
- [x] No duplicate notifications on consecutive runs
- [x] Production-ready

### Future Enhancements

- [ ] Support multiple job boards (config-driven parsing)
- [ ] Webhook notifications (Discord, Slack, etc.)
- [ ] Web UI dashboard for viewing jobs
- [ ] SMS notifications

---

**Questions?** Check the README or open an issue on GitHub.
