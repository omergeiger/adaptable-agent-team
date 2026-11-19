"""lobste.rs RSS (S5). The item link is the target page; the discussion URL is kept in extras.

fetch() parses the feed only. fetch_checked() also verifies each linked page (QA D-4): an off-topic or
mismatched page is quarantined (dropped and recorded), never delivered.
"""
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

from ..http import FetchError
from ..models import classify_url, collect, make_candidate
from .rss import parse_entries

TECH_WORDS = {"code", "api", "model", "models", "llm", "software", "algorithm", "compiler", "benchmark", "github",
              "python", "rust", "data", "training", "inference", "agent", "agents", "neural", "function",
              "implementation", "library", "performance", "security", "prompt", "token", "tokens", "database"}
MIN_TECH_WORDS = 1  # lobste.rs is a technical community: only clearly non-technical pages are quarantined
MIN_TITLE_OVERLAP = 0.34
CHECK_WORKERS = 8
STOPWORDS = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are", "with", "your", "how",
             "why", "what", "from", "into", "that", "this", "new", "way"}
SKIP_HOSTS = {"github.com", "arxiv.org", "lobste.rs"}  # already classified by the link itself


def fetch(http, url, name="lobste.rs"):
    def build(e):
        return make_candidate(
            e["title"], e["link"], name, "Lobsters", classify_url(e["link"]), "", e["published"],
            {"discussion_url": e["comments"], "author": e["author"]})

    return collect(build, parse_entries(http.fetch(url)))


def _page_text(html):
    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).lower()


def page_problem(title, html):
    """None if the page looks technical and matches the title, else a short reason."""
    text = _page_text(html)
    words = set(re.findall(r"[a-z][a-z0-9+.#-]*", text))
    tech = len(TECH_WORDS & words) + (2 if re.search(r"(?i)<(pre|code)\b", html) else 0)
    if tech < MIN_TECH_WORDS:
        return "linked page does not look technical"
    tokens = [t for t in re.findall(r"[a-z0-9]{4,}", title.lower()) if t not in STOPWORDS]
    if tokens and sum(t in words for t in tokens) / len(tokens) < MIN_TITLE_OVERLAP:
        return "linked page does not match the title"
    return None


def _check(http, c):
    """(problem or None) for one candidate. SSL / blocked failures are ours, not the page's: kept unverified."""
    if (urlsplit(c.url).hostname or "") in SKIP_HOSTS:
        return None
    try:
        return page_problem(c.title, http.fetch(c.url).decode("utf-8", "replace"))
    except FetchError as e:
        if getattr(e, "kind", "") in ("ssl", "blocked"):
            return None
        return f"linked page unreachable ({e})"


def fetch_checked(http, url, name="lobste.rs", quarantine=None):
    """fetch() + link sanity check, run in parallel. Mismatched or dead targets go to `quarantine` as 'title: reason'."""
    quarantine = quarantine if quarantine is not None else []
    candidates = fetch(http, url, name)
    with ThreadPoolExecutor(max_workers=CHECK_WORKERS) as pool:
        problems = list(pool.map(lambda c: _check(http, c), candidates))  # map keeps feed order
    kept = []
    for c, problem in zip(candidates, problems):
        if problem:
            quarantine.append(f"{c.title}: {problem}")
        else:
            kept.append(c)
    return kept
