"""HTTP fetcher with retry logic."""

import time
from typing import Optional

import httpx


def fetch_url(url: str, max_retries: int = 3, timeout: float = 30.0) -> Optional[str]:
    """
    Fetch a URL with retries and exponential backoff.

    Returns the page HTML or None if it fails.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "cs,en;q=0.9",
    }

    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        for attempt in range(max_retries):
            try:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
                return None
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

    return None
