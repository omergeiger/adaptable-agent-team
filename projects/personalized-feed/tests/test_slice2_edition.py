import json
import shutil
from datetime import date

import pytest

from rank_helpers import PROFILE, ROOT, cand, empty_ledger, good_pool
from pfeed import feedback, rank
from pfeed.adapters import Source
from pfeed.ledger import Ledger
from pfeed.pipeline import run_daily
from pfeed.rank_data import DEFAULT_WEIGHTS, SIGNALS
from pfeed.render import next_edition, render_edition, write_edition

TODAY = date(2026, 11, 19)


def selection(tmp_path):
    return rank.select(good_pool(), PROFILE, DEFAULT_WEIGHTS, empty_ledger(tmp_path))


def fake_root(tmp_path):
    (tmp_path / "profile").mkdir()
    shutil.copy(ROOT / "profile" / "alex.md", tmp_path / "profile" / "alex.md")
    return tmp_path


def pool_source(pool):
    return [Source("fake", "https://fake.test/", lambda http: pool)]


# ---- renderer ----
def test_markdown_matches_feed_item_format(tmp_path):
    md = render_edition(selection(tmp_path), "alex", TODAY)
    assert md.startswith("# Personalized Feed - 2026-11-19\n**User:** alex · **Items:** ")
    n = len(selection(tmp_path).items)
    assert md.count("\n## ") == n
    for label in ("**Source:**", "**Link:** https://", "**Type:**", "**Why it's worth investigating:**",
                  "**Relevance signals:** interest-match"):
        assert md.count(label) == n
    assert md.rstrip().endswith('to tune future feeds._')
    assert "Broadening pick:" in md


def test_renderer_refuses_bad_editions(tmp_path):
    sel = selection(tmp_path)
    sel.items = sel.items[:2]
    with pytest.raises(AssertionError):
        render_edition(sel, "alex", TODAY)


def test_edition_numbering_increments(tmp_path):
    sel = selection(tmp_path)
    p1, e1 = write_edition(sel, "alex", TODAY, DEFAULT_WEIGHTS, tmp_path / "feeds")
    p2, e2 = write_edition(sel, "alex", TODAY, DEFAULT_WEIGHTS, tmp_path / "feeds")
    assert (p1.name, p2.name) == ("2026-11-19-01.md", "2026-11-19-02.md") and next_edition(tmp_path / "feeds", TODAY) == 3
    assert json.loads(p1.with_suffix(".json").read_text())["items"][0]["signals"]


# ---- pipeline ----
def test_pipeline_writes_edition_and_ledger_then_second_run_has_no_repeats(tmp_path):
    root = fake_root(tmp_path)
    r1 = run_daily("alex", TODAY, None, root, out_dir=tmp_path / "out", sources=pool_source(good_pool()))
    assert r1["path"].name == "2026-11-19-01.md"
    delivered = {c.canonical_url for c in (s.candidate for s in r1["selection"].items)}
    ledger = Ledger(root / "profile" / "alex-delivered.md")
    assert {row[2] for row in ledger.rows} == delivered
    r2 = run_daily("alex", TODAY, None, root, out_dir=tmp_path / "out", sources=pool_source(good_pool()))
    second = {s.candidate.canonical_url for s in r2["selection"].items}
    assert not (delivered & second)


def test_pipeline_drops_stale_and_ships_nothing_when_unsatisfiable(tmp_path):
    old = [cand(f"o{i}/agent{i}", f"https://github.com/o{i}/agent{i}", summary="agent framework",
                published="2026-01-01T00:00:00Z") for i in range(6)]
    root = fake_root(tmp_path)
    r = run_daily("alex", TODAY, None, root, out_dir=tmp_path / "out", sources=pool_source(old))
    assert r["stale_dropped"] == 6 and r["path"] is None
    assert not (tmp_path / "out").exists() and not (root / "profile" / "alex-delivered.md").exists()


def test_failed_source_is_reported_and_nothing_fabricated(tmp_path):
    from pfeed.http import FetchError

    def boom(http):
        raise FetchError("down")
    r = run_daily("alex", TODAY, None, fake_root(tmp_path), out_dir=tmp_path / "out",
                  sources=[Source("bad", "https://bad.test/", boom)])
    assert r["fetched"] == 0 and r["path"] is None and not r["sources"][0].ok


def test_ledger_adds_header_to_preamble_only_file(tmp_path):
    p = tmp_path / "l.md"
    p.write_text("# Delivered ledger\nprose only\n")
    led = Ledger(p)
    led.append("2026-11-19", "01", [cand("t", "https://github.com/a/b")])
    assert "| date |" in p.read_text() and len(Ledger(p).rows) == 1


# ---- feedback ----
def sidecar_for(tmp_path):
    p, _ = write_edition(selection(tmp_path), "alex", TODAY, DEFAULT_WEIGHTS, tmp_path / "feeds")
    return p.with_suffix(".json")


@pytest.mark.parametrize("text,expected", [("👍 1", ("up", 1)), ("more like #3", ("up", 3)), ("👎 2", ("down", 2)),
                                           ("Less like #4", ("down", 4))])
def test_parse_event(text, expected):
    assert feedback.parse_event(text) == expected
    with pytest.raises(ValueError):
        feedback.parse_event("meh")


def test_adjust_sums_to_one_and_respects_clamp():
    w = dict(DEFAULT_WEIGHTS)
    for _ in range(40):
        w = feedback.adjust(w, {k: 5 for k in SIGNALS[:1]} | {k: 0 for k in SIGNALS[1:]}, "up")
    assert sum(w.values()) == pytest.approx(1.0, abs=1e-9)
    assert all(v > 0 for v in w.values())
    down = feedback.adjust(DEFAULT_WEIGHTS, {k: 5 for k in SIGNALS}, "down")
    assert sum(down.values()) == pytest.approx(1.0, abs=1e-9)


def test_apply_up_raises_high_signals_logs_and_flags_on_down(tmp_path):
    side, wf = sidecar_for(tmp_path), tmp_path / "alex-weights.json"
    item1 = json.loads(side.read_text())["items"][0]
    assert feedback.apply(wf, side, ["👍 1"]) == []
    state = json.loads(wf.read_text())
    high = [k for k in SIGNALS if item1["signals"][k] >= 4]
    low = [k for k in SIGNALS if k not in high]  # renormalizing can shave a big weight, so compare group shares
    assert sum(state["weights"][k] for k in high) > sum(DEFAULT_WEIGHTS[k] for k in high) or not low
    assert sum(state["weights"].values()) == pytest.approx(1.0, abs=1e-9) and state["log"][0]["tag"] == "real"
    flags = feedback.apply(wf, side, ["less like #1"], simulated=True)
    assert flags and flags[0]["tag"] == "simulated" and len(json.loads(wf.read_text())["log"]) == 2


def test_apply_rejects_unknown_item(tmp_path):
    with pytest.raises(ValueError):
        feedback.apply(tmp_path / "w.json", sidecar_for(tmp_path), ["👍 9"])


def test_weights_file_is_picked_up_by_load_weights(tmp_path):
    root = fake_root(tmp_path)
    assert rank.load_weights(root, "alex") == DEFAULT_WEIGHTS
    feedback.apply(rank.weights_path(root, "alex"), sidecar_for(tmp_path), ["👍 1"])
    assert rank.load_weights(root, "alex") != DEFAULT_WEIGHTS


def test_exploration_why_line_starts_with_broadening_pick(tmp_path):
    from pfeed.render import why_line
    pick = next(s for s in selection(tmp_path).items if s.exploration)
    assert why_line(pick).startswith("Broadening pick:")
