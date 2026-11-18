# profile-schema - User Interest Profile & Onboarding

**Audience: agent-applied (loop-plugin:profile-schema).** Keeps the user-interest model and the onboarding/preference-capture flow consistent and multi-user (D5) - never hardcoded to one user.

## Profile schema

One file per user: `projects/personalized-feed/profile/<user-id>.md`.

```markdown
# Profile - <user-id>
**Role:** <e.g. AI professional> · **Created:** <date> · **Last refined:** <date>

## Goals
- <what the user wants from the feed - learn X, find repos to try, follow thought leaders, …>

## Interests (weighted)
| Interest | Weight (1-5) | Status | Notes |
|---|---|---|---|
| agentic systems / LLM tooling | 5 | confirmed | seed default for Alex (D1) |
| <interest> | <n> | confirmed \| inferred | <evidence> |

## Anti-interests / excludes
- <topics to down-rank or never show>

## Preferred sources / authors
- <named repos, publications, people to favor>

## Engagement history (signal)
- <date> · item <id> · 👍/👎 / "more like" / "less like" · resulting adjustment
```

Rules: every interest is tagged `confirmed` or `inferred`; inferred interests are proposed to the human before they drive ranking strongly. Weights feed `loop-plugin:relevance-rubric`.

## Onboarding flow (new user)

1. Capture role + top goals (free text).
2. Offer 5-8 candidate interest tags; let the user keep/drop/add.
3. Ask for any anti-interests and any must-follow sources/authors.
4. Write the profile with all tags `confirmed`; set initial weights from stated priority.
5. Create an empty dedup ledger `projects/personalized-feed/profile/<user-id>-delivered.md`.

## When to Apply

- user-profiler creates and refines profiles and runs onboarding to this schema.
- ranking-engineer reads weights/excludes; never invents interests not in the profile.
