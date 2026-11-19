"""Slice 4: ranking-engineer cycle-6 eval + QA D-1 (offline, synthetic test-only candidates)."""
from datetime import date

import pytest

from rank_helpers import PROFILE, cand, empty_ledger, good_pool
from pfeed import rank
from pfeed.ledger import Ledger, name_key
from pfeed.rank_data import DEFAULT_WEIGHTS

W = DEFAULT_WEIGHTS
TODAY = date(2026, 11, 19)


def run(pool, tmp_path, ledger=None):
    return rank.select(pool, PROFILE, W, ledger or empty_ledger(tmp_path), today=TODAY)


def urls(sel):
    return [s.candidate.url for s in sel.items]


def article(title, url, summary="", source="Some Blog", stype="blog"):
    return cand(title, url, stype, "article", summary, source=source)


# ---- 5. QA D-1: ArtCraft ----
ARTCRAFT = "AI Ambition: ArtCraft Cloned Photoshop and shipped it with Rust"


def test_artcraft_title_is_excluded_as_ai_art():
    c = article(ARTCRAFT, "https://latent.space/p/artcraft", source="Latent Space", stype="Substack")
    rules, _ = rank.active_exclude_rules(PROFILE)
    assert rank.exclude_reason(c, rules) == "ai-art"


@pytest.mark.parametrize("title", ["Photoshop plugin written with an LLM", "Midjourney vs local image generation",
                                   "An AI art generator in 100 lines"])
def test_ai_art_keywords_widened(title):
    rules, _ = rank.active_exclude_rules(PROFILE)
    assert rank.exclude_reason(article(title, "https://blog.test/x"), rules) == "ai-art"


def test_ai_art_does_not_fire_on_ai_artifacts_or_articles():
    rules, _ = rank.active_exclude_rules(PROFILE)
    for t in ("Tracing AI artifacts in agent pipelines", "A tutorial article on agent evals"):
        assert rank.exclude_reason(article(t, "https://blog.test/y", "step-by-step tutorial"), rules) is None


def test_artcraft_is_not_delivered(tmp_path):
    art = article(ARTCRAFT, "https://latent.space/p/artcraft", source="Latent Space", stype="Substack")
    assert art.url not in urls(run(good_pool() + [art], tmp_path))


# ---- 1. clone clusters ----
def clones(a="a", b="b", stars=62):
    return [cand(f"{o}/ai--manus2.0", f"https://github.com/{o}/ai--manus2.0", summary="agent framework tool use",
                 stars=stars) for o in (a, b)]


def test_same_name_clones_yield_one_item(tmp_path):
    pool = [p for p in good_pool() if "agentflow" not in p.title] + clones()
    sel = run(pool, tmp_path)
    assert sum("ai--manus2.0" in u for u in urls(sel)) == 1
    assert sel.stats["name_clone_dupes"] == 1


def test_clone_winner_is_higher_stars_then_earlier_created_then_owner(tmp_path):
    hi = cand("z/ai--manus2.0", "https://github.com/z/ai--manus2.0", summary="agent", stars=90)
    lo = cand("a/ai--manus2.0", "https://github.com/a/ai--manus2.0", summary="agent", stars=62)
    assert rank.drop_name_clones([lo, hi], {}) == [hi]
    old = cand("z/ai--manus2.0", "https://github.com/z/ai--manus2.0", stars=62, created_at="2026-11-10T00:00:00Z")
    new = cand("a/ai--manus2.0", "https://github.com/a/ai--manus2.0", stars=62, created_at="2026-11-15T00:00:00Z")
    assert rank.drop_name_clones([new, old], {}) == [old]
    b, a = clones("b", "a")
    assert rank.drop_name_clones([b, a], {}) == [a]  # all tied: owner alphabetical


def test_generic_names_are_not_merged(tmp_path):
    a = cand("a/demo", "https://github.com/a/demo", summary="agent", stars=100)
    b = cand("b/demo", "https://github.com/b/demo", summary="agent", stars=100)
    stats = {}
    assert rank.drop_name_clones([a, b], stats) == [a, b] and stats["name_clone_dupes"] == 0
    assert name_key("https://github.com/a/agents") is None and name_key("https://github.com/a/short") is None
    assert name_key("https://github.com/a/v2.1") == "name:v2.1"  # digit/./-/_ marks a distinctive name


def test_delivered_repo_covers_same_name_clone_on_later_day(tmp_path):  # D7
    ledger = Ledger(tmp_path / "ledger.md")
    first, second = clones()
    ledger.append("2026-11-18", "01", [first])
    assert ledger.seen(second)
    assert Ledger(tmp_path / "ledger.md").seen(second)  # survives reload: derived from the stored URL
    pool = [p for p in good_pool() if "agentflow" not in p.title] + [second]
    sel = run(pool, tmp_path, ledger)
    assert second.url not in urls(sel) and sel.stats["ledger_seen"] == 1


def test_ledger_does_not_cover_generic_same_name(tmp_path):
    ledger = Ledger(tmp_path / "ledger.md")
    ledger.append("2026-11-18", "01", [cand("a/demo", "https://github.com/a/demo", stars=100)])
    assert not ledger.seen(cand("b/demo", "https://github.com/b/demo", stars=100))


# ---- 2. strong / weak keywords and the interest-match floor ----
def test_lone_production_hit_scores_at_most_1():
    c = article("Why production matters", "https://blog.test/p")
    assert rank.match_interest(c, PROFILE)[2] <= 1


def test_rust_headline_without_llm_term_does_not_match():
    c = article("Why I rewrote my blog in Rust", "https://x.substack.test/p", source="Some Newsletter", stype="Substack")
    assert rank.match_interest(c, PROFILE)[2] <= 1


def test_rust_with_llm_term_or_as_repo_still_matches():
    assert rank.match_interest(article("Rust for LLM inference", "https://blog.test/r"), PROFILE)[0] == "rust tooling"
    repo = cand("o/candle-llm-runner", "https://github.com/o/candle-llm-runner", summary="candle-based LLM runner", stars=80)
    assert rank.match_interest(repo, PROFILE)[0] != ""
    plain = cand("o/rustfmt-thing", "https://github.com/o/rustfmt-thing", summary="rust formatter", stars=80)
    assert rank.match_interest(plain, PROFILE)[0] == "rust tooling"  # repos are exempt from the context rule


def test_slack_does_not_match_sla_and_documentation_not_document():
    slack = article("Slack announces new bot APIs", "https://blog.test/s")
    assert rank.match_interest(slack, PROFILE)[0] == ""
    docs = article("Our documentation site is live", "https://blog.test/d")
    assert rank.match_interest(docs, PROFILE)[0] == ""
    assert rank.match_interest(article("SLAs for LLM apps", "https://blog.test/sl"), PROFILE)[0].startswith("production reliability")


def test_weak_keyword_in_title_alone_is_not_strong_but_second_hit_is():
    one = article("Retrieval notes", "https://blog.test/a")  # weak only
    two = article("Retrieval with rerank", "https://blog.test/b")  # two distinct hits
    strong = article("Structured extraction notes", "https://blog.test/c")  # one strong keyword in title
    assert rank.match_interest(one, PROFILE)[2] == 1  # slice 6: weak-only scores 1
    assert rank.match_interest(two, PROFILE)[2] == 3
    assert rank.match_interest(strong, PROFILE)[2] == 3


def test_stems_still_prefix_match():
    c = article("Quantization and orchestration at scale", "https://blog.test/q")
    assert rank.match_interest(c, PROFILE)[0] in ("running models locally / small models / quantization",
                                                  "agent frameworks / orchestration / tool use")


def test_match_one_item_never_fills_main_slot(tmp_path):
    filler = article("Why production matters", "https://blog.test/p", "production", source="Latent Space")
    sel = run(good_pool() + [filler], tmp_path)
    assert filler.url not in urls(sel)
    assert all(s.signals["interest-match"] >= 3 for s in sel.items)


def test_weak_matches_are_never_admitted_even_on_the_last_rung(tmp_path):
    pool = [cand("o1/agentflow", "https://github.com/o1/agentflow", summary="agent framework with tool use", stars=900),
            article("Why production matters", "https://blog.test/p", "production", source="Latent Space"),
            cand("Prod hardening on HN", "https://news.ycombinator.com/item?id=9", "HN", "discussion",
                 "production notes", comments=120, points=200)]
    sel = run(pool, tmp_path)
    assert sel.items == [] and any("ALARM" in w for w in sel.warnings)  # slice 6: ship nothing rather than weak items


# ---- 3. exploration quality ----
def _explore_pool(extra):
    return [p for p in good_pool() if "candle" not in p.title and "extraction" not in p.title.lower()] + extra


def test_exploration_not_a_weak_match(tmp_path):
    weak = article("Rust for LLM tooling", "https://x.substack.test/r", "rust llm", source="Some Newsletter", stype="Substack")
    sel = run(_explore_pool([weak]), tmp_path)
    assert not any(s.exploration and s.candidate.url == weak.url for s in sel.items)


def test_exploration_needs_interest_match_3_and_a_tryable_type(tmp_path):
    obs_repo = cand("o5/otel-llm-tracer", "https://github.com/o5/otel-llm-tracer",
                    summary="opentelemetry tracing for llm pipelines", stars=300)
    sel = run(_explore_pool([obs_repo]), tmp_path)
    picks = [s for s in sel.items if s.exploration]
    assert picks and picks[0].signals["interest-match"] >= 3 and picks[0].candidate.url == obs_repo.url


def test_substack_headline_is_not_exploration_even_if_tryable(tmp_path):
    sub = article("OpenTelemetry tracing for llm apps: a tutorial", "https://x.substack.test/o",
                  "step-by-step tutorial on tracing with opentelemetry", source="Some Newsletter", stype="Substack")
    sel = run(_explore_pool([sub]), tmp_path)
    assert not any(s.exploration and s.candidate.url == sub.url for s in sel.items)


def test_empty_exploration_slot_warns_instead_of_weak_fill(tmp_path):
    pool = [p for p in good_pool() if p.item_type != "paper" and "candle" not in p.title and "Tracing" not in p.title]
    pool.append(cand("o6/agent-evals-2", "https://github.com/o6/agent-evals-2", summary="evals for llm agents", stars=400))
    pool.append(cand("Local gguf notes", "https://lobste.rs/s/abc", "Lobsters", "discussion", "quantization with gguf", comments=60))
    sel = run(pool, tmp_path)
    assert not any(s.exploration for s in sel.items)
    assert any("no exploration" in w for w in sel.warnings)


# ---- 4. star gates ----
@pytest.mark.parametrize("stars,dropped", [(12, True), (24, True), (25, False), (49, False)])
def test_min_repo_stars_is_25(tmp_path, stars, dropped):
    c = cand("o1/agentflow", "https://github.com/o1/agentflow", summary="agent framework with tool use", stars=stars)
    sel = run([p for p in good_pool() if "agentflow" not in p.title] + [c], tmp_path)
    assert (sel.stats["excluded"].get("zero-traction repo", 0) == 1) is dropped


def test_at_most_one_sub_50_star_repo_per_edition(tmp_path):
    tails = [cand(f"t{i}/tail-agent-{i}", f"https://github.com/t{i}/tail-agent-{i}",
                  summary="agent framework tool use evals for llm", stars=30 + i) for i in range(4)]
    pool = [p for p in good_pool() if "candle" not in p.title] + tails
    sel = run(pool, tmp_path)
    assert sum(1 for s in sel.items if s.candidate.extras.get("stars", 999) < 50) <= 1
    assert sel.items


def test_notable_stars_threshold_reverted_to_5000():
    from pfeed import rank_data
    assert rank_data.NOTABLE_REPO_STARS == 5000 and rank_data.MIN_REPO_STARS == 25
    big = cand("o/x", "https://github.com/o/x", stars=3469)
    assert rank.source_quality(big, TODAY) == 5 and rank.thought_leadership(big) == 1


def test_weights_unchanged():
    assert W == {"interest-match": 0.35, "novelty": 0.20, "hands-on": 0.20, "thought-leadership": 0.15,
                 "source-quality": 0.10}
