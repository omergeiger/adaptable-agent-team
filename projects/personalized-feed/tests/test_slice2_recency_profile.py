from datetime import date

from rank_helpers import PROFILE, cand
from pfeed.recency import filter_recent, parse_published

TODAY = date(2026, 11, 19)


def test_parse_published_handles_iso_rfc_and_garbage():
    assert parse_published("2026-11-18T10:00:00Z").day == 18
    assert parse_published("Tue, 17 Nov 2026 08:00:00 GMT").day == 17
    assert parse_published("2026-11-10").day == 10
    assert parse_published("") is None and parse_published("not a date") is None


def test_filter_recent_drops_old_keeps_new_and_undated():
    old = cand("old", "https://a.test/old", published="2026-10-01T00:00:00Z")
    new = cand("new", "https://a.test/new", published="2026-11-15T00:00:00Z")
    undated = cand("undated", "https://a.test/u", published="")
    kept, dropped = filter_recent([old, new, undated], TODAY, window_days=14)
    assert [c.title for c in kept] == ["new", "undated"] and dropped == 1


def test_window_is_configurable():
    c = cand("x", "https://a.test/x", published="2026-11-01T00:00:00Z")
    assert filter_recent([c], TODAY, 30)[1] == 0
    assert filter_recent([c], TODAY, 7)[1] == 1


def test_real_profile_parses_with_inferred_cap():
    names = {i.name: i for i in PROFILE.interests}
    assert len(PROFILE.interests) == 10
    inferred = [i for i in PROFILE.interests if i.status == "inferred"]
    assert all(i.effective_weight <= 2 for i in inferred)
    assert any("crypto" in e for e in PROFILE.excludes)
    assert names["agent frameworks / orchestration / tool use"].effective_weight == 5
