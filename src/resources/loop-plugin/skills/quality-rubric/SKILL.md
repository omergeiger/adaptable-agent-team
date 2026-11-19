---
name: quality-rubric
description: 1-5 CV content quality rubric (impact language, quantification, and more). Apply when the content-writer self-scores a draft before handing it to Review; any dimension below 3 blocks advancing.
---

# quality-rubric - CV Content Quality Scoring Rubric

Provides a consistent scoring standard so content quality is measurable across cycles and agents, not subjective. Applied by the content-writer before handoff to Review.

## Rubric

Score each dimension 1-5. The minimum passing score per dimension to advance from Draft to Review is **3**. A dimension below 3 must be flagged to the orchestrator with the specific sections that scored low.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| **Impact language** | Duties-focused ("responsible for X") | Mix of duties and outcomes | Every bullet leads with outcome or measurable impact |
| **Quantification** | No numbers anywhere | Some numbers, inconsistently applied | Every achievement has a number, range, or relative scale |
| **Relevance** | Generic; could be any candidate | Moderately tailored to the target role | Every section speaks directly to the job description requirements |
| **ATS keyword density** | Key terms from JD absent | Some terms present, often buried | Primary JD terms appear naturally in context, not stuffed |
| **Clarity & concision** | Long, passive sentences; jargon without explanation | Some verbosity; mostly clear | Every bullet is one clear action + one clear result; no filler |

## Scoring Protocol

1. Read the full `cv-draft.md` against the intake note and job description.
2. Score each dimension independently - do not let one strong section inflate others.
3. For any dimension scoring below 3, quote the two worst-offending bullets verbatim.
4. Report format: a markdown table with dimension, score, and one-line note. Example:

```
| Dimension | Score | Note |
|---|---|---|
| Impact language | 4 | Most bullets outcome-focused; two experience entries still duty-focused |
| Quantification | 2 | Only 3 of 12 bullets carry numbers - needs a revision pass |
| Relevance | 3 | Summary strong; skills section doesn't mirror JD terminology |
| ATS keyword density | 3 | Core terms present; seniority language thin |
| Clarity & concision | 4 | Clean throughout; summary slightly verbose |
```

## When to Apply

`content-writer` applies this rubric to self-score before reporting to the orchestrator. If any dimension is below 3, the content-writer must attempt a targeted revision in the same cycle before reporting. If still below 3 after revision, report the score and flag it - do not advance to Review until the orchestrator decides.
