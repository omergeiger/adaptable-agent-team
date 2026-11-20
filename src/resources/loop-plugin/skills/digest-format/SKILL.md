---
name: digest-format
description: Exact template for the daily AI tooling digest. Apply when the editor writes a digest in the Publish phase and when the orchestrator checks a digest before marking Publish complete.
---

# digest-format - Daily Digest Template

Fixes the structure of every published digest so readers and later cycles can rely on it; the format must not drift between cycles.

## Template

File: `projects/<active_project>/digests/YYYY-MM-DD.md` (UTC date of the cycle; `-2`, `-3` suffix if the file already exists). Fill every `<...>`; keep headings and order exactly.

```markdown
# AI Tooling Digest - YYYY-MM-DD

**Theme:** <the day's theme, one line>

## 1. <Headline: what happened, plain and specific>

<Why it matters, sentence 1: what changes for people building with AI.> <Why it matters, sentence 2: who is affected or what it enables/replaces.>

**Source:** [<publisher - page title>](<primary-source URL>)

## 2. <Headline>

<Sentence 1.> <Sentence 2.>

**Source:** [<publisher - page title>](<primary-source URL>)

<... items 3-5 in the same shape ...>

---

*<N> candidates reviewed; <M> dropped as repeats, <F> as funding news, <S> as stale or unsourced.*
```

Optional per item, directly under **Source:**: `**Also:** [<title>](<URL>)` for at most one secondary link (coverage or discussion).

**Fewer than 5 items:** publish only the items that qualify, numbered 1..k, and insert this line immediately after the Theme line:

```markdown
> Only <k> developments met the significance bar in the last 24 hours. This digest is intentionally short.
```

**Follow-up items:** start the first why-it-matters sentence with `Update:` and say what changed since the earlier coverage.

## Compliance checklist

- Title line and date match the filename date.
- Exactly 5 items, or fewer with the "only <k>" note present. Never more than 5.
- Each item: one `##` headline, exactly 2 sentences of why-it-matters, one **Source:** link pointing to a primary source (vendor blog, release notes/changelog, GitHub release, paper, official docs, official announcement).
- Items ordered by significance, most significant first.
- No framework stamps (cycle numbers, agent names, timestamps beyond the date) in the digest.
- Footer counts present.

## When to Apply

- **editor**: when writing the digest in rank-and-write mode.
- **Orchestrator**: before marking the Publish phase complete, check the digest against the compliance checklist. If it fails, send it back to the editor once with the specific failures; if it still fails, record the failure in Team State and Open Questions.
