"""URL normalization, cluster keys, and the append-only dedup ledger (markdown, human-readable)."""
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import GITHUB_RESERVED_OWNERS

TRACKING_PARAMS = {"ref", "source"}
_ARXIV_RE = re.compile(r"^/(?:abs|pdf)/(.+?)(?:\.pdf)?$")
_VERSION_RE = re.compile(r"v\d+$")
HEADER = "| date | edition | canonical_url | cluster_key | title |\n|---|---|---|---|---|\n"


def canonical_url(url):
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError(f"not an http(s) URL: {url!r}")
    host = parts.hostname.lower().removeprefix("www.")
    netloc = host if parts.port in (None, 80, 443) else f"{host}:{parts.port}"
    path = parts.path.rstrip("/")
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in TRACKING_PARAMS]
    if host == "arxiv.org":
        m = _ARXIV_RE.match(path)
        if m:
            path = "/abs/" + _VERSION_RE.sub("", m.group(1))
    elif host == "github.com":
        path = path.lower().removesuffix(".git")
    return urlunsplit(("https", netloc, path, urlencode(query), ""))


def repo_slug(url):
    """'owner/repo' (lowercase) if url is a GitHub repo (or a page inside one), else None."""
    parts = urlsplit(canonical_url(url))
    if parts.hostname != "github.com":
        return None
    segs = [s for s in parts.path.split("/") if s]
    if len(segs) < 2 or segs[0] in GITHUB_RESERVED_OWNERS:
        return None
    return f"{segs[0]}/{segs[1]}"


def cluster_key(item):
    """Project/topic identity: gh:<owner>/<repo>, arxiv:<id>, else the canonical URL.

    Accepts a URL string or a Candidate. A paper (arXiv / HF Papers) that links a repo clusters with
    that repo, so the same project arriving as a paper and as a repo is one item. Only papers do this:
    a blog post that merely mentions a repo is not the same item as the repo.
    """
    url = item if isinstance(item, str) else item.canonical_url
    slug = repo_slug(url)
    if slug:
        return f"gh:{slug}"
    if not isinstance(item, str) and item.item_type == "paper":
        for link in item.extras.get("repo_links", []):
            slug = repo_slug(link)
            if slug:
                return f"gh:{slug}"
    canon = canonical_url(url)
    if canon.startswith("https://arxiv.org/abs/"):
        return "arxiv:" + canon.removeprefix("https://arxiv.org/abs/")
    return canon


def ledger_path(root, user_id):
    """profile/<user_id>-delivered.md under the project root (D5: ledger is per user)."""
    return Path(root) / "profile" / f"{user_id}-delivered.md"


def _cell(text):
    return re.sub(r"\s+", " ", str(text)).replace("|", "\\|").strip()


class Ledger:
    """Append-only record of delivered items. Call append() only after the edition is safely written."""

    def __init__(self, path):
        self.path = Path(path)
        self.rows = []  # (date, edition, canonical_url, cluster_key, title)
        self._urls, self._clusters = set(), set()
        if self.path.exists():
            self._load()

    def _load(self):
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            if len(cells) != 5 or cells[0] == "date" or set(cells[0]) <= {"-", ":"}:
                continue
            self._remember(tuple(cells))

    def _remember(self, row):
        self.rows.append(row)
        self._urls.add(row[2])
        self._clusters.add(row[3])

    def seen(self, candidate):
        return candidate.canonical_url in self._urls or cluster_key(candidate) in self._clusters

    def append(self, date, edition, candidates):
        new_rows = [(str(date), str(edition), c.canonical_url, cluster_key(c), c.title) for c in candidates]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(HEADER, encoding="utf-8")
        with self.path.open("a", encoding="utf-8") as f:
            for row in new_rows:
                f.write("| " + " | ".join(_cell(c) for c in row) + " |\n")
        for row in new_rows:
            self._remember(row)
