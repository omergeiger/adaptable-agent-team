"""Slice 6: ranking-engineer cycle-8 findings. Offline: synthetic test-only candidates and canned pages."""
import ssl
import threading
import time
import urllib.error
from datetime import date

import pytest

from rank_helpers import PROFILE, cand, empty_ledger, good_pool
from pfeed import rank
from pfeed.adapters import lobsters
from pfeed.http import FetchError, Http
from pfeed.rank_data import DEFAULT_WEIGHTS
from pfeed.render import render_edition, sidecar, why_line

TODAY = date(2026, 11, 19)


def score(c):
    return rank.score(c, PROFILE, DEFAULT_WEIGHTS, set(), TODAY)


def select(pool, tmp_path):
    return rank.select(pool, PROFILE, DEFAULT_WEIGHTS, empty_ledger(tmp_path), today=TODAY)


# ---- 4: weak-only match scores 1 (D-6) ----
def test_weak_only_title_match_scores_1():
    s = score(cand("Catching prompt injections hidden in PDFs", "https://x.test/p", "Lobsters", "article"))
    assert s.signals["interest-match"] == 1


def test_weak_only_high_interest_still_scores_1():
    # "benchmark" is a weak keyword of a weight-4 interest: one tier lower is not enough, weak-only is 1
    s = score(cand("A benchmark of web servers", "https://x.test/b", "blog", "article", "latency numbers"))
    assert s.signals["interest-match"] <= 1


# ---- 1: why-line cites only real content matches ----
def alive():
    return cand("ALIVE: streaming video models", "https://arxiv.org/abs/2601.99999", "arXiv", "paper",
                "Video generation with tracing of objects across frames.", repo_links=["https://github.com/v/alive"])


def test_alive_video_paper_is_not_matched_to_observability():
    s = score(alive())
    assert s.signals["interest-match"] <= 2 and not s.strong


def test_why_line_omits_interest_without_strong_match():
    s = score(alive())
    assert "observability" not in why_line(s)


def test_why_line_cites_interest_and_matched_keywords_when_strong():
    s = score(cand("Tracing LLM pipelines with OpenTelemetry", "https://blog.test/tracing", "blog", "article",
                   "step-by-step guide", source="Some Blog"))
    why = why_line(s)
    assert "observability" in why and "tracing" in why.lower()


# ---- 2: weak items are dropped; source-type shortfall is logged, not filled ----
def test_items_with_interest_match_2_or_less_are_never_selected(tmp_path):
    pool = good_pool() + [cand("o5/sae-interpretability", "https://github.com/o5/sae-interpretability",
                               summary="sparse autoencoder interpretability toolkit", stars=300)]
    sel = select(pool, tmp_path)
    assert sel.items and all(s.signals["interest-match"] >= 3 for s in sel.items)
    assert not any("sae-interpretability" in s.candidate.title for s in sel.items)


def only_github_pool():
    topics = ["agent framework with tool use", "evals for llm agents", "quantization to gguf for llama.cpp",
              "structured extraction from documents", "llm observability with opentelemetry tracing"]
    return [cand(f"o{i}/proj-{i}", f"https://github.com/o{i}/proj-{i}", summary=t, stars=300 + i)
            for i, t in enumerate(topics, 1)]


def test_source_type_shortfall_ships_with_warning_instead_of_filling(tmp_path):
    pool = only_github_pool() + [cand("Weak pdf note", "https://x.test/w", "Lobsters", "article", "pdf")]
    sel = select(pool, tmp_path)
    assert sel.items, "an under-diverse but relevant edition still ships"
    assert not any(s.candidate.source_type == "Lobsters" for s in sel.items)
    assert any("source-type shortfall" in w for w in sel.warnings)
    assert sel.stats["source_types"] == ["GitHub"]
    render_edition(sel, "alex", TODAY)  # renders; does not assert on diversity


def test_too_few_relevant_items_ships_nothing(tmp_path):
    sel = select(only_github_pool()[:2], tmp_path)
    assert sel.items == [] and any("ALARM" in w for w in sel.warnings)


# ---- 3: broadening vs in-interest exploration ----
def test_in_interest_exploration_is_not_labelled_broadening(tmp_path):
    sel = select(good_pool(), tmp_path)
    picks = [s for s in sel.items if s.exploration]
    assert picks, "fixture pool has an exploration-eligible item"
    for s in picks:
        assert s.exploration_kind == "in-interest"
        why = why_line(s)
        assert why.startswith("Exploration pick") and "Broadening" not in why and s.interest in why
    side = sidecar(sel, "alex", TODAY, 1, DEFAULT_WEIGHTS)
    assert {i["exploration_kind"] for i in side["items"]} <= {"", "in-interest", "broadening"}


def test_true_broadening_label_is_reserved_for_items_outside_all_interests():
    s = score(cand("o1/gardening-bot", "https://github.com/o1/gardening-bot", summary="plant watering", stars=300))
    s.exploration, s.exploration_kind = True, "broadening"
    assert why_line(s).startswith("Broadening pick") and "touching" not in why_line(s)


# ---- 5: Lobsters quarantine thresholds and parallel link check ----
FEED_TMPL = """<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>{items}</channel></rss>"""
ITEM = ("<item><title>{t}</title><link>{u}</link><author>x via y</author>"
        "<pubDate>Wed, 18 Nov 2026 08:45:20 -0600</pubDate><comments>https://lobste.rs/s/{i}/x</comments></item>")


class Routed:
    def __init__(self, titles_urls, pages, delay=0.0):
        items = "".join(ITEM.format(t=t, u=u, i=f"a{n}") for n, (t, u) in enumerate(titles_urls))
        self.feed, self.pages, self.delay = FEED_TMPL.format(items=items).encode(), pages, delay

    def fetch(self, url):
        if url == "https://lobste.rs/rss":
            return self.feed
        time.sleep(self.delay)
        page = self.pages[url]
        if isinstance(page, Exception):
            raise page
        return page


def run(titles_urls, pages, **kw):
    q = []
    kept = lobsters.fetch_checked(Routed(titles_urls, pages, **kw), "https://lobste.rs/rss", quarantine=q)
    return [c.title for c in kept], q


def test_page_with_one_tech_word_is_not_quarantined():
    html = b"<html><p>Fibonacci numbers and a small algorithm to compute them quickly</p></html>"
    kept, q = run([("Fibonacci numbers quickly", "https://f.test/fib")], {"https://f.test/fib": html})
    assert kept == ["Fibonacci numbers quickly"] and q == []


@pytest.mark.parametrize("err", [FetchError("u: SSL certificate verify failed", kind="ssl"),
                                 FetchError("u: HTTP 403", kind="blocked")])
def test_environmental_failures_are_kept_unverified_not_quarantined(err):
    kept, q = run([("Some story about code", "https://e.test/x")], {"https://e.test/x": err})
    assert kept == ["Some story about code"] and q == []


def test_real_dead_link_still_quarantined():
    kept, q = run([("Dead story about code", "https://d.test/x")], {"https://d.test/x": FetchError("u: HTTP 404")})
    assert kept == [] and "unreachable" in q[0]


def test_link_checks_run_in_parallel_and_keep_feed_order():
    n = 12
    tu = [(f"Story {i} about code and api", f"https://p.test/{i}") for i in range(n)]
    pages = {u: b"<p>story code api about</p>" for _, u in tu}
    start = time.monotonic()
    kept, q = run(tu, pages, delay=0.2)
    assert time.monotonic() - start < 0.2 * n / 3  # serial would be 2.4s
    assert kept == [t for t, _ in tu]


def test_http_marks_ssl_and_403_errors():
    def ssl_opener(req, timeout):
        raise urllib.error.URLError(ssl.SSLCertVerificationError("unable to get local issuer certificate"))

    with pytest.raises(FetchError) as e:
        Http(opener=ssl_opener, sleep=lambda s: None).fetch("https://a.test/")
    assert e.value.kind == "ssl"

    def forbidden(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)

    with pytest.raises(FetchError) as e:
        Http(opener=forbidden, sleep=lambda s: None).fetch("https://a.test/")
    assert e.value.kind == "blocked"
