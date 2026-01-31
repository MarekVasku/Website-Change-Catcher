# Website Change Catcher - Job Listing Monitor

A Python monitoring service that watches a specific webpage for job listing changes and sends email notifications when changes are detected.

## Features

- Periodically fetches a webpage (configurable via environment variables)
- Parses job listings from HTML (specifically designed for brigoska.cz)
- Detects changes: new jobs, removed jobs, and modified jobs
- Sends email notifications with a compact diff
- Persistent state using SQLite (survives restarts)
- De-duplicates notifications (won't spam for the same change)
- Robust error handling with retries and exponential backoff
- Anti-bot hygiene (realistic User-Agent, timeouts, etc.)


## Installation

1. Install [uv](https://docs.astral.sh/uv/): `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone or download this repository
3. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

Or install without dev dependencies: `uv pip install -e .`

## Configuration

Create a `.env` file in the project root with your secrets. This file is in `.gitignore` and will **not** be committed:

```bash
cp env.example .env
# Edit .env with your real SMTP credentials and email addresses
```

Example `.env`:

```bash
# URL to monitor
WATCH_URL=https://brigoska.cz/cs/mista

# Check interval in minutes (for continuous mode)
CHECK_INTERVAL_MINUTES=30

# SQLite database path
STATE_DB_PATH=./state.db

# SMTP configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Email addresses
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com,another@example.com
```

## Usage

Activate the virtual environment first (`source .venv/bin/activate`), or use `uv run`:

### Run Once

Check the webpage once and exit:

```bash
uv run python -m watcher --once
```

### Run Continuously

Run forever, checking every 30 minutes (or as configured):

```bash
uv run python -m watcher
```

Press `Ctrl+C` to stop.

## Testing

Run tests with pytest:

```bash
uv run pytest
```

To test parsing with a real HTML fixture, save a sample HTML page to `tests/fixtures/brigoska_sample.html`.

## Deployment

### GitHub Actions (Recommended for Free Hosting)

Create `.github/workflows/watcher.yml`:

```yaml
name: Job Watcher

on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  workflow_dispatch:  # Allow manual runs

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      - name: Install dependencies
        run: |
          uv pip install -e .
      - name: Run watcher
        env:
          WATCH_URL: ${{ secrets.WATCH_URL }}
          SMTP_HOST: ${{ secrets.SMTP_HOST }}
          SMTP_PORT: ${{ secrets.SMTP_PORT }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          STATE_DB_PATH: ./state.db
        run: |
          uv run python -m watcher --once
      - name: Upload state
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: watcher-state
          path: state.db
          retention-days: 90
      - name: Download previous state
        uses: actions/download-artifact@v3
        if: always()
        with:
          name: watcher-state
          path: ./
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

**Note**: GitHub Actions artifacts have limitations. For persistent state, consider using a database service or commit the state file (not recommended for sensitive data).

### Render.com

1. Create a new Web Service
2. Build command: `pip install uv && uv pip install -e .`
3. Start command: `uv run python -m watcher`
4. Add environment variables in the Render dashboard
5. The service will run continuously

### Fly.io

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Create app: `fly launch`
3. Build command: `pip install uv && uv pip install -e .`
4. Start command: `uv run python -m watcher`
5. Set environment variables: `fly secrets set SMTP_HOST=... SMTP_USER=... ...`
6. Deploy: `fly deploy`
5. The service will run continuously

**Note**: For Fly.io, you may want to use persistent volumes for the SQLite database:

```bash
fly volumes create watcher_data --size 1
```

Then mount it and set `STATE_DB_PATH=/data/state.db`.

## Project Structure

```
watcher/
├── __init__.py
├── __main__.py       # Entry point
├── cli.py            # CLI interface
├── models.py         # Job data model
├── fetch.py          # HTTP client with retries
├── parse.py          # HTML parsing
├── store.py          # SQLite storage
├── diff.py           # Change detection
└── notify.py         # Email notifications

tests/
├── test_models.py    # Model tests
├── test_diff.py      # Diff logic tests
├── test_parse.py     # Parser tests
└── fixtures/         # HTML fixtures for testing
```

## How It Works

1. **Fetch**: Downloads the webpage using `httpx` with retry logic
2. **Parse**: Extracts job listings using `selectolax` HTML parser
3. **Store**: Saves jobs to SQLite database with stable keys (hash of normalized content)
4. **Diff**: Compares current jobs with stored jobs to detect changes
5. **Notify**: Sends email via SMTP if changes are detected (and not already notified)
6. **Update**: Updates the database with new state

## Stable Key Strategy

Jobs are identified by a stable key computed from:
- Normalized text: `title + city + date + time_range + wage`
- Normalization: strip whitespace, collapse spaces, remove NBSP
- Hash: SHA256 (first 16 characters)

This ensures the same job (even with minor formatting differences) gets the same key.

## License

MIT
