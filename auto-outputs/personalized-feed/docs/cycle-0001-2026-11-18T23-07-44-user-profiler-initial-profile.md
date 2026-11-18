# Cycle 1 - user-profiler - initial profile for alex

Source: steering/personalized-feed/reader-source.md only (D8).

## Decisions
- Weights from listed order: 5,4,4,3,3,2,1 (agents, evals, local models, retrieval/extraction, observability, safety, rust). Order, not tie-ness, is the signal; ranking should break ties by list order.
- Content-form preference (hands-on/tryable) is recorded as its own section, since it cuts across topics and matches how Alex describes himself.
- Excludes include the stated list plus "news with nothing to try", which comes from the simulated-reaction rule.

## Inferred (weight <= 2, not to drive ranking)
1. document-processing agents (shipping docs / support copilot) - 2 - from job description
2. production reliability / hardening of LLM apps - 2 - from "boring reliability stuff"
3. classic ML forecasting - 1 - past experience only

## Ambiguities (conservative default applied)
- "Medium/substack blogs": none named; source-scout to propose, flagged as unconfirmed.
- Safety = 2 and rust = 1 may be ties with nearby topics; list order used as tie-break.

## Files
profile/alex.md, profile/alex-delivered.md (empty ledger), profile/_onboarding-template.md
