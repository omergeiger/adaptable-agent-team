# QA gate - slice 5 (cycle 8): APPROVE (with open risks)

Suite: `.venv/bin/python -m pytest -q` -> 196 passed in 0.19s (green). New file tests/test_slice5_ranking_fixes.py: real assertions, offline, canned pages.

Probes (scratch script, not committed):
- Recalc: body-only hits on HN/Lobsters capped at 3, origin=summary; same text from blog/repo uncapped (by design). Still eligible for a main slot (MIN 2); only loses to a good pool.
- Lobsters PDF: binary PDF / empty / non-utf8 / tiny pages quarantined; arXiv/github/lobste.rs links skipped. CJK-only titles have no tokens so skip the overlap check (minor).
- Confirmed-low (AI safety, rust) = 2; inferred = 1 and never explores; exploration requires strong.
- D-6: weak-only title match ("PDFs") still scores 2 and gets a main slot.

Live trial (network up, temp dir, ~107s/run; real feeds/ledger untouched):
- Run 1: 5 items; types blog, GitHub x3, Lobsters (D2 ok, D3 ok); 5/5 links HTTP 200; all have "why". 11 QUARANTINED lines.
- Run 2 same date: ledger_seen 6, zero repeats (D7 ok).

Open:
1. Lobsters "Catching prompt injections hidden in PDFs" (tomclancy.info) still delivered at #5 with a "ties to retrieval/structured extraction" rationale from a weak-only title hit. Page is real and on-topic enough (QA for AI incl. PDF tool), so the link is fine, but the stated reason is over-credited. Suggest: weak-only match -> signal 1 for main slots, or drop the interest name from the why.
2. Quarantine false positives: Fibonacci, OCaml unikernels, "Let's Build a Brain" etc. dropped as "not technical" (prose/JS pages); cert-verify failure and 403 (medium.com) also quarantine. Over-filtering, not harmful to D2/D3.
3. Run time ~107s (serial extra GET per Lobsters item).
4. arXiv "ALIVE: streaming video models" matched observability/tracing in run 2 (weak-match leakage outside slice scope).
No regression test added for these; recommend one for #1 against a realistic pool.
