# Cycle 9 - developer - Slice 6 (ranking fixes from cycle-8 QA/ranking findings)

Suite: 212 passed (196 before; 16 new in tests/test_slice6_ranking_fixes.py; 5 older tests updated to the new rules).

## Changes
1. Why-line cites an interest only for a strong match (rank Scored.strong), and lists the keywords that matched
   ("matched: tracing, otel"). Non-strong items get "a looser match to your interests". ALIVE-style paper (lone
   summary "tracing") now scores <= 2 and is dropped anyway.
2. MIN_INTEREST_MATCH_MAIN = 3 (and exploration min 3): items scoring <= 2 are never selected. The "floor lowered to 1"
   relaxation rung is removed. Source-type diversity is best-effort (swap only among eligible items); a shortfall
   yields warning "source-type shortfall: ..." and stats["source_types"]; the renderer no longer asserts >= 3 types.
   Fewer than 3 eligible items still ships nothing with an ALARM.
   Consequence for alex: confirmed-low (AI safety, rust) and inferred interests cannot ship in a main slot.
3. Scored.exploration_kind: "in-interest" (today's pick: a real interest outside the top 3) vs "broadening"
   (reserved for items outside all interests; nothing produces it yet). Why-line: "Exploration pick: ... from your X
   interest, outside your top interests"; "Broadening pick" only for kind "broadening". Sidecar gains exploration_kind.
4. Weak-only match (no non-weak keyword hit) scores 1 (fixes D-6: Lobsters "PDFs" item).
5. Lobsters: MIN_TECH_WORDS 2 -> 1, MIN_TITLE_OVERLAP 0.5 -> 0.34. FetchError now carries kind: "ssl" (local cert
   verify failure, no retry) or "blocked" (401/403/429); those are kept unverified, not quarantined. 404/timeouts still
   quarantine. Link checks run in a ThreadPoolExecutor (8 workers), feed order preserved.

## Not measured
Live run time was not re-measured (no network trial this slice); the parallel test shows 12 x 0.2s checks finish
in well under the serial 2.4s. Expect roughly serial/8 for the Lobsters portion.

## Handoff to QA
Re-run a live trial: check time vs 107s, quarantine count vs 11, that Lobsters PDF item is gone, and the new
shortfall warning wording. Needs critic GO/NO-GO per rank_data.py header (selection rules changed).
