"""lobste.rs RSS (S5). The item link is the target page; the discussion URL is kept in extras."""
from ..models import classify_url, collect, make_candidate
from .rss import parse_entries


def fetch(http, url, name="lobste.rs"):
    def build(e):
        return make_candidate(
            e["title"], e["link"], name, "Lobsters", classify_url(e["link"]), "", e["published"],
            {"discussion_url": e["comments"], "author": e["author"]})

    return collect(build, parse_entries(http.fetch(url)))
