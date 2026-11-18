"""QA exploratory-pass regressions (cycle 2). Defects are xfail(strict) so a fix flips them to a visible XPASS failure."""
import pytest

from conftest import FakeHttp
from pfeed.adapters import github, hn, run_sources, Source
from pfeed.http import FetchError
from pfeed.ledger import Ledger, canonical_url, cluster_key
from pfeed.models import make_candidate


@pytest.mark.xfail(strict=True, reason="QA-1: null items/hits escapes as TypeError, breaking fail-soft (run_sources catches only FetchError)")
@pytest.mark.parametrize("fetch,body", [
    (lambda h: github.fetch(h, url="https://x.test/"), b'{"items": null}'),
    (lambda h: hn.fetch(h, url="https://x.test/"), b'{"hits": null}')])
def test_null_collection_is_fetch_error(fetch, body):
    with pytest.raises(FetchError):
        fetch(FakeHttp(body))


def test_null_payload_does_not_stop_other_sources_documented():
    """Characterizes QA-1 end to end: today a null payload crashes the whole run."""
    class H:
        def fetch(self, url):
            return b'{"items": null}'
    srcs = [Source("a", "https://a/", lambda http: github.fetch(http, url="https://a/"))]
    try:
        run_sources(H(), srcs)
    except TypeError:
        pytest.xfail("QA-1 still open")


@pytest.mark.parametrize("raw,expected", [
    ("https://github.com/Owner/Repo/", "https://github.com/owner/repo"),
    ("https://Example.com:443/a", "https://example.com/a"),
    ("https://example.com/a//", "https://example.com/a"),
    ("https://arxiv.org/abs/hep-th/9901001v2", "https://arxiv.org/abs/hep-th/9901001"),
])
def test_canonical_url_oddities(raw, expected):
    assert canonical_url(raw) == expected


def test_repo_subpage_and_query_cluster_to_repo():
    assert cluster_key("https://github.com/o/r/issues/3") == cluster_key("https://github.com/o/r?tab=readme") == "gh:o/r"


def test_ledger_title_with_pipe_newline_backslash_roundtrips(tmp_path):
    p = tmp_path / "l.md"
    c = make_candidate("a | b\nc \\| d", "https://q.test/1", "s", "blog", "article")
    Ledger(p).append("2026-11-19", "01", [c])
    assert Ledger(p).rows[0][4] == "a | b c \\| d"


def test_ledger_tolerates_truncated_row_and_blank_lines(tmp_path):
    p = tmp_path / "l.md"
    c = make_candidate("t", "https://q.test/1", "s", "blog", "article")
    Ledger(p).append("d", "e", [c])
    with p.open("a") as f:
        f.write("| 2026-11-20 | 02 | https://z.test/ |\n\n")
    assert len(Ledger(p).rows) == 1


def test_paper_linking_repo_is_seen_after_repo_delivered(tmp_path):
    p = tmp_path / "l.md"
    Ledger(p).append("d", "e", [make_candidate("r", "https://github.com/A/B", "s", "GitHub", "repo")])
    paper = make_candidate("P", "https://arxiv.org/abs/2611.1v1", "a", "arXiv", "paper",
                           extras={"repo_links": ["https://github.com/a/b"]})
    assert Ledger(p).seen(paper)
