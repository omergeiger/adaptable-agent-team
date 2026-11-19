"""Recency filter on Candidate.published. Undated or unparseable items are kept (conservative)."""
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

DEFAULT_WINDOW_DAYS = 14


def parse_published(text):
    """ISO-8601 or RFC-2822 string -> aware UTC datetime, or None."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = parsedate_to_datetime(text)
        except (TypeError, ValueError):
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def filter_recent(candidates, today, window_days=DEFAULT_WINDOW_DAYS):
    """(kept, dropped_count). today is a date; items older than window_days before end of today are dropped."""
    cutoff = datetime(today.year, today.month, today.day, tzinfo=timezone.utc) - timedelta(days=window_days)
    kept = []
    for c in candidates:
        dt = parse_published(c.published)
        if dt is None or dt >= cutoff:
            kept.append(c)
    return kept, len(candidates) - len(kept)
