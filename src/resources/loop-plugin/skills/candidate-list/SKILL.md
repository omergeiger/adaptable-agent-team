---
name: candidate-list
description: Return format for the researcher's 10-15 digest candidates. Apply when the researcher reports candidates in the Collect phase and when the editor reads them in the Rank phase.
---

# candidate-list - Candidate Report Format

Gives the editor a consistent, checkable input every cycle so filtering and ranking never depend on how the researcher happened to phrase things.

## Template

```markdown
THEME: <theme received>
WINDOW: <cycle time minus 24h> to <cycle time> (UTC)
COUNT: <n>

| # | Title | Primary URL | Published (UTC) | Category | Funding | Follow-up | Summary |
|---|---|---|---|---|---|---|---|
| 1 | <specific title> | <primary-source URL> | <YYYY-MM-DD HH:MM, or "date unconfirmed"> | <category> | <amount, or "-"> | <"-" or "follows YYYY-MM-DD item: <title>"> | <one line, factual> |
```

Field rules:

- **Primary URL**: the primary source itself (vendor blog, release notes/changelog, GitHub release, paper, official docs, official announcement). If only secondhand coverage was found, put it in the cell prefixed `SECONDARY:`.
- **Published**: from the primary source. Use `date unconfirmed` rather than guessing.
- **Category**: one of `dev-tools`, `agent-frameworks`, `model-apis`, `coding-assistants`, `evals-observability`, `infra`, `other`.
- **Funding**: the round size (e.g. `$250M`) for funding news; `-` otherwise.
- **Summary**: one line, factual, no adjectives like "huge" or "game-changing".
- 10-15 rows. If under 10, add a line after the table: `SHORTFALL: <why>`.

## When to Apply

- **researcher**: format every candidate report this way.
- **editor**: treat this table as the input to `loop-plugin:significance-rubric`; flag rows that break the field rules instead of guessing.
- **Orchestrator**: save the researcher's table verbatim in the researcher's by-product doc.
