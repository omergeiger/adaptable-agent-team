"""RSS 2.0 and Atom parsing, one function for both, plus the generic blog/Substack/Medium adapter."""
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from ..http import FetchError
from ..models import collect, extract_repo_links, make_candidate

ATOM = "{http://www.w3.org/2005/Atom}"
CONTENT = "{http://purl.org/rss/1.0/modules/content/}encoded"
DC_DATE = "{http://purl.org/dc/elements/1.1/}date"


def _text(node, *tags):
    for tag in tags:
        child = node.find(tag)
        if child is not None and (child.text or "").strip():
            return child.text.strip()
    return ""


def _iso(raw):
    try:
        return parsedate_to_datetime(raw).isoformat()
    except (TypeError, ValueError):
        return raw or ""


def _atom_link(entry):
    for link in entry.findall(f"{ATOM}link"):
        if link.get("rel", "alternate") == "alternate" and link.get("href"):
            return link.get("href")
    return ""


def parse_entries(body):
    """-> list of dicts {title, link, summary, published, comments, author}. Raises FetchError on non-feeds."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        raise FetchError(f"unparseable feed: {e}") from e
    if root.tag == f"{ATOM}feed":
        return [{
            "title": _text(e, f"{ATOM}title"), "link": _atom_link(e),
            "summary": _text(e, f"{ATOM}content", f"{ATOM}summary"),
            "published": _text(e, f"{ATOM}published", f"{ATOM}updated"),
            "comments": "", "author": _text(e, f"{ATOM}author/{ATOM}name"),
        } for e in root.findall(f"{ATOM}entry")]
    if root.tag == "rss":
        return [{
            "title": _text(i, "title"), "link": _text(i, "link"),
            "summary": _text(i, CONTENT, "description"),
            "published": _iso(_text(i, "pubDate", DC_DATE)),
            "comments": _text(i, "comments"), "author": _text(i, "author", "{http://purl.org/dc/elements/1.1/}creator"),
        } for i in root.iter("item")]
    raise FetchError(f"not an RSS/Atom document (root <{root.tag}>)")


def fetch(http, url, name, source_type):
    """Blog/Substack/Medium feed -> article candidates. source_type: 'blog' | 'Substack' | 'Medium'."""
    entries = parse_entries(http.fetch(url))

    def build(e):
        return make_candidate(
            e["title"], e["link"], name, source_type, "article", e["summary"], e["published"],
            {"author": e["author"], "repo_links": extract_repo_links(e["summary"])})

    return collect(build, entries)
