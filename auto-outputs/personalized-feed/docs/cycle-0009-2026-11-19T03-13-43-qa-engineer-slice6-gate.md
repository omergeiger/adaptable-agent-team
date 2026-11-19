# Cycle 9 QA gate - Slice 6: APPROVE (with notes)

Suite: `cd projects/personalized-feed && PYTHONPATH=src .venv/bin/python -m pytest -q` -> 212 passed in 0.64s (green).

Live trial (temp dir /tmp/trial9, ledger copied there; real feeds/ and ledger untouched):
`PYTHONPATH=src .venv/bin/python -m pfeed daily --user alex --out /tmp/trial9 --date 2026-11-19`
- Run time 80s (was 107s). Sources 33/33 ok. Quarantined 8 (was 11); all "does not match/not technical"/404, none ssl/blocked.
- 3 items, 3 types (GitHub, HN, blog) -> D2/D3 pass at the minimum. All 3 links HTTP 200 (curl). Why-lines present.
- D7: none of the 3 items appear in edition 01's 5 items or the real ledger. Lobsters "PDFs" item gone; ALIVE paper gone; no "looser match" or weak-only items shipped.
- Rung 4 was needed (hands-on floor 1, size 3, 2nd item for a capped interest); no exploration pick; no source-type shortfall warning.

Notes / risks (non-blocking)
1. Thin margin: exactly 3 items / 3 types; any one failing a link check tomorrow gives an ALARM/ship-nothing or a shortfall.
2. Item 1 (boring-marketing-skills, a marketing-skills repo) scores interest-match 5 on generic keywords "agent, agents" only; likely over-credited. Item 3 "matched: llama.cpp, ollama" for datasette-llm is plausible but loose.
3. rank.py:370 warning text "hands-on floor lowered to 1" remains (hands-on rung, not the removed interest-floor rung); wording can confuse readers.
4. Critic GO/NO-GO still required per rank_data.py header; not done by QA.
5. No new tests added this gate (no new bug in code; the items above are ranking-quality judgments for ranking-engineer).
