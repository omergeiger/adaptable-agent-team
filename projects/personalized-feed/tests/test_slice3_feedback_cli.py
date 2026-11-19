"""D-3: pfeed feedback must be trial-safe (--root / --weights)."""
import json

from pfeed import __main__ as cli, rank


def sidecar(tmp_path):
    p = tmp_path / "2026-11-19-01.json"
    p.write_text(json.dumps({"date": "2026-11-19", "edition": 1, "items": [
        {"n": 1, "url": "https://x.test/1", "interest": "rust tooling",
         "signals": {"interest-match": 5, "novelty": 5, "hands-on": 5, "thought-leadership": 1, "source-quality": 4}}]}))
    return p


def test_feedback_with_root_writes_only_under_root(tmp_path):
    side = sidecar(tmp_path)
    root = tmp_path / "trial"
    assert cli.feedback_cmd(["--user", "alex", "--edition", str(side), "--event", "👍 1", "--root", str(root)]) == 0
    assert rank.weights_path(root, "alex").exists()


def test_feedback_with_explicit_weights_file(tmp_path):
    side, w = sidecar(tmp_path), tmp_path / "w" / "my.json"
    cli.feedback_cmd(["--user", "alex", "--edition", str(side), "--event", "👎 1", "--weights", str(w)])
    assert w.exists()
