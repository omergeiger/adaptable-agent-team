"""Daily entry point: sources -> recency -> rank -> edition file + sidecar -> ledger (D7, only after the write)."""
from datetime import date as _date
from pathlib import Path

from .adapters import build_sources, run_sources
from .ledger import Ledger, ledger_path
from .profile import load_profile
from .rank import load_weights, select
from .recency import DEFAULT_WINDOW_DAYS, filter_recent
from .render import write_edition

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def run_daily(user_id, today=None, http=None, root=DEFAULT_ROOT, out_dir=None, ledger_file=None,
              window_days=DEFAULT_WINDOW_DAYS, sources=None):
    """Returns a report dict. Never fabricates: failed sources contribute nothing; an unsatisfiable day ships nothing."""
    today = today or _date.today()
    root = Path(root)
    out_dir = Path(out_dir) if out_dir else root / "feeds"
    profile = load_profile(root, user_id)
    weights = load_weights(root, user_id)
    ledger = Ledger(ledger_file or ledger_path(root, user_id))
    result = run_sources(http, sources if sources is not None else build_sources(today))
    fresh, stale = filter_recent(result.candidates, today, window_days)
    selection = select(fresh, profile, weights, ledger)
    report = {"user": user_id, "date": str(today), "sources": result.reports, "fetched": len(result.candidates),
              "stale_dropped": stale, "selection": selection, "path": None, "edition": None}
    if selection.items:
        path, edition = write_edition(selection, user_id, today, weights, out_dir)
        ledger.append(today, f"{edition:02d}", [s.candidate for s in selection.items])
        report.update(path=path, edition=edition)
    return report


def format_report(r):
    ok = sum(s.ok for s in r["sources"])
    lines = [f"sources ok: {ok}/{len(r['sources'])}; fetched {r['fetched']}; stale dropped {r['stale_dropped']}; "
             f"stats {r['selection'].stats}"]
    lines += [f"  FAIL {s.id}: {s.error}" for s in r["sources"] if not s.ok]
    lines += [f"WARNING: {w}" for w in r["selection"].warnings]
    lines += [f"  #{n} {s.total:.2f} {s.candidate.source_type:<8} {s.interest or '(exploration)'} | {s.candidate.title}"
              for n, s in enumerate(r["selection"].items, 1)]
    lines.append(f"wrote {r['path']}" if r["path"] else "nothing shipped")
    return "\n".join(lines)
