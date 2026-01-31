# Website Change Catcher – AI coding guide

## Big picture
- Entry point is the Typer CLI in watcher/cli.py, invoked via python -m watcher (watcher/__main__.py).
- Core pipeline is fetch → parse → diff → notify → store:
  - fetch: watcher/fetch.py (httpx client with headers/retries/backoff)
  - parse: watcher/parse.py (selectolax HTML parsing for brigoska.cz job table)
  - diff: watcher/diff.py (JobDiff with new/removed/changed)
  - notify: watcher/notify.py (SMTP email from env vars)
  - store: watcher/store.py (SQLite state + notification de-dupe)

## Data model + identity
- Job is a dataclass in watcher/models.py. Identity is a stable key from normalized text.
- compute_key() hashes: title + city + date + day_of_week + time_range + wage; normalization collapses whitespace and removes NBSP.
- If adding fields, update normalize_text(), diff comparison, and store schema/queries to keep keys stable.

## Parsing conventions (project-specific)
- parse_html() is tuned for brigoska.cz: looks for “»” bullet, date/time pattern, and Kč/h wage.
- _parse_job_container() uses Czech day-of-week abbreviations (Po, Út, St, Čt, Pá, So, Ne) and city heuristics.
- Keep filters strict to avoid noise; tests in tests/test_parse.py are minimal by design.

## Persistence + de-dup
- SQLite file path is controlled by STATE_DB_PATH (default ./state.db).
- Notifications are de-duplicated via notifications table; cli.py filters out already-notified changes.
- Store migration is handled in JobStore._init_db() with ALTER TABLE for day_of_week.

## Developer workflows
- Install: uv venv && source .venv/bin/activate && uv pip install -e " .[dev]" (see README.md).
- Run once: uv run python -m watcher --once
- Run continuously: uv run python -m watcher
- Tests: uv run pytest

## Environment configuration
- .env is loaded from project root by watcher/cli.py via python-dotenv.
- Required SMTP vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO.

## Integration points
- External deps: httpx (HTTP), selectolax (HTML parsing), typer (CLI), python-dotenv (env loading).
- Email transport uses SMTP/STARTTLS (watcher/notify.py). Use port 465 for SSL.