import json

import pytest

from adapters_helpers import hn_candidate_for
from conftest import FakeHttp
from pfeed.adapters import arxiv, github, hfpapers, hn, lobsters, rss
from pfeed.http import FetchError
from pfeed.models import Candidate, SOURCE_TYPES, ITEM_TYPES

U = "https://x.test/feed"


def assert_valid(cands):
    assert cands
    for c in cands:
        assert isinstance(c, Candidate)
        assert c.title and c.url.startswith("https://") and c.canonical_url.startswith("https://")
        assert c.source and c.source_type in SOURCE_TYPES and c.item_type in ITEM_TYPES


# ---- GitHub
def test_github_fixture(fx):
    cands = github.fetch(FakeHttp(fx("github.json")), url=U)
    assert_valid(cands)
    first = cands[0]
    assert (first.title, first.source_type, first.item_type) == ("HKUDS/nanobot", "GitHub", "repo")
    assert first.extras["stars"] > 1000 and first.canonical_url == "https://github.com/hkuds/nanobot"


def test_github_drops_awesome_lists(fx):
    data = json.loads(fx("github.json"))
    clone = dict(data["items"][0], name="awesome-agents", full_name="x/awesome-agents",
                 html_url="https://github.com/x/awesome-agents")
    data["items"].append(clone)
    cands = github.fetch(FakeHttp(json.dumps(data).encode()), url=U)
    assert "x/awesome-agents" not in [c.title for c in cands]
    assert len(cands) == len(data["items"]) - 1


def test_github_url_builder():
    assert github.url_for("topic:mcp+created:>2026-11-12").startswith(
        "https://api.github.com/search/repositories?q=topic:mcp+created:>2026-11-12&sort=stars")


# ---- HN
def test_hn_fixture_min_points(fx):
    http = FakeHttp(fx("hn.json"))
    cands = hn.fetch(http, url=U, min_points=0)
    assert_valid(cands)
    assert all(c.source_type == "HN" and c.extras["hn_url"].startswith("https://news.ycombinator.com/item?id=")
               for c in cands)
    assert hn.fetch(http, url=U, min_points=10_000) == []


def test_hn_story_to_repo_is_repo_item_and_ask_hn_is_discussion():
    assert hn_candidate_for("https://github.com/foo/bar").item_type == "repo"
    assert hn_candidate_for("https://arxiv.org/abs/2611.1").item_type == "paper"
    hit = {"objectID": "7", "title": "Ask HN: evals?", "url": None, "points": 99, "num_comments": 40,
           "created_at": "2026-11-18T00:00:00Z"}
    c = hn.fetch(FakeHttp(json.dumps({"hits": [hit]}).encode()), url=U)[0]
    assert c.item_type == "discussion" and c.url == "https://news.ycombinator.com/item?id=7"


# ---- lobste.rs
def test_lobsters_fixture(fx):
    cands = lobsters.fetch(FakeHttp(fx("lobsters.xml")), url=U)
    assert_valid(cands)
    assert all(c.source_type == "Lobsters" and c.extras["discussion_url"].startswith("https://lobste.rs/s/")
               for c in cands)


# ---- arXiv
def test_arxiv_keeps_only_papers_with_github_link(fx):
    cands = arxiv.fetch(FakeHttp(fx("arxiv.xml")), url=U)
    assert_valid(cands)
    assert len(cands) == 1  # fixture has 4 entries, one links a repo (in the comment field)
    c = cands[0]
    assert (c.source_type, c.item_type) == ("arXiv", "paper")
    assert c.extras["repo_links"] == ["https://github.com/WangHaoZhe/metal-sandbox",
                                      "https://github.com/WangHaoZhe/harbor"]
    assert c.url.startswith("https://arxiv.org/abs/")


# ---- HF papers
def test_hfpapers_keeps_papers_with_repo(fx):
    rows = json.loads(fx("hfpapers.json"))
    cands = hfpapers.fetch(FakeHttp(fx("hfpapers.json")), url=U)
    assert_valid(cands)
    assert len(cands) == sum(1 for r in rows if r["paper"].get("githubRepo"))
    assert cands[0].canonical_url == "https://arxiv.org/abs/2611.20995"


# ---- RSS / Atom
@pytest.mark.parametrize("name,stype", [("blog_rss.xml", "blog"), ("substack_rss.xml", "Substack"),
                                        ("atom.xml", "blog")])
def test_rss_and_atom_fixtures(fx, name, stype):
    cands = rss.fetch(FakeHttp(fx(name)), url=U, name="n", source_type=stype)
    assert_valid(cands)
    assert all(c.source_type == stype and c.item_type == "article" for c in cands)
    assert all("<" not in c.summary for c in cands)


def test_rss_pubdate_is_iso(fx):
    c = lobsters.fetch(FakeHttp(fx("lobsters.xml")), url=U)[0]
    assert c.published.startswith("2026-11-18T15:53:43")


# ---- malformed entries and failures
def test_malformed_entries_are_skipped_not_raised(fx):
    data = json.loads(fx("github.json"))
    data["items"] += [{}, {"name": "x"}, {"name": "y", "full_name": "", "html_url": "https://github.com/a/b"},
                      {"name": "z", "full_name": "a/z", "html_url": "http://github.com/a/z"}, "garbage", None]
    cands = github.fetch(FakeHttp(json.dumps(data).encode()), url=U)
    assert len(cands) == len(json.loads(fx("github.json"))["items"])


def test_rss_entries_without_title_or_https_link_are_skipped():
    xml = (b"<rss><channel><item><title></title><link>https://a.test/1</link></item>"
           b"<item><title>no link</title></item>"
           b"<item><title>http only</title><link>http://a.test/2</link></item>"
           b"<item><title>good</title><link>https://a.test/3</link></item></channel></rss>")
    assert [c.title for c in rss.fetch(FakeHttp(xml), url=U, name="n", source_type="blog")] == ["good"]


@pytest.mark.parametrize("fetch", [
    lambda h: github.fetch(h, url=U), lambda h: hn.fetch(h, url=U), lambda h: lobsters.fetch(h, url=U),
    lambda h: arxiv.fetch(h, url=U), lambda h: hfpapers.fetch(h, url=U),
    lambda h: rss.fetch(h, url=U, name="n", source_type="blog")])
@pytest.mark.parametrize("body", [b"<html>not a feed</html>", b"\x00\xffgarbage", b""])
def test_garbage_body_raises_fetch_error(fetch, body):
    with pytest.raises(FetchError):
        fetch(FakeHttp(body))
