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
- If adding fields, update `normalize_text()`, diff compari# Website Change Catcher – AI coding guide

## Big picture
- Entry point is the Typer CLI in watcher/cli.py, i
-
## Big picture
- Entry poor brigoska.cz: look- Entry pointll- Core pipeline is fetch → parse → diff → notify → store:
  - **fetch**: watcher/fetch.py (http(P  - **fetch**: watcher/fetch.py (httpx client ics.
- Keep filters   - **parse**: watcher/parse.py (selectolax HTML parsing for brigoska.cz jan  - **diff**: watcher/diff.py (JobDiff with new/removed/changed)
  - **notify**: wtu  - **notify**: watcher/notify.py (SMTP email from env vars)
   +  - **store**: watcher/store.py (SQLite state + notificatio (
## Data model + identity
- `Job` is a dataclass in watcher/models.ptio- `Job` is a dataclass rs- `compute_key()` hashes: title + city + date + day_of_week + time_range + wage; normaliza h- If adding fields, update `normalize_text()`, diff compari# Website Change Catcher – AI coding guide

## Big picture
- Entry point is the Ty_s
## Big picture
- Entry point is the Typer CLI in watcher/cli.py, i
-
## Big picture
- Entry poor brigv &- Entry pointv/-
## Big picture
- Entry poor brigoska.cz: look- EEADM- Entry poor n   - **fetch**: watcher/fetch.py (http(P  - **fetch**: watcher/fetch.py (httpx client ics.
- Keep filters   - EC- Keep filters   - **parse**: watcher/parse.py (selectolax HTML parsing for brigoska.cz fi  - **notify**: wtu  - **notify**: watcher/notify.py (SMTP email from env vars)
   +  - **store**cli.py – it already prints fetch/parse/diff summaries.

## Environment configuration
- .env is loaded from project root by watcher/cli.py## Data model + identity
- `Job` is a dataclass in watcher/modelT`- `Job` is a dataclass SS
## Big picture
- Entry point is the Ty_s
## Big picture
- Entry point is the Typer CLI in watcher/cli.py, i
-
## Big picture
- Entry poor brigv &- Entry pointv/-
## Big picification()).
- `SMTP_PASS` strips spaces (common issue with Google App Passwords).
- `EMAIL_F- Entry pointch## Big picture
- Entry p
#- Entry pointon-
## Big picture
- Entry poor brigv &- Entry pointher.- Entry poor ry## Big picture
- Entry poor brigoskcr- Entry poor et- Keep filters   - ETP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO.
- Uses `actions/setup-python@v5` + `astral-sh/setup-uv@v4` for enviro   +  - **store**cli.py – it already prints fetch/parse/diff summaries.

## Environment configuration
- .env is loaded from project root by watcher/cli.py## Data model + identity
- `Job` is
## Environment configuration
- .env is loaded from project root by watc (H- .env is loaded from projepy- `Job` is a dataclass in watcher/modelT`- `Job` is a dataclass SS
## Big pnt## Big picture
- Entry point is the Ty_s
## Big picture
- Entry pit- Entry poi tra## Big picture
- Entry pS - Entry pointfy-
## Big picture
- Entry poor brigv &- Entry pointunts- Entry poor pi## Big picification()).
- `SMTP_PASha- `SMTP_PASS` strips s)`- `EMAIL_F- Entry pointch## Big picture
- Entry p
#- Entry pointon-
rs- Entry p
#- Entry pointon-
## Big pican#- Entry_r## Big picture
-x - Entry poor s - Entry poor brigoskcr- Entry poor et- Keep filters   - ETP_PORT,fi- Uses `actions/setple.html for real HTML validation.
- Python version: Project requires 3.11 (`>=3.11,<3.12` in pyproject.toml) for consistent behavior.
