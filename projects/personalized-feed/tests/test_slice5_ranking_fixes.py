"""Slice 5: ranking-engineer cycle-7 eval (MF1 false positives, confirmed-low tiers) + QA D-4 (Lobsters links).
Offline: synthetic test-only candidates and canned pages; nothing touches the network."""
from datetime import date

from conftest import FakeHttp
from rank_helpers import PROFILE, cand, empty_ledger, good_pool
from pfeed import rank
from pfeed.adapters import lobsters
from pfeed.http import FetchError
from pfeed.rank_data import DEFAULT_WEIGHTS

TODAY = date(2026, 11, 19)
RECALC_BODY = ("Recalc is a spreadsheet where every cell is a Claude Code terminal. We ran evals on layout "
               "benchmark runs and evaluation of cell scheduling; useful for any team.")


def score(c):
    return rank.score(c, PROFILE, DEFAULT_WEIGHTS, set(), TODAY)


def recalc():
    return cand("Show HN: Recalc - a spreadsheet of Claude Code terminals", "https://recalc.test/", "HN", "article",
                RECALC_BODY, points=120, comments=30)


# ---- MF1a: provenance ----
def test_matches_record_keyword_and_origin():
    s = score(cand("o2/agent-evals", "https://github.com/o2/agent-evals", summary="evaluation harness", stars=300))
    origins = {m["keyword"]: m["origin"] for m in s.matches}
    assert origins["evals"] == "title" and origins["evaluation"] == "summary"
    assert all(set(m) == {"keyword", "origin"} for m in s.matches)


# ---- MF1b: summary-only cap for HN / Lobsters ----
def test_recalc_weak_body_hit_is_not_credited_to_evals():
    c = cand("Show HN: Recalc - a spreadsheet of Claude Code terminals", "https://recalc.test/", "HN", "article",
             "Every cell is a Claude Code terminal; we ran a benchmark of the layout engine.", points=120)
    s = score(c)
    assert not s.interest.startswith("evals") and s.signals["interest-match"] == 0


def test_recalc_strong_body_hits_are_capped_at_3():
    s = score(recalc())
    assert s.signals["interest-match"] == 3
    assert all(m["origin"] == "summary" for m in s.matches)


def test_same_text_from_a_repo_is_not_capped():
    s = score(cand("o9/spreadsheet-terminals", "https://github.com/o9/spreadsheet-terminals", summary=RECALC_BODY, stars=300))
    assert s.signals["interest-match"] > 3 or s.interest.startswith("evals")


def test_hn_title_hit_is_not_capped():
    s = score(cand("Show HN: agent evals harness", "https://x.test/h", "HN", "article", "details", points=80))
    assert s.signals["interest-match"] == 5


# ---- MF1c: pdf / extraction weak ----
def test_pdf_alone_is_weak():
    s = score(cand("Catching prompt injections hidden in PDFs", "https://x.test/p", "Lobsters", "article"))
    assert s.signals["interest-match"] <= 2 and not s.strong


def test_pdf_plus_extraction_still_weak_but_structured_extraction_is_strong():
    weak = score(cand("pdf extraction notes", "https://x.test/q", "blog", "article"))
    assert not weak.strong
    strong = score(cand("Structured extraction from pdf", "https://x.test/r", "blog", "article"))
    assert strong.strong


def test_pdf_injection_piece_does_not_beat_good_items(tmp_path):
    pool = good_pool() + [recalc(), cand("Catching prompt injections hidden in PDFs", "https://x.test/p",
                                         "Lobsters", "article", "pdf extraction injection")]
    sel = rank.select(pool, PROFILE, DEFAULT_WEIGHTS, empty_ledger(tmp_path), today=TODAY)
    assert not any("Recalc" in s.candidate.title for s in sel.items)
    assert not any("injections" in s.candidate.title for s in sel.items)


# ---- confirmed-low tiers (QA D-5) ----
def test_confirmed_low_safety_scores_2_and_is_eligible():
    c = cand("o5/sae-interpretability", "https://github.com/o5/sae-interpretability",
             summary="sparse autoencoder interpretability toolkit", stars=300)
    s = score(c)
    assert s.interest.startswith("AI safety") and s.signals["interest-match"] == 2 and s.strong


def test_confirmed_low_rust_with_llm_term_scores_2_without_context_none():
    s = score(cand("o4/candle-llm", "https://github.com/o4/candle-llm", summary="rust llm inference with candle", stars=300))
    assert s.signals["interest-match"] >= 2
    none = score(cand("Rust tokio tips", "https://blog.test/r", "blog", "article", "cargo and tokio"))
    assert none.signals["interest-match"] == 0


def test_inferred_low_stays_at_1_and_never_explores(tmp_path):
    s = score(cand("o6/retry-hardening", "https://github.com/o6/retry-hardening",
                   summary="retry fallback incident hardening for reliability", stars=300))
    assert s.interest.startswith("production reliability") and s.signals["interest-match"] == 1
    assert not rank._exploration_eligible(s)


def test_exploration_requires_strong_match():
    weak = score(cand("o7/dashboard", "https://github.com/o7/dashboard", summary="telemetry", stars=300))
    assert weak.signals["interest-match"] >= 2 and not weak.strong
    assert not rank._exploration_eligible(weak)


# ---- QA D-4: Lobsters link sanity ----
FEED = """<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>Catching prompt injections hidden in PDFs</title><link>https://tomclancy.test/joshua-judges-ruth.html</link>
<author>x via y</author><pubDate>Wed, 18 Nov 2026 08:45:20 -0600</pubDate><comments>https://lobste.rs/s/aaaaaa/x</comments></item>
<item><title>Tracing LLM inference latency in Rust</title><link>https://good.test/tracing</link>
<author>x via y</author><pubDate>Wed, 18 Nov 2026 08:45:20 -0600</pubDate><comments>https://lobste.rs/s/bbbbbb/y</comments></item>
<item><title>Dead link story about code</title><link>https://dead.test/x</link>
<author>x via y</author><pubDate>Wed, 18 Nov 2026 08:45:20 -0600</pubDate><comments>https://lobste.rs/s/cccccc/z</comments></item>
</channel></rss>"""
PAGES = {
    "https://tomclancy.test/joshua-judges-ruth.html": b"<html><title>Joshua, Judges, Ruth</title><p>Sermon notes on the book of Judges and Ruth.</p></html>",
    "https://good.test/tracing": b"<html><h1>Tracing LLM inference latency in Rust</h1><pre>fn main(){}</pre><p>code and benchmark of model inference</p></html>",
}


class RoutedHttp:
    def __init__(self):
        self.urls = []

    def fetch(self, url):
        self.urls.append(url)
        if url == "https://lobste.rs/rss":
            return FEED.encode()
        if url in PAGES:
            return PAGES[url]
        raise FetchError(f"{url}: HTTP 404")


def test_lobsters_pdf_item_quarantined_and_good_item_kept():
    q = []
    kept = lobsters.fetch_checked(RoutedHttp(), "https://lobste.rs/rss", quarantine=q)
    assert [c.title for c in kept] == ["Tracing LLM inference latency in Rust"]
    assert any("injections" in m and "technical" in m for m in q)
    assert any("Dead link" in m and "unreachable" in m for m in q)


def test_page_problem_flags_title_mismatch():
    html = "<p>code api model software algorithm benchmark but about something else entirely</p>"
    assert lobsters.page_problem("Quantum widgets frobnicate zebras", html) == "linked page does not match the title"
