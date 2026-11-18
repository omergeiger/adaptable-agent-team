"""Candidate: the only shared type, plus small helpers every adapter uses."""
import html
import re
from dataclasses import dataclass, field

SOURCE_TYPES = {"GitHub", "HN", "Lobsters", "arXiv", "blog", "Medium", "Substack"}
ITEM_TYPES = {"repo", "article", "discussion", "paper", "tool"}

GITHUB_RESERVED_OWNERS = {
    "topics", "orgs", "features", "sponsors", "marketplace", "about", "pricing", "login",
    "explore", "collections", "trending", "settings", "apps", "enterprise", "search", "site",
    "security", "customer-stories", "readme", "blog", "users", "issues", "pulls", "events",
}
_REPO_RE = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9][\w.-]*)/([A-Za-z0-9_.-]+)")


@dataclass
class Candidate:
    title: str
    url: str
    canonical_url: str
    source: str          # e.g. "GitHub search: topic:llm-agents", "Hamel Husain"
    source_type: str     # one of SOURCE_TYPES (what D2 counts)
    item_type: str       # one of ITEM_TYPES (matches feed-item-format)
    summary: str = ""
    published: str = ""
    extras: dict = field(default_factory=dict)


def clean_text(text, limit=500):
    """Strip HTML tags, unescape entities, collapse whitespace, truncate."""
    text = re.sub(r"<[a-zA-Z/!][^>]*>?", " ", text or "")  # also drops a tag cut off at the end of a truncated feed
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def extract_repo_links(text):
    """Normalized https://github.com/owner/repo links found in free text (order kept, deduped)."""
    seen, out = set(), []
    for owner, repo in _REPO_RE.findall(text or ""):
        repo = repo.rstrip(".,;:)").removesuffix(".git")
        if not repo or owner.lower() in GITHUB_RESERVED_OWNERS:
            continue
        link = f"https://github.com/{owner}/{repo}"
        if link.lower() not in seen:
            seen.add(link.lower())
            out.append(link)
    return out


def classify_url(url):
    """item_type for a link that arrives via a forum/aggregator."""
    from .ledger import canonical_url, repo_slug  # local import: ledger imports models

    canon = canonical_url(url)
    if repo_slug(canon):
        return "repo"
    if canon.startswith("https://arxiv.org/abs/"):
        return "paper"
    return "article"


def make_candidate(title, url, source, source_type, item_type, summary="", published="", extras=None):
    """Validated Candidate or None. Requires a non-empty title and an https URL (never invents links)."""
    from .ledger import canonical_url

    title = clean_text(title, limit=300)
    url = (url or "").strip()
    if not title or not url.startswith("https://"):
        return None
    assert source_type in SOURCE_TYPES and item_type in ITEM_TYPES
    return Candidate(title, url, canonical_url(url), source, source_type, item_type,
                     clean_text(summary), published or "", extras or {})


def collect(build, raw_entries):
    """Apply build(raw) to each entry; malformed entries are skipped, never raised."""
    out = []
    for raw in raw_entries:
        try:
            cand = build(raw)
        except (KeyError, TypeError, ValueError, AttributeError, IndexError):
            continue
        if cand is not None:
            out.append(cand)
    return out
