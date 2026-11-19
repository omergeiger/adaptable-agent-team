"""python -m pfeed check-live : hit each source endpoint once and print status counts (not part of pytest)."""
import sys
from collections import Counter

from .adapters import build_sources, run_sources
from .http import Http


def check_live(http=None, out=print, today=None):
    sources = build_sources(today)
    result = run_sources(http or Http(), sources)
    for r in result.reports:
        out(f"{'OK  ' if r.ok else 'FAIL'} {r.id:<28} {r.count:>3} items" + (f"  {r.error}" if r.error else ""))
    ok = sum(r.ok for r in result.reports)
    by_type = Counter(c.source_type for c in result.candidates)
    out(f"sources ok: {ok}/{len(result.reports)}, failed: {len(result.reports) - ok}, "
        f"candidates: {len(result.candidates)} {dict(by_type)}")
    return 0 if ok == len(result.reports) else 1


def daily(args):
    import argparse
    from datetime import date
    from pathlib import Path

    from .pipeline import format_report, run_daily
    p = argparse.ArgumentParser(prog="pfeed daily")
    p.add_argument("--user", required=True)
    p.add_argument("--date", type=date.fromisoformat, default=None)
    p.add_argument("--out", help="edition directory (default: feeds/). With --out, the ledger defaults to OUT/ledger.md")
    p.add_argument("--ledger")
    p.add_argument("--window-days", type=int, default=14)
    a = p.parse_args(args)
    ledger = a.ledger or (str(Path(a.out) / "ledger.md") if a.out else None)
    report = run_daily(a.user, a.date, Http(), out_dir=a.out, ledger_file=ledger, window_days=a.window_days)
    print(format_report(report))
    return 0 if report["path"] else 1


def feedback_cmd(args):
    import argparse
    from pathlib import Path

    from . import feedback
    from .pipeline import DEFAULT_ROOT
    from .rank import weights_path
    p = argparse.ArgumentParser(prog="pfeed feedback")
    p.add_argument("--user", required=True)
    p.add_argument("--edition", required=True, help="path to feeds/<date>-NN.json (or .md)")
    p.add_argument("--event", action="append", required=True)
    p.add_argument("--simulated", action="store_true")
    p.add_argument("--root", help="project root whose profile/<user>-weights.json is updated (default: this project)")
    p.add_argument("--weights", help="explicit weights file (overrides --root); use for trials")
    a = p.parse_args(args)
    side = Path(a.edition).with_suffix(".json")
    target = Path(a.weights) if a.weights else weights_path(a.root or DEFAULT_ROOT, a.user)
    for flag in feedback.apply(target, side, a.event, a.simulated):
        print("interest flag for user-profiler:", flag)
    return 0


def main(argv):
    if argv[1:] == ["check-live"]:
        return check_live()
    if argv[1:2] == ["daily"]:
        return daily(argv[2:])
    if argv[1:2] == ["feedback"]:
        return feedback_cmd(argv[2:])
    print("usage: python -m pfeed check-live | daily --user U [--date D] [--out DIR] | feedback --user U --edition F --event E [--root DIR | --weights FILE]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
