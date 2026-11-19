"""D6 feedback: apply 👍/👎/more/less events to a user's signal weights (rubric: +/-0.05, clamp, renormalize, log)."""
import json
import re
from pathlib import Path

from .rank_data import DEFAULT_WEIGHTS, SIGNALS

STEP, LO, HI, HIGH_SCORE = 0.05, 0.05, 0.50, 4
_EVENT = re.compile(r"^\s*(👍|👎|more(?:\s+like)?|less(?:\s+like)?)\s*#?\s*(\d+)\s*$", re.I)


def parse_event(text):
    """'👍 1' / 'more like #3' -> ('up'|'down', item_number); ValueError otherwise."""
    m = _EVENT.match(text)
    if not m:
        raise ValueError(f"unrecognized feedback event: {text!r}")
    return ("up" if m.group(1) in ("👍",) or m.group(1).lower().startswith("more") else "down"), int(m.group(2))


def adjust(weights, signals, direction):
    """New weights: +/-STEP on each signal scoring >= 4, clamp to [LO, HI], renormalize to sum 1.0."""
    sign = 1 if direction == "up" else -1
    w = {k: min(HI, max(LO, weights[k] + (sign * STEP if signals[k] >= HIGH_SCORE else 0))) for k in SIGNALS}
    total = sum(w.values())
    return {k: v / total for k, v in w.items()}


def apply(weights_file, sidecar_file, events, simulated=False):
    """Apply events to <user>-weights.json; returns interest flags for user-profiler (profile is never edited)."""
    weights_file, sidecar = Path(weights_file), json.loads(Path(sidecar_file).read_text(encoding="utf-8"))
    state = json.loads(weights_file.read_text(encoding="utf-8")) if weights_file.exists() else \
        {"weights": dict(DEFAULT_WEIGHTS), "log": []}
    items, flags = {i["n"]: i for i in sidecar["items"]}, []
    for text in events:
        direction, n = parse_event(text)
        if n not in items:
            raise ValueError(f"edition {sidecar['date']}-{sidecar['edition']:02d} has no item #{n}")
        item, before = items[n], state["weights"]
        after = adjust(before, item["signals"], direction)
        state["log"].append({"date": sidecar["date"], "edition": sidecar["edition"], "event": text, "item": n,
                             "url": item["url"], "tag": "simulated" if simulated else "real",
                             "before": before, "after": after})
        state["weights"] = after
        if direction == "down" and item["interest"]:
            flags.append({"interest": item["interest"], "item": n, "reason": f"👎/less on #{n}",
                          "tag": "simulated" if simulated else "real"})
    weights_file.parent.mkdir(parents=True, exist_ok=True)
    weights_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return flags
