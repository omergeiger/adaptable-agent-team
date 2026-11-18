from datetime import date

from conftest import FakeHttp
from pfeed.__main__ import check_live
from pfeed.adapters import Source, build_sources, rss, run_sources
from pfeed.http import FetchError

FEED = (b"<rss><channel><item><title>ok</title><link>https://a.test/1</link></item></channel></rss>")


class RoutedHttp:
    def __init__(self, routes):
        self.routes = routes

    def fetch(self, url):
        r = self.routes[url]
        if isinstance(r, Exception):
            raise r
        return r


def src(url):
    return Source(url, url, lambda http, url=url: rss.fetch(http, url=url, name=url, source_type="blog"))


def test_failure_in_one_source_does_not_stop_others_and_is_recorded():
    routes = {"https://a.test/ok": FEED, "https://a.test/down": FetchError("https://a.test/down: HTTP 500"),
              "https://a.test/junk": b"garbage", "https://a.test/ok2": FEED}
    result = run_sources(RoutedHttp(routes), [src(u) for u in routes])
    assert [c.title for c in result.candidates] == ["ok", "ok"]
    status = {r.id: r for r in result.reports}
    assert status["https://a.test/ok"].ok and status["https://a.test/ok"].count == 1
    assert not status["https://a.test/down"].ok and "HTTP 500" in status["https://a.test/down"].error
    assert not status["https://a.test/junk"].ok and status["https://a.test/junk"].error


def test_build_sources_covers_catalog_and_every_url_is_https():
    sources = build_sources(date(2026, 11, 19))
    ids = {s.id.split(":")[0] for s in sources}
    assert {"S1", "S3", "S5", "S7", "S7c", "S8", "S9", "S10", "S11", "S17"} <= ids
    assert all(s.url.startswith("https://") for s in sources)
    assert sum(s.id.startswith("S1:") for s in sources) <= 15  # GitHub search budget


def test_check_live_prints_status_counts_offline():
    lines = []
    http = FakeHttp(error=FetchError("boom"))
    assert check_live(http=http, out=lines.append, today=date(2026, 11, 19)) == 1
    assert lines[-1].startswith("sources ok: 0/") and any(l.startswith("FAIL") for l in lines)
