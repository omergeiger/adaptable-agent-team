# Developer - slice 5 (cycle 8)

Built to ranking-engineer cycle-7 eval (MF1, low-weight decision) and QA D-4/D-5/D-6. Suite: 196 passed (was 182).

- rank.py `_match` (match_interest wraps it): every hit is logged as {keyword, origin: title|summary}; Scored gets
  `strong` and `matches`; sidecar JSON now has `matches` per item.
- HN/Lobsters items with all hits in the summary: capped at 3 (SUMMARY_ONLY_CAP); if every such hit is weak the
  item gets no interest match at all (so a bad match cannot feed the thumbs-down loop).
- "pdf", "extraction" added to WEAK_KEYWORDS. Strong now needs a non-weak title hit, or >= 2 hits with one non-weak.
- Confirmed low-weight interests (AI safety, rust) tier base 2; inferred stays 1. Exploration needs `strong` and
  interest-match >= 2 (EXPLORATION_MIN_INTEREST_MATCH 3 -> 2).
- lobsters.fetch_checked: fetches each linked page, quarantines it when not technical, title overlap < 50%, or
  unreachable. Source.quarantine / SourceReport.quarantined; format_report prints QUARANTINED lines.
  S5 sources use it (one extra GET per Lobsters item; skipped for github/arxiv/lobste.rs links).
- Tests: tests/test_slice5_ranking_fixes.py (offline, canned pages).

Leftovers: no live trial run (network); weights/caps untouched; thresholds in lobsters.py are starting guesses.
