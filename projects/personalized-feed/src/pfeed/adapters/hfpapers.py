"""Hugging Face Daily Papers (S7c): undocumented public API, fragile, optional. Papers with a repo only."""
import json

from ..http import FetchError
from ..models import collect, extract_repo_links, make_candidate

URL = "https://huggingface.co/api/daily_papers?limit=30"


def fetch(http, url=URL, name="HF Daily Papers"):
    try:
        rows = json.loads(http.fetch(url))
        if not isinstance(rows, list):
            raise TypeError("expected a list")
    except (ValueError, TypeError) as e:
        raise FetchError(f"{url}: unexpected HF payload ({e})") from e

    def build(row):
        p = row["paper"]
        repos = extract_repo_links(p.get("githubRepo") or "")
        if not repos:
            return None
        return make_candidate(
            p["title"], f"https://arxiv.org/abs/{p['id']}", name, "arXiv", "paper", p.get("summary", ""),
            p.get("publishedAt", ""), {"repo_links": repos, "upvotes": p.get("upvotes"), "stars": p.get("githubStars")})

    return collect(build, rows)
