# Onboarding template - new user (D5)
Follows loop-plugin:profile-schema. Design goal: the first minute asks for little; depth comes later through feedback. Never infer interests from anything but what the user gives.

## Step 0 - Setup (no questions)
Create `<user-id>.md` (empty schema) and `<user-id>-delivered.md` (empty dedup ledger, D7).

## Step 1 - Core (required, 2 questions, free text)
1. What do you do, and what do you want from this feed? (role + goals -> Role, Goals)
2. What would you actually do with a good item: try it, read it, follow the author, share it? (-> content-form preference)

## Step 2 - Pick interests (recognition, not recall)
Show 5-8 candidate tags (drawn from the source catalog, not from the user's environment). For each: Keep / Drop / Add own.
Then: "Order your kept tags by how much you care" (drag, or number 1..n).
Weights: first 1-2 -> 5; next -> 4; then 3, 2, 1 in order of rank. Tags the user ordered are `confirmed`.

## Step 3 - Excludes and sources (optional, skippable)
- "Anything you never want to see?" -> Anti-interests.
- "Any sources, sites or people you already trust?" -> Preferred sources. Skipping is fine.

## Step 4 - Write the profile
- All user-stated tags `confirmed`. Anything the agent guessed is `inferred`, weight <= 2, and flagged for a one-line confirm ("We think you may also like X - keep?") in the first edition.
- Last refined = today. Engagement history empty.

## Step 5 - First edition and feedback
- Each item shows 👍 / 👎 and "more like this" / "less like this" (cheap, one tap, no explanation required).
- Defaults when the user ignores everything: neutral, no change (silence is not dislike).

## Feedback -> profile rules (shared by all users)
| Signal | Adjustment |
|---|---|
| 👍 on item | +0.5 to its matched interests (inferred stays <= 2 until the user confirms) |
| 👎 on item | -0.5 to matched interests; if the item matched an exclude, strengthen exclude |
| "more like this" | +1 to the item's interest and note the form (repo/paper/writeup) |
| "less like this" | -1 to the item's interest or source |
| repeated 👍 on an inferred interest (>=2) | propose promotion to `confirmed` |
| no reaction | none |
Log every change in Engagement history with date, item id, signal, and adjustment; mark simulated feedback as `simulated`. Hand interest implications to ranking-engineer.
