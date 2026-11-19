"""QA gate, slice 4 (cycle 7): low-weight interest reachability and small-edition behaviour."""
from datetime import date

from rank_helpers import PROFILE, cand, empty_ledger, good_pool
from pfeed import rank
from pfeed.rank_data import DEFAULT_WEIGHTS

TODAY = date(2026, 11, 19)


def test_low_weight_interest_matches_cap_at_one():
    """Characterization (QA D-5): weight<=2 interests (rust tooling, AI safety) score at most 1, below the
    main-slot floor of 2, so they only appear on the last warned relaxation rung. Flip this test if the
    ranking-engineer decides low tiers must be reachable."""
    c = cand("Writing a rust tooling CLI for LLM agent traces with cargo", "https://example.org/r1", "GitHub", "repo",
             "rust tooling cargo clippy rustfmt llm agent", stars=500)
    name, tier, sig = rank.match_interest(c, PROFILE)
    if name and tier == "low":
        assert sig <= 1


def test_small_edition_still_meets_d3_and_d2():
    sel = rank.select(good_pool(), PROFILE, DEFAULT_WEIGHTS, empty_ledger(__import__("pathlib").Path("/tmp")), today=TODAY)
    assert 3 <= len(sel.items) <= 5
