# ATS Report - Talia Brennwood (review attempt 2)

Audited: projects/cv-designer/talia-brennwood/cv-draft.md against intake/raw-material.md, using loop-plugin:ats-checklist and loop-plugin:cv-section-template.

## Verdict: PASS

- FORBIDDEN items triggered: 0
- REQUIRED items failing: 0
- Compliance violations: 0 (3 advisory notes below)
- Second draft pass needed before Design: No (optional polish and open questions only)

## Compliance checklist

FORBIDDEN (none present)

- [x] Tables: none. Pipes appear only as inline separators in the contact line and entry headings; no Markdown table header/separator rows.
- [x] Multi-column layouts: none.
- [x] Text boxes or frames: none.
- [x] Inline images or logos: none.
- [x] Headers/footers with name or page number: none.
- [x] Decorative Unicode: none. Bullets are plain "-", separators are ASCII "|" and "---".
- [x] Non-standard fonts: not applicable to Markdown source; re-check in the Design phase.
- [x] Embedded hyperlinks: none; no [text](url) links in the draft.

REQUIRED (all present)

- [x] Full name is the first line ("# Talia Brennwood").
- [x] Email and phone are on line 5, within the first 5 lines.
- [x] Section headings are plain text and match the template exactly: Professional Summary, Experience, Education, Skills, Publications & Projects. Certifications & Awards is omitted (see advisory 3).
- [x] Dates are consistent: Month YYYY - Month YYYY / Present for roles; year-only for Education and Publications, which the template allows.
- [x] Every experience entry has title, company and dates (3 of 3 entries).

## Advisory notes (not failures)

1. Portfolio URL has no scheme ("portfolio.example.com/talia"). The checklist wants raw URLs as https://...; the draft carries an inline [CONFIRM https:// scheme] tag. Recommend writing https://portfolio.example.com/talia once confirmed. The source omits the scheme too, so this is a confirmation, not an invention.
2. Headline "Lead Product Designer" is the target role, while the current title is Senior Product Designer. This is how the template defines the headline and is not fabrication, but ATS title matching reads the Experience entry; keep the Fernhollow title as stated.
3. Raw material lists the Ridgecrest Design Prize under Certifications & Awards. The draft carries it as a thesis bullet in Education. This is acceptable and avoids duplication. An ATS keyword for "awards" will not fire, which is minor.

## Known open tags (tracked, do not fail ATS)

- [MISSING - LinkedIn URL] (contact line)
- [MISSING - city] x4 (Fernhollow, Quillmark, Copperline, Ridgecrest)
- [CONFIRM start month] (Fernhollow, March 2022)
- [CONFIRM currency] (Quillmark ARR)
- [CONFIRM https:// scheme] (portfolio)

These tags must be resolved or removed before the final ATS plain-text export, because a parser will read them as literal text. Contact has email plus phone, so the missing LinkedIn URL does not break the REQUIRED rule.

## Fidelity spot-check against raw-material.md

All figures match the source: 61% to 84% over about 2 quarters; Fern UI with 1 designer and 3 engineers across 5 teams; no-shows down 18%; 2M to 9M ARR worded as "contributing to" (team effort preserved); 58% to 89% task success; about 40 interviews per year; low-vision kiosk testing. Deliberately omitted per source: the unconfirmed +22% trial-to-paid, 2015-2016 freelance, headcount, UX certificate, and the leadership workshop. No fabricated claims found. "Regulated healthcare setting" in the summary is a reasonable reading of the JD framing.

## Keyword alignment (JD: Lead Product Designer - Care Platform)

| Cluster | Rating | Evidence |
|---|---|---|
| Design systems / systems thinking | High | Summary, Fernhollow bullet, Skills |
| Accessibility (WCAG) | High | Summary, Fernhollow bullet, Skills, kiosk low-vision |
| Measurable outcomes | High | 61 to 84%, 18%, 58 to 89%, ARR in multiple places |
| Facilitation | High | Summary, critique bullet, Skills |
| Regulated domain (healthcare) | Medium | "regulated healthcare setting" once in Summary; "legal" in a bullet |
| Seniority language (Senior / Lead) | Medium | "Senior Product Designer" title and "Lead" headline; no "led design for an area" |
| Health-tech / patients and care teams | Medium | "telehealth", "patient", "clinicians" appear; "care teams" absent |
| 7+ years | Medium | "since 2017" implies 9+ years; the number is never stated |
| People management (manage 2-3 designers) | Low | Only "mentors 2 mid-level designers"; no "manage/lead team" language, correctly, per source |
| Leading a product area | Low | Not supported by source; see gap 1 |
| Partnering with product and engineering leads | Low | Engineers appear only as co-builders; "partner" appears only for clinicians |

Clusters below Medium: 3 of 11. This is a content gap, not a formatting defect.

## Top 3 keyword gaps and recommendations (recommendations only; draft not modified)

1. Product-area ownership and people management (Low). Do not claim ownership or line management without the candidate's answer to intake question 7. If she confirms either, add it as a Fernhollow bullet using the JD wording ("led design for ..." / "managed N designers"). If not, keep "mentors 2 mid-level designers" and consider "leads the design critique" in the Summary.
2. Cross-functional partnership (Low). The source supports working with clinicians and with 3 engineers on Fern UI. Suggest: "Partnered with clinicians, product and engineering ..." only to the extent the facts support it (clinicians and engineers are supported; "product leads" is not stated and needs confirmation).
3. Years of experience and domain terms (Medium). Add an explicit "8+ years" to the Summary opening (supported by the 2017 start; the candidate says "8ish") and include "health-tech" and "care teams" phrasing only where facts support it (patients and clinicians are supported).

## Pre-Design handoff

Before the graphical-designer builds the plain-text ATS version, resolve or strip all bracketed tags, write the portfolio URL as raw https text, and keep the contact line free of tables. No second Draft pass is required for ATS; one is optional to apply gap 3 and any answers to the open questions.
