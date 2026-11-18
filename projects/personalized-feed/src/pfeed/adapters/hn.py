"""Hacker News via Algolia (S3). Stories only; low-point stories are dropped here (source-specific filter)."""
import json
from urllib.parse import quote

from ..http import FetchError
from ..models import classify_url, collect, make_candidate

MIN_POINTS = 10
API = "https://hn.algolia.com/api/v1/search_by_date?query={q}&tags=story&hitsPerPage=30&numericFilters={nf}"


def url_for(query, since_epoch=None, min_points=MIN_POINTS):
    nf = f"points>{min_points}" + (f",created_at_i>{since_epoch}" if since_epoch else "")
    return API.format(q=quote(query), nf=quote(nf, safe=",="))


def fetch(http, url, name="Hacker News", min_points=MIN_POINTS):
    try:
        hits = json.loads(http.fetch(url))["hits"]
    except (ValueError, KeyError, TypeError) as e:
        raise FetchError(f"{url}: unexpected HN payload ({e})") from e

    def build(h):
        if (h.get("points") or 0) < min_points:
            return None
        hn_url = f"https://news.ycombinator.com/item?id={h['objectID']}"
        target = h.get("url")
        # Ask HN / text posts have no target: the discussion itself is the item.
        link, item_type = (target, classify_url(target)) if target else (hn_url, "discussion")
        return make_candidate(
            h["title"], link, name, "HN", item_type, h.get("story_text") or "", h.get("created_at", ""),
            {"points": h.get("points"), "comments": h.get("num_comments"), "hn_url": hn_url, "author": h.get("author")})

    return collect(build, hits)
