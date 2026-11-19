import pytest

from rank_helpers import PROFILE, cand, empty_ledger, good_pool
from pfeed import rank
from pfeed.ledger import Ledger
from pfeed.rank_data import DEFAULT_WEIGHTS
from pfeed.profile import Interest, Profile

W = DEFAULT_WEIGHTS


def run(pool, tmp_path, profile=PROFILE, ledger=None):
    return rank.select(pool, profile, W, ledger or empty_ledger(tmp_path))


def test_default_weights_sum_to_one():
    assert sum(W.values()) == pytest.approx(1.0)


# ---- excludes ----
@pytest.mark.parametrize("c,reason", [
    (cand("Bitcoin agent", "https://x.test/1", "blog", "article", "crypto trading agent code github.com/a/b"), "crypto"),
    (cand("7 ways AI will help", "https://x.test/2", "blog", "article", "agent"), "listicle"),
    (cand("Acme raises $50M for agents", "https://x.test/3", "blog", "article", "agent platform"), "funding"),
    (cand("Acme launches agent platform", "https://x.test/4", "blog", "article", "announces new agent product"),
     "announcement with nothing to try"),
    (cand("o/awesome-agents", "https://github.com/o/awesome-agents", summary="list"), "awesome-list"),
    (cand("A paper", "https://arxiv.org/abs/2601.1", "arXiv", "paper", "agents"), "paper without code"),
    (cand("Evals tutorial", "https://blog.langchain.com/p", "blog", "article", "evals, sign up for free trial",
          source="LangChain blog"), "vendor post with product CTA"),
])
def test_exclude_rules(c, reason):
    rules, _ = rank.active_exclude_rules(PROFILE)
    assert rank.exclude_reason(c, rules) == reason


def test_announcement_with_repo_is_not_excluded():
    c = cand("Launches agent lib", "https://x.test/5", "blog", "article", "announcing it, code at github.com/a/b")
    rules, _ = rank.active_exclude_rules(PROFILE)
    assert rank.exclude_reason(c, rules) is None


def test_unknown_profile_exclude_is_warned_not_silent():
    p = Profile("u", PROFILE.interests, ["weird new exclude"])
    rules, warnings = rank.active_exclude_rules(p)
    assert not rules and "weird new exclude" in warnings[0]


# ---- interest matching ----
def test_best_single_interest_highest_tier_wins_never_summed():
    c = cand("Demo", "https://github.com/a/b", summary="multi-agent demo with otel tracing observability trace", stars=1)
    name, tier, sig = rank.match_interest(c, PROFILE)
    assert name.startswith("agent frameworks") and tier == "high" and sig == 5


def test_weight_zero_interest_never_matches():
    c = cand("Demand forecasting", "https://github.com/a/c", summary="time series forecasting")
    assert rank.match_interest(c, PROFILE) == ("", "", 0)


def test_inferred_interest_capped_to_low_tier():
    c = cand("Doc pipeline", "https://github.com/a/d", summary="invoice document handling")
    name, tier, _ = rank.match_interest(c, PROFILE)
    assert name.startswith("document-processing") and tier == "low"


def test_weak_match_lowers_signal_by_one_but_not_past_tier():
    c = cand("Something", "https://github.com/a/e", summary="a small note about orchestration")  # 1 hit, not in title
    assert rank.match_interest(c, PROFILE)[2] == 4


# ---- signals ----
def test_hands_on_heuristics():
    assert rank.hands_on(cand("r", "https://github.com/a/r")) == 5
    assert rank.hands_on(cand("p", "https://arxiv.org/abs/1", "arXiv", "paper", repo_links=["https://github.com/a/b"])) == 4
    assert rank.hands_on(cand("d", "https://news.ycombinator.com/item?id=2", "HN", "discussion", comments=80)) == 3
    assert rank.hands_on(cand("a", "https://x.test/a", "blog", "article", "just opinions")) == 2


def test_notable_author_and_stars_drive_thought_leadership():
    assert rank.thought_leadership(cand("x", "https://hamel.dev/x", "blog", "article", source="Hamel Husain")) == 5
    assert rank.thought_leadership(cand("x", "https://github.com/a/big", stars=9000)) == 3
    assert rank.thought_leadership(cand("x", "https://github.com/a/small", stars=10)) == 1


def test_novelty_drops_for_recently_delivered_domain(tmp_path):
    led = empty_ledger(tmp_path)
    led.append("2026-11-18", "01", [cand("old", "https://github.com/o1/old")])
    s = rank.score(cand("new", "https://github.com/o1/new", summary="agent"), PROFILE, W, rank.recent_domains(led))
    assert s.signals["novelty"] == 3
    s2 = rank.score(cand("new", "https://github.com/zz/new", summary="agent"), PROFILE, W, rank.recent_domains(led))
    assert s2.signals["novelty"] == 5


def test_total_is_weighted_sum_and_signals_recorded():
    s = rank.score(cand("o/agents", "https://github.com/o/agents", summary="agent framework tool use"), PROFILE, W, set())
    assert s.total == pytest.approx(sum(W[k] * s.signals[k] for k in W), abs=1e-4)
    assert set(s.signals) == set(W)


# ---- selection guardrails ----
def test_selection_meets_d2_size_and_has_one_exploration(tmp_path):
    sel = run(good_pool(), tmp_path)
    assert 3 <= len(sel.items) <= 5
    assert len({s.candidate.source_type for s in sel.items}) >= 3
    assert sum(s.exploration for s in sel.items) == 1


def test_interest_cap_no_echo_chamber(tmp_path):
    pool = [cand(f"o{i}/agent{i}", f"https://github.com/o{i}/agent{i}", summary="agent framework agentic", stars=100 + i)
            for i in range(8)] + good_pool()[3:]
    sel = run(pool, tmp_path)
    counts = {}
    for s in sel.items:
        counts[s.interest] = counts.get(s.interest, 0) + 1
    assert max(counts.values()) <= 2


def test_one_per_cluster_and_per_domain(tmp_path):
    pool = good_pool() + [cand("o1/other", "https://github.com/o1/other", summary="agent framework tool use")]
    sel = run(pool, tmp_path)
    doms = [rank.domain_key(s.candidate) for s in sel.items if rank.domain_key(s.candidate)]
    assert len(doms) == len(set(doms))


def test_ledger_repeats_never_selected(tmp_path):
    led = empty_ledger(tmp_path)
    pool = good_pool()
    led.append("2026-11-18", "01", pool[:1])
    sel = run(pool, tmp_path, ledger=led)
    assert all(s.candidate.canonical_url != pool[0].canonical_url for s in sel.items)
    assert sel.stats["ledger_seen"] == 1


def test_homogeneous_pool_swaps_in_missing_type(tmp_path):
    repos = [cand(f"o{i}/x{i}", f"https://github.com/o{i}/x{i}", summary=s) for i, s in enumerate(
        ["agent framework tool use", "agent evals evaluation", "gguf quantization llama.cpp", "rust candle", "tracing otel"])]
    pool = repos + [good_pool()[3], good_pool()[4]]
    sel = run(pool, tmp_path)
    assert len({s.candidate.source_type for s in sel.items}) >= 3


def test_single_source_type_ships_nothing_with_alarm(tmp_path):
    pool = [cand(f"o{i}/agent{i}", f"https://github.com/o{i}/agent{i}", summary="agent framework") for i in range(6)]
    sel = run(pool, tmp_path)
    assert sel.items == [] and any("ALARM" in w for w in sel.warnings)


def test_relaxation_to_fewer_items_warns(tmp_path):
    sel = run(good_pool()[:4] + good_pool()[4:5], tmp_path)  # only 5 candidates, caps force relaxation
    assert sel.items and (len(sel.items) == 5 or any("relaxed" in w for w in sel.warnings))


def test_no_exploration_candidate_ships_without_and_reports(tmp_path):
    pool = [p for p in good_pool() if "candle" not in p.title and "extraction" not in p.title.lower()]
    sel = run(pool, tmp_path)
    if not any(s.exploration for s in sel.items):
        assert any("exploration" in w for w in sel.warnings)


def test_exploration_is_outside_top_interests_and_not_inferred(tmp_path):
    sel = run(good_pool(), tmp_path)
    pick = next(s for s in sel.items if s.exploration)
    assert pick.interest.split()[0] not in ("agent", "evals", "running") and pick.signals["hands-on"] >= 4


def test_deterministic(tmp_path):
    a = run(good_pool(), tmp_path)
    b = run(list(reversed(good_pool())), tmp_path)
    assert [s.candidate.url for s in a.items] == [s.candidate.url for s in b.items]
