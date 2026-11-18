# ATS Report - Talia Brennwood (review attempt 3)

Audited: projects/cv-designer/talia-brennwood/cv-draft.md against the target JD in intake/raw-material.md, using loop-plugin:ats-checklist and loop-plugin:cv-section-template. The draft was not modified.

## Verdict: PASS (with advisories)

- FORBIDDEN items triggered: 0
- REQUIRED items failing: 0
- Compliance violations: 0
- Advisory items (must be resolved before Design): 3 groups, listed below
- Keyword clusters rated below Medium: 0 of 4 (the checklist threshold for a mandatory revision pass is more than 2)
- Second draft pass needed before Design: Not required for ATS. One light pass is recommended to apply the answers to the open human-input items and the optional recommendations below.

## Compliance checklist

FORBIDDEN (none present)

- [x] Tables: none. Pipes appear only as inline separators in the contact line and in entry headings. There are no Markdown table header or separator rows, and every "---" is a standalone horizontal rule with a blank line above it.
- [x] Multi-column layouts: none.
- [x] Text boxes or frames: none.
- [x] Inline images or logos: none.
- [x] Headers or footers with name or page number: none.
- [x] Decorative Unicode: none. Bullets are plain "-", and quotes and separators are ASCII.
- [x] Non-standard fonts: not applicable to the Markdown source. Re-check in the Design phase.
- [x] Embedded hyperlinks: none. There are no [text](url) links. The portfolio URL is raw text but lacks a scheme (see advisory A1).

REQUIRED (all present)

- [x] Full name is the first line ("# Talia Brennwood").
- [x] Contact info: email and phone are on line 5 of the file, within the first 5 lines. This has no slack, so the Design phase must not add anything above the contact line.
- [x] Section headings are plain text and match the cv-section-template names, case-sensitive and in template order: Professional Summary, Experience, Education, Skills, Publications & Projects. Certifications & Awards is omitted, which is allowed (see advisory A3).
- [x] Dates are consistent for all experience entries: Month YYYY - Month YYYY or Present. The roles run without gaps from January 2017 to Present. Education and Publications use year only, as the template specifies.
- [x] Every experience entry has title, company and dates (3 of 3).

## Advisory items

These are not ATS failures, but they must be resolved before Design.

A1. Open tags are tracked as human-input items. A parser reads bracketed text as literal content, so each tag must be resolved or removed before the plain-text ATS export.
- [MISSING - LinkedIn URL] (contact line). Email plus phone satisfies the REQUIRED rule, so this is not a violation.
- [MISSING - city] x4 (Fernhollow, Quillmark, Copperline, Ridgecrest).
- [CONFIRM start month] (Fernhollow, March 2022).
- [CONFIRM currency] (Quillmark ARR).
- [CONFIRM https:// scheme] (portfolio). Once confirmed, write it as raw text: https://portfolio.example.com/talia. The source omits the scheme too, so this is a confirmation, not an invention.

A2. Headline "Lead Product Designer" is the target role, while the current title is Senior Product Designer. The template defines the headline as the target role, so this is not fabrication and not an ATS failure. Title matching reads the Experience entry, so keep "Senior Product Designer" exactly as stated. The orchestrator should be aware that the headline could be read as a claimed current title.

A3. The Ridgecrest Design Prize sits in an Education bullet rather than under Certifications & Awards. This is acceptable and avoids duplication. An "awards" heading keyword will not fire, which is minor.

## Fidelity spot-check against raw-material.md

No fabricated claims found. All figures match the source:
- Intake completion 61% to 84% over about 2 quarters.
- Fern UI built with 1 designer and 3 engineers, used by 5 product teams.
- No-shows down 18%.
- ARR 2M to 9M, worded as "contributing to", which preserves the candidate's team-effort caveat.
- Task success 58% to 89%.
- About 40 interviews per year.
- Low-vision kiosk testing.

Deliberately omitted per source status: the unconfirmed +22% trial-to-paid, 2015-2016 freelance, Fernhollow headcount, the UX certificate (candidate says skip), and the 2023 leadership workshop. The summary phrase "regulated healthcare setting" is a reasonable reading of the JD framing and of the audit coordinated with legal.

## Keyword alignment (JD: Lead Product Designer - Care Platform)

Cluster ratings (High = 2+ in context, Medium = once, Low = absent or skills list only):

1. Core skills: High. Design systems and WCAG accessibility each appear in the Summary, in an Experience bullet and in Skills. Measurable outcomes are present in numbers throughout. The phrase "systems thinking" is absent, but design-system evidence is strong.
2. Seniority and leadership language: Medium. "Senior" appears in the title and "Lead" in the headline. "Led" appears about accessibility, and "mentors" appears several times. There is no "led design for a product area" or "managed designers" language, correctly, because the source does not support it.
3. Domain vocabulary: High. "Healthcare" and "telehealth" each appear in more than one place, and "patient", "clinicians", "regulated" and "provider-side" appear too. "Health-tech" and "care teams" as phrases are absent.
4. Soft skills: Medium. Facilitation appears in the Summary, in the critique bullet and in Skills. "Communication" and "partnering with product and engineering" are not stated.

Individual JD terms rated Low:
- Leading a product area.
- Managing 2-3 designers.
- Partnering with product and engineering leads (engineers appear only as Fern UI co-builders).
- The "7+ years" number (the draft says "since 2017", which implies it, but the figure is never stated).

## Top 3 keyword gaps and recommendations (recommendations only)

1. Product-area ownership and people management (Low). Do not claim either without the candidate's answer to intake question 7. If she confirms, add a Fernhollow bullet using the JD wording ("led design for ...", "managed N designers"). If not, keep "mentors 2 mid-level designers" and "facilitates the weekly design critique", which are already present.
2. Cross-functional partnership and communication (Low). The facts support working with clinicians, 3 engineers on Fern UI and legal on the accessibility remediation. Suggest wording such as "Partnered with clinicians, engineers and legal ..." only to that extent. "Product leads" is not in the source and needs confirmation.
3. Explicit years of experience (Low as a stated number). Employment is continuous from January 2017 to Present, which is about 9 years 10 months as of November 2026. Adding "9+ years" to the Summary opening is derivable from the dates and is not an invention. This replaces the earlier "8+" suggestion, which used the candidate's stale "8ish" figure. Also consider "health-tech" and "care teams" wording only where the facts support it (patients and clinicians are supported).

Optional: restore the Quillmark onboarding bullet's 22% trial-to-paid result only after the human confirms whether it is relative or in percentage points.

## Pre-Design handoff

- Resolve or strip all bracketed tags.
- Write the portfolio URL as raw https text.
- Keep the contact line within the first 5 lines, with no tables.
- Re-check fonts and header/footer content in the HTML and PDF exports. The plain-text ATS version must carry no page numbers.
