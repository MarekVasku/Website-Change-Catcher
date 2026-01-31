# Website Change Catcher – AI coding guide

## Big picture
- Entry point is the Typer CLI in watcher/cli.py, invoked via `python -m watcher` (watcher/__main__.py).
- Core pipeline is fetch → parse → diff → notify → store:
  - **fetch**: watcher/fetch.py (httpx client with headers/retries/backoff)
  - **parse**: watcher/parse.py (selectolax HTML parsing for brigoska.cz job table)
  - **diff**: watcher/diff.py (JobDiff with new/removed/changed)
  - **notify**: watcher/notify.py (SMTP email from env vars)
  - **store**: watcher/store.py (SQLite state + notification de-dupe)

## Data model + identity
- `Job` is a dataclass in watcher/models.py. Identity is a stable key from normalized text.
- `compute_key()` hashes: title + city + date + day_of_week + time_range + wage; normalization collapses whitespace and removes NBSP (`\u00a0`).
- If adding fields, update `normalize_text()`, diff comparison in watcher/diff.py, and store schema/queries to keep keys stab# Website Change Catcher – AI coding guide


-
## Big picture
- Entry point is the Typer ook- Entry pointll- Core pipeline is fetch → parse → diff → notify → store:
  - **fetch**: watcher/fetch.py (http(P  - **fetch**: watcher/fetch.py (httpx client with headers/retris   - **parse**: watcher/parse.py (selectolax HTML parsing for brigoska.cz jan  - **diff**: watcher/diff.py (JobDiff with new/removed/changed)
  - **notify**: wtu  - **notify**: watcher/notify.py (SMTP email from env vars)
   +  - **store**: watcher/store.py (SQLite state + notificatio (
## Data model + identity
- `Job` is a dataclass in watcher/models.ptio- `Job` is a dataclass rs- `compute_key()` hashes: title + city + date + day_of_week + time_range + wage; normaliza h- If adding fields, update `normalize_text()`, diff comparison in watcher/diff.py, and store schema/queries to keep keys stab# Website Change C_s

-
## Big picture
- Entry point is the Typer ook- Entry pointll- Core pipeline is fetch → parse → diff → notify → store:
  - **fetch**: watcher/fetch.py (h- **Run on- Entry point p  - **fetch**: watcher/fetch.py (http(P  - **fetch**: watcher/fetch.py (httpx client with headers/retris   - TE  - **notify**: wtu  - **notify**: watcher/notify.py (SMTP email from env vars)
   +  - **store**: watcher/store.py (SQLite state + notificatio (
## Data model + identity
- `Job` is a dataclass in watcher/models.ptio- `Job` is a dataclass rs- `ation
- .env is loaded from project root by watcher/cli.py via python-dotenv.
- Re## Data model + identity
- `Job` is a dataclass in watcher/modelAS- `Job` is a dataclass L_
-
## Big picture
- Entry point is the Typer ook- Entry pointll- Core pipeline is fetch → parse → diff → notify → store:
  - **fetch**: watcher/fetch.py (h- **Run on- Entry point p  - **fetch**: watcher/fetch.py (http(P  - **fetch**: watcher/fetch.py (httpx client with headers/retris   - TE  - **nyment- Entry pointn   - **fetch**: watcher/fer.yml` runs every 30 minutes via cron.
- Requires secrets in repo settings: SMTP_HOST,   +  - **store**: watcher/store.py (SQLite state + notificatio (
## Data model + identity
- `tral-sh/setup-uv@v4` for environment.
- `uv pip install --system` required in CI (no venv).
- State persists via `actions/upload-artifact@v4` and `actions/d## Data model + identity
- `Job` is a dataclass in watcher/modelis- `Job` is a dataclass n - .env is loaded from project root by watcher/cli.py via python-dotenv.
- Re#).- Re## Data model + identity
- `Job` is a dataclass in watcher/modelAS a- `Job` is a dataclass in wn -
## Big picture
- Entry point is the Typer ook- Entry pointll- Ctype- Entry pointon  - **fetch**: watcher/fetch.py (h- **Run on- Entry point p  - **fetch**: watcher/fetch.py (http(P  - **fetchli- Requires secrets in repo settings: SMTP_HOST,   +  - **store**: watcher/store.py (SQLite state + notificatio (
## Data model + identity
- `tral-sh/setup-uv@v4` for environment.
- `uv pip install --system` required in CI (no venv).
- State persists via `actica## Data model + identity
- `tral-sh/setup-uv@v4` for environment.
- `uv pip install --system` required in CI (nfi- `trailure point.
- Test- `uv pip install --system` required inre- State persists via `actions/upload-artifact@v4` anyt- `Jversion: Project requires 3.11 (`>=3.11,<3.12` in pyproject.toml) for consistent behavior.
