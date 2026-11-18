import pytest

from pfeed.ledger import Ledger, canonical_url, cluster_key, ledger_path
from pfeed.models import Candidate, make_candidate


@pytest.mark.parametrize("raw,expected", [
    ("http://www.Example.com/post/?utm_source=x&utm_medium=y&id=3#frag", "https://example.com/post?id=3"),
    ("https://example.com/a/?ref=hn&source=rss", "https://example.com/a"),
    ("https://EXAMPLE.com/", "https://example.com"),
    ("https://github.com/Owner/Repo.git", "https://github.com/owner/repo"),
    ("https://arxiv.org/pdf/2611.22148v2.pdf", "https://arxiv.org/abs/2611.22148"),
    ("http://arxiv.org/abs/2611.22148v1", "https://arxiv.org/abs/2611.22148"),
])
def test_canonical_url(raw, expected):
    assert canonical_url(raw) == expected


def test_canonical_url_rejects_non_http():
    with pytest.raises(ValueError):
        canonical_url("ftp://example.com/x")


def test_hn_story_pointing_at_repo_canonicalizes_to_repo():
    from adapters_helpers import hn_candidate_for
    c = hn_candidate_for("https://github.com/Foo/Bar/?utm_source=hn")
    assert c.canonical_url == "https://github.com/foo/bar"


def cand(url, item_type="article", repo_links=None):
    return Candidate("t", url, canonical_url(url), "s", "blog", item_type, extras={"repo_links": repo_links or []})


def test_cluster_key_repo_and_arxiv_repo_link_agree():
    repo = cand("https://github.com/WangHaoZhe/harbor", "repo")
    paper = cand("https://arxiv.org/abs/2611.22148v1", "paper", ["https://github.com/wanghaozhe/harbor"])
    assert cluster_key(repo) == cluster_key(paper) == "gh:wanghaozhe/harbor"


def test_cluster_key_arxiv_versions_agree():
    assert cluster_key("https://arxiv.org/abs/2611.22148v1") == cluster_key("https://arxiv.org/pdf/2611.22148v2") \
        == "arxiv:2611.22148"


def test_cluster_key_plain_url_and_repo_subpage():
    assert cluster_key("https://example.com/a/?utm_x=1") == "https://example.com/a"
    assert cluster_key("https://github.com/o/r/tree/main/docs") == "gh:o/r"
    assert cluster_key("https://github.com/topics/agents").startswith("https://github.com/topics")


def test_blog_mentioning_repo_does_not_cluster_with_repo():
    assert cluster_key(cand("https://blog.test/p", "article", ["https://github.com/o/r"])) == "https://blog.test/p"


def test_ledger_roundtrip_and_seen(tmp_path):
    path = ledger_path(tmp_path, "alex")
    assert path.name == "alex-delivered.md"
    led = Ledger(path)
    repo = cand("https://github.com/o/r", "repo")
    led.append("2026-11-19", "01", [repo])
    again = Ledger(path)
    assert again.rows == led.rows and len(again.rows) == 1
    assert again.seen(repo)
    assert again.seen(cand("https://www.github.com/O/R/?ref=x", "repo"))  # same canonical
    paper = cand("https://arxiv.org/abs/2611.1v1", "paper", ["https://github.com/o/r"])
    assert again.seen(paper)  # same cluster, different URL
    assert not again.seen(cand("https://example.com/new"))


def test_ledger_file_is_readable_markdown_with_header(tmp_path):
    path = tmp_path / "profile" / "u-delivered.md"  # missing dir and file: created on append
    Ledger(path).append("2026-11-19", "01", [cand("https://a.test/x")])
    lines = path.read_text().splitlines()
    assert lines[0] == "| date | edition | canonical_url | cluster_key | title |"
    assert lines[1].startswith("|---")
    assert lines[2] == "| 2026-11-19 | 01 | https://a.test/x | https://a.test/x | t |"


def test_ledger_titles_with_pipes_roundtrip(tmp_path):
    c = make_candidate("A | B\nC", "https://a.test/x", "s", "blog", "article")
    led = Ledger(tmp_path / "l.md")
    led.append("2026-11-19", "01", [c])
    assert Ledger(tmp_path / "l.md").rows[0][4] == "A | B C"


def test_no_append_leaves_ledger_unchanged(tmp_path):
    path = tmp_path / "l.md"
    led = Ledger(path)
    led.append("2026-11-19", "01", [cand("https://a.test/x")])
    before = path.read_text()
    Ledger(path)  # selecting/ranking would happen here; a crash means append is never called
    assert path.read_text() == before


def test_ledger_unique_per_user(tmp_path):
    a, b = Ledger(ledger_path(tmp_path, "alex")), Ledger(ledger_path(tmp_path, "sam"))
    c = cand("https://a.test/x")
    a.append("2026-11-19", "01", [c])
    assert a.seen(c) and not Ledger(ledger_path(tmp_path, "sam")).seen(c) and not b.seen(c)
