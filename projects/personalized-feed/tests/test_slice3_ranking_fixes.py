"""Slice 3: critic cycle-3 required changes 1-6 (offline, synthetic test-only candidates)."""
from datetime import date

import pytest

from rank_helpers import PROFILE, cand, empty_ledger, good_pool
from pfeed import rank
from pfeed.rank_data import DEFAULT_WEIGHTS

W = DEFAULT_WEIGHTS
TODAY = date(2026, 11, 19)


def run(pool, tmp_path, ledger=None):
    return rank.select(pool, PROFILE, W, ledger or empty_ledger(tmp_path), today=TODAY)


# ---- 1. exploration needs a real matched non-top interest ----
def test_unmatched_repo_never_becomes_exploration_pick(tmp_path):
    junk = cand("o9/fresh-thing", "https://github.com/o9/fresh-thing", summary="a brand new thing", stars=900)
    pool = [p for p in good_pool() if "candle" not in p.title and "extraction" not in p.title.lower()] + [junk]
    sel = run(pool, tmp_path)
    assert all(s.interest for s in sel.items) and junk.url not in [s.candidate.url for s in sel.items]
    assert all(s.interest for s in sel.items if s.exploration)


# ---- 2. traction ----
@pytest.mark.parametrize("stars,q", [(5, 1), (10, 2), (49, 2), (50, 3), (199, 3), (200, 4), (999, 4), (1000, 5)])
def test_github_source_quality_ladder(stars, q):
    assert rank.source_quality(cand("o/x", "https://github.com/o/x", stars=stars), TODAY) == q


def test_young_repo_with_velocity_counts_as_4():
    c = cand("o/hot", "https://github.com/o/hot", stars=60, created_at="2026-11-15T00:00:00Z")
    old = cand("o/old", "https://github.com/o/old", stars=60, created_at="2026-01-15T00:00:00Z")
    assert rank.source_quality(c, TODAY) == 4 and rank.source_quality(old, TODAY) == 3


def test_hn_linked_repo_uses_points_when_stars_unknown():
    c = cand("o/x", "https://github.com/o/x", "HN", "repo", points=250)
    assert rank.source_quality(c, TODAY) == 4
    c = cand("o/x", "https://github.com/o/x", "HN", "repo", points=20)
    assert rank.source_quality(c, TODAY) == 2


def test_thought_leadership_notable_repo_at_1000_stars():
    assert rank.thought_leadership(cand("o/x", "https://github.com/o/x", stars=1000)) == 3
    assert rank.thought_leadership(cand("o/x", "https://github.com/o/x", stars=999)) == 1


def test_zero_traction_repo_dropped_unless_backed_by_another_item(tmp_path):
    tiny = cand("o1/agentflow", "https://github.com/o1/agentflow", summary="agent framework tool use", stars=2)
    pool = [p for p in good_pool() if "agentflow" not in p.title]
    assert tiny.url not in [s.candidate.url for s in run(pool + [tiny], tmp_path).items]
    assert run(pool + [tiny], tmp_path).stats["excluded"]["zero-traction repo"] == 1
    paper = cand("Agent paper", "https://arxiv.org/abs/2601.00009", "arXiv", "paper", "agent tool use",
                 repo_links=["https://github.com/o1/agentflow"])
    sel = run(pool + [tiny, paper], tmp_path)
    assert sel.stats["excluded"].get("zero-traction repo", 0) == 0


# ---- 3. tryable words are whole words ----
def test_quarterly_report_announcement_is_still_excluded():
    c = cand("Acme announces quarterly report", "https://x.test/q", "blog", "article",
             "we decode the barcode of repository growth? no: announcing numbers in our report, encoded")
    rules, _ = rank.active_exclude_rules(PROFILE)
    assert not rank._tryable(cand("t", "https://x.test/q2", "blog", "article", "quarterly report, decode, barcode, encoded"))
    assert rank.exclude_reason(cand("Acme announces results", "https://x.test/q3", "blog", "article",
                                    "announces quarterly report, decode barcode"), rules) == "announcement with nothing to try"
    assert rank._tryable(cand("t", "https://x.test/q4", "blog", "article", "clone the repository and run it"))
    assert rank._tryable(cand("t", "https://x.test/q5", "blog", "article", "a tutorial for you"))
    assert c  # constructed fine


# ---- 4. top-3 interests cap ----
def test_at_most_three_of_five_from_top_three_interests(tmp_path):
    def many(prefix, text, n=3):
        return [cand(f"{prefix}{i}/{prefix}{i}", f"https://github.com/{prefix}{i}/{prefix}{i}", summary=text, stars=500) for i in range(n)]
    pool = (many("agt", "agent framework tool use") + many("evl", "evals evaluation benchmark")
            + many("loc", "gguf quantization llama.cpp") + good_pool()[3:])
    sel = run(pool, tmp_path)
    top = {"agent frameworks", "evals for llm", "running models locally"}
    in_top = [s for s in sel.items if any(s.interest.startswith(t) for t in top)]
    assert len(sel.items) == 5 and len(in_top) <= 3


# ---- 5. topic fatigue ----
def test_interest_in_three_of_last_five_editions_gets_novelty_3(tmp_path):
    led = empty_ledger(tmp_path)
    for d in range(1, 4):
        led.append(f"2026-11-0{d}", "01", [cand(f"Agent tool use {d}", f"https://x{d}.test/a", "blog", "article")])
    led.append("2026-11-04", "01", [cand("Unrelated gardening", "https://g.test/a", "blog", "article")])
    fat = rank.fatigued_interests(led, PROFILE)
    assert any(name.startswith("agent frameworks") for name in fat)
    c = cand("o/newagent", "https://github.com/o/newagent", summary="agent framework tool use", stars=500)
    assert rank.score(c, PROFILE, W, set(), TODAY, fat).signals["novelty"] == 3
    assert rank.score(c, PROFILE, W, set(), TODAY).signals["novelty"] == 5


def test_two_of_five_editions_is_not_fatigue(tmp_path):
    led = empty_ledger(tmp_path)
    for d in range(1, 3):
        led.append(f"2026-11-0{d}", "01", [cand(f"Agent tool use {d}", f"https://x{d}.test/a", "blog", "article")])
    assert rank.fatigued_interests(led, PROFILE) == set()


# ---- 6. report ----
def test_report_shows_signals_and_rung(tmp_path):
    from pfeed.pipeline import format_report
    sel = run(good_pool(), tmp_path)
    assert "rung" in sel.stats
    text = format_report({"sources": [], "fetched": 7, "stale_dropped": 0, "selection": sel, "path": None})
    assert "interest-match=" in text and "hands-on=" in text and "rung" in text
