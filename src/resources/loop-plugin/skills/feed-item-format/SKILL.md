---
name: feed-item-format
description: Template for every feed edition and its items (3-5 items, 3+ source types, real link and a why-line each). Apply when the developer renders an edition and when the qa-engineer checks one.
---

# feed-item-format - Daily Feed & Item Template

**Audience: agent-applied (loop-plugin:feed-item-format).** Protects the shape of every feed item and the daily digest so output stays consistent across cycles, users, and the Slack vs markdown channels.

## Template

A daily feed is a markdown file `projects/personalized-feed/feeds/<YYYY-MM-DD>-NN.md` (NN = edition number, 01, 02, ...) with 3 to 5 items spanning at least 3 distinct source types.

```markdown
# Personalized Feed - <YYYY-MM-DD>
**User:** <user-id> · **Items:** <n> · **Source types:** <e.g. GitHub, Medium, forum>

## 1. <Item title>
- **Source:** <GitHub | Medium | HN | Lobsters | blog | …> · **Link:** <verifiable URL>
- **Type:** <repo | article | discussion | paper | tool>
- **Why it's worth investigating:** <1-2 sentences tying it to a specific interest in the user's profile; what they'll learn or could try hands-on.>
- **Relevance signals:** interest-match <0-5> · novelty <0-5> · source-quality <0-5> · hands-on <0-5> · thought-leadership <0-5>

## 2. <Item title>
...
```

End the file with a one-line feedback prompt:
```markdown
---
_Feedback: reply 👍/👎 per item, or "more like #2 / less like #4" to tune future feeds._
```

## When to Apply

- The developer renders feeds to this exact structure; the same renderer feeds the Slack push.
- qa-engineer rejects any feed that breaks the structure, drops below 3 / above 5 items, has <3 source types, or has any item missing a real link or a "why it's worth investigating" line.
- Relevance-signal numbers come from ranking-engineer (`loop-plugin:relevance-rubric`).
