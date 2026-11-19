"""Slice 7: lone generic keywords are weak matches; why-lines never cite weak matches; exploration can carry low-weight interests."""
from datetime import date

import pytest

from rank_helpers import PROFILE, cand, empty_ledger
from pfeed import rank
from pfeed.rank_data import DEFAULT_WEIGHTS
from pfeed.render import why_line

TODAY = date(2026, 11, 19)


def score(c):
    return rank.score(c, PROFILE, DEFAULT_WEIGHTS, set(), TODAY)


@pytest.mark.parametrize("title", ["Our new agent", "Why every LLM matters", "AI agents everywhere"])
def test_lone_generic_keyword_is_weak_even_in_title(title):
    s = score(cand(title, "https://github.com/o/x", stars=500, summary="a thing"))
    assert s.signals["interest-match"] <= 2 and not s.strong


def test_second_distinct_keyword_backs_a_generic_one():
    s = score(cand("An agent with tool use", "https://github.com/o/y", stars=500))
    assert s.signals["interest-match"] >= 3 and s.strong


def test_why_line_does_not_cite_weak_or_generic_matches():
    s = score(cand("Agent tracing with opentelemetry", "https://github.com/o/z", stars=500))
    line = why_line(s)
    assert "matched:" in line and "opentelemetry" in line and "agent" not in line.split("matched:")[1]
    weak = score(cand("Our new agent", "https://github.com/o/x", stars=500))
    assert "matched" not in why_line(weak)


def test_exploration_slot_can_carry_low_weight_interests():
    for title, summary, interest in [("rust-candle-demo", "rust inference demo with candle for llm", "rust tooling"),
                                     ("jailbreak-lab", "interpretability and jailbreak experiments", "AI safety")]:
        c = cand(title, f"https://github.com/o/{title}", stars=300, summary=summary)
        s = score(c)
        assert s.interest.lower().startswith(interest.lower()) and rank._exploration_eligible(s), title
        pick = rank._exploration_pick([s], PROFILE, 3, 5, 0)
        assert pick is s


def test_hands_on_floor_warning_is_soft():
    text = next(w for *_, w in rank.RELAXATIONS if "hands-on floor" in w)
    assert "less tryable than usual" in text
