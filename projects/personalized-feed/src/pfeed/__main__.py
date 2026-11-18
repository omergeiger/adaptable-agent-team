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


def main(argv):
    if argv[1:] == ["check-live"]:
        return check_live()
    print("usage: python -m pfeed check-live", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
