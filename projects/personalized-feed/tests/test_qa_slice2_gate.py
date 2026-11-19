"""Cycle 3 QA gate probes for Slice 2 (offline, synthetic pools)."""
from datetime import date

import pytest

from rank_helpers import cand, good_pool
from test_slice2_edition import fake_root, pool_source
from pfeed.pipeline import run_daily
from pfeed.render import render_edition
from pfeed import rank
from pfeed.rank_data import DEFAULT_WEIGHTS
from rank_helpers import PROFILE, empty_ledger

TODAY = date(2026, 11, 19)


def _root(tmp_path):
    root = tmp_path / "root"
    if not root.exists():
        root.mkdir()
        fake_root(root)
    return root


def run(tmp_path, pool, **kw):
    return run_daily("alex", TODAY, None, root=_root(tmp_path),
                     out_dir=tmp_path / "out", ledger_file=tmp_path / "out" / "ledger.md", sources=pool_source(pool), **kw)


def test_empty_pool_ships_nothing_and_writes_nothing(tmp_path):
    r = run(tmp_path, [])
    assert r["path"] is None and not list((tmp_path / "out").glob("*.md"))
    assert any("ALARM" in w for w in r["selection"].warnings)
    assert not (tmp_path / "out" / "ledger.md").exists()


def test_all_stale_pool_ships_nothing(tmp_path):
    old = [cand(f"o/r{i}", f"https://github.com/o/r{i}", summary="agent framework tool use", published="2025-01-01T00:00:00Z") for i in range(8)]
    r = run(tmp_path, old)
    assert r["path"] is None and r["stale_dropped"] == 8


def test_preamble_only_ledger_then_d7_across_two_runs(tmp_path):
    root = _root(tmp_path)
    led = tmp_path / "out" / "ledger.md"
    led.parent.mkdir()
    led.write_text("# Delivered ledger\nprose only, no table\n", encoding="utf-8")
    pool = good_pool()
    r1 = run_daily("alex", TODAY, None, root=root, out_dir=tmp_path / "out", ledger_file=led, sources=pool_source(pool))
    assert r1["path"] and 3 <= len(r1["selection"].items) <= 5
    urls1 = {s.candidate.canonical_url for s in r1["selection"].items}
    r2 = run_daily("alex", TODAY, None, root=root, out_dir=tmp_path / "out", ledger_file=led, sources=pool_source(pool))
    urls2 = {s.candidate.canonical_url for s in r2["selection"].items}
    assert not (urls1 & urls2)  # D7
    assert r2["path"] is None or r2["path"].name.endswith("-02.md")


def test_d2_d3_on_good_pool(tmp_path):
    sel = rank.select(good_pool(), PROFILE, DEFAULT_WEIGHTS, empty_ledger(tmp_path))
    assert 3 <= len(sel.items) <= 5
    assert len({s.candidate.source_type for s in sel.items}) >= 3


def test_renderer_refuses_non_https_link(tmp_path):
    pool = good_pool()
    sel = rank.select(pool, PROFILE, DEFAULT_WEIGHTS, empty_ledger(tmp_path))
    sel.items[0].candidate.url = "http://example.test/x"
    with pytest.raises(AssertionError):
        render_edition(sel, "alex", TODAY)


def test_link_is_emitted_unrewritten(tmp_path):
    sel = rank.select(good_pool(), PROFILE, DEFAULT_WEIGHTS, empty_ledger(tmp_path))
    md = render_edition(sel, "alex", TODAY)
    for s in sel.items:
        assert f"**Link:** {s.candidate.url}\n" in md
