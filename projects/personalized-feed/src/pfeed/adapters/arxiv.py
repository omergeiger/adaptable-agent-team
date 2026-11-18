"""arXiv API (S7). Keeps only papers whose abstract or comment links a GitHub repo (Alex: papers with code)."""
import xml.etree.ElementTree as ET

from ..http import FetchError
from ..models import collect, extract_repo_links, make_candidate

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
URL = ("https://export.arxiv.org/api/query?search_query="
       "(cat:cs.CL+OR+cat:cs.AI+OR+cat:cs.SE+OR+cat:cs.MA)+AND+all:agent+AND+abs:github"
       "&max_results=30&sortBy=submittedDate&sortOrder=descending")


def fetch(http, url=URL, name="arXiv"):
    try:
        root = ET.fromstring(http.fetch(url))
    except ET.ParseError as e:
        raise FetchError(f"{url}: unparseable arXiv response ({e})") from e

    if root.tag != "{http://www.w3.org/2005/Atom}feed":
        raise FetchError(f"{url}: not an Atom feed (root <{root.tag}>)")
    entries = root.findall("a:entry", NS)

    def build(e):
        summary = e.findtext("a:summary", "", NS)
        comment = e.findtext("x:comment", "", NS)
        repos = extract_repo_links(f"{summary} {comment}")
        if not repos:
            return None
        link = next(l.get("href") for l in e.findall("a:link", NS) if l.get("rel") == "alternate")
        return make_candidate(
            e.findtext("a:title", "", NS), link, name, "arXiv", "paper", summary, e.findtext("a:published", "", NS),
            {"repo_links": repos, "comment": " ".join(comment.split()),
             "categories": [c.get("term") for c in e.findall("a:category", NS)]})

    return collect(build, entries)
