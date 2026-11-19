"""GitHub search API (S1): 'new and rising' repos by topic. Official API, unauthenticated."""
import json
import re
from urllib.parse import quote

from ..http import FetchError
from ..models import collect, make_candidate

API = "https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=30"
_AWESOME = re.compile(r"^awesome([-_]|$)", re.I)


def url_for(query):
    return API.format(q=quote(query, safe=":>+"))


def fetch(http, url, name="GitHub search"):
    try:
        items = json.loads(http.fetch(url))["items"]
        if not isinstance(items, list):
            raise TypeError("items is not a list")
    except (ValueError, KeyError, TypeError) as e:
        raise FetchError(f"{url}: unexpected GitHub payload ({e})") from e

    def build(r):
        if _AWESOME.match(r["name"]):
            return None  # awesome-lists are curation, not something to clone and try
        return make_candidate(
            r["full_name"], r["html_url"], name, "GitHub", "repo", r.get("description") or "", r.get("pushed_at", ""),
            {"stars": r.get("stargazers_count"), "language": r.get("language"), "topics": r.get("topics") or [],
             "created_at": r.get("created_at"), "pushed_at": r.get("pushed_at")})

    return collect(build, items)
