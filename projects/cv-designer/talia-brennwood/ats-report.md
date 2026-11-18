# ATS Report - Talia Brennwood (Lead Product Designer, Care Platform)

Reviewed: cv-draft.md against the target JD in intake/raw-material.md. Skill applied: loop-plugin:ats-checklist (with loop-plugin:cv-section-template for heading names). Review cycle 3. Recommendations only; the draft was not modified.

## Verdict: FAIL (1 compliance violation, fixable with a one-line edit)

- Confirmed compliance violations: 1 (inconsistent date format, "Spring 2022").
- Advisories (non-failing): 4.
- The known inline [MISSING]/[CONFIRM] tags alone do NOT change the verdict. They are legitimate draft-stage placeholders under the section template, and no REQUIRED item depends on them (name, email and phone, headings, and company/title/dates per entry are all present). They remain a hard blocker for Design (see "Tags to resolve").
- The FAIL stands even if the tags are ignored, because of the date-format violation (R4). Once R4 is fixed, the draft would pass the format checklist, with the tags still open.
- A second draft pass is needed before Design: small content-writer pass for R4 and keyword wording, plus human input for the tags.

## 1. Compliance Checklist

### FORBIDDEN (all clear)

- Tables: clear. Pipes appear only as inline separators in the contact line and entry headings (template-mandated); there is no header-separator row or column grid.
- Multi-column layouts: clear (pure Markdown, single flow).
- Text boxes or frames: clear.
- Inline images or logos: clear.
- Headers or footers with name/page number: none in the Markdown. Must be re-verified in the Design output (HTML/PDF print CSS must not add running headers or footers).
- Decorative Unicode: clear. Only ASCII hyphens and standard punctuation found; no check marks, arrows, or stars. The "---" rules are plain.
- Non-standard fonts: not assessable in Markdown. Deferred to Design; ATS version should use a standard system font.
- Embedded hyperlinks in display text: clear. No [text](url) links; the portfolio URL is raw text.

### REQUIRED

- Full name as first line: PASS ("# Talia Brennwood").
- Email plus phone or LinkedIn in the first 5 lines: PASS (email and phone on line 5; LinkedIn is a [MISSING] tag but is not needed to satisfy this item).
- Section headings plain text and matching the template: PASS for Professional Summary, Experience, Education, Skills, Publications & Projects. See advisory A3 on the omitted Certifications & Awards section.
- Consistent date format (Month YYYY or MM/YYYY): FAIL. See R4.
- Company, title, and dates on every experience entry: PASS (cities are [MISSING], but city is not one of the three required fields).

### Violations

- V1 (R4): Fernhollow Health entry uses "Spring 2022 - Present". "Spring" is not a Month YYYY value, an ATS date parser may drop it, and the experience duration (and thus the JD's "7+ years" match) can be miscomputed. The other roles use full Month YYYY ("June 2018 - February 2022", "January 2017 - May 2018") so the format is also mixed. The intake gives "March 2022" as the candidate's best recollection, flagged UNCONFIRMED.

### Advisories

- A1: Portfolio URL is "portfolio.example.com/talia" with no scheme. The checklist wants URLs as raw text in the form https://... for the ATS-submitted version. Confirm the scheme with the candidate rather than assuming.
- A2: Year-only dates in Education (2016) and Publications ("2023", "Since 2021") are consistent with the template and acceptable, but note they are not Month YYYY. Fine as is; do not mix further.
- A3: The Ridgecrest Design Prize appears only as an Education bullet. The intake lists it under Certifications & Awards, and ATS award parsers look for that heading. Consider a short Certifications & Awards section (heading must match the template exactly) with the prize, Ridgecrest Institute of Art & Design, 2016. Do not add the unfinished UX certificate; the candidate said SKIP.
- A4: Headline "Lead Product Designer" is the target role (template-mandated), while the current title is Senior Product Designer. Keep as is, but the Design phase should not present it as a held title.

## 2. Keyword Alignment

Scale: High = 2+ appearances in context; Medium = once; Low = absent or skills list only.

### Cluster 1 - Core skills (design systems, accessibility, measurable outcomes): High
- Design system: High (summary, Fern UI bullet, Skills).
- Accessibility / WCAG: High (summary, audit bullet, Skills, kiosk low-vision testing).
- Measurable outcomes: High (61% to 84%, 18%, 22%, 58% to 89%).
- Cross-functional partnership with product and engineering leads: Low. Engineers appear once ("3 engineers"); "product" partnership is not evidenced anywhere.

### Cluster 2 - Seniority and leadership language: Medium
- "Lead"/"Senior": Medium (headline, "Senior Product Designer", "led accessibility").
- "Mentor": High.
- Leading a product area / managing designers / direct reports: Low (absent). This is the JD's central requirement. The intake itself marks it [MISSING]; see Gaps. The draft correctly does not claim it.
- "7+ years": Medium. Draft says "since 2017", which an ATS cannot always convert to a year count. The candidate said "8ish"; dates from January 2017 span longer than that. Do not state a number until confirmed.

### Cluster 3 - Domain vocabulary (health tech, regulated domains): Medium
- Healthcare / telehealth / patient / clinicians: High.
- "Health tech" or "care" phrasing: Low (absent).
- "Regulated" / compliance: Low (absent). Evidence exists in the facts (WCAG 2.1 AA audit, coordination with legal, healthcare employer) but the word is never used. Do not add HIPAA or any specific regulation; the source does not support it.

### Cluster 4 - Soft skills named in the JD (facilitation, communication): Low
- Facilitation: Low. Appears only in the Skills list ("workshops and facilitation"); the critique bullet does not use the word.
- Communication: Low (absent). Evidence exists (Cascadia UX talk, weekly critique, legal coordination) but is not worded as such.

### Scoring outcome
- One of four clusters is below Medium (Cluster 4). The checklist threshold for a mandatory revision pass (more than two clusters below Medium) is not met. A pass is still needed because of V1 and the tags.

### Top 3 keyword gaps
1. Product-area ownership and people management (lead a product area, manage 2-3 designers). Needs candidate confirmation; cannot be fixed by wording alone.
2. Facilitation and communication language in context (currently Skills-list only).
3. Regulated-domain and health-tech vocabulary ("regulated", "health tech", care team context).

## 3. Rewrite Suggestions (for content-writer or orchestrator; all within intake facts)

- S1 (fixes V1): Fernhollow header date to "March 2022 - Present" and keep a [CONFIRM start month] tag until the candidate verifies. Do not invent a different month.
- S2 (Gap 2): In the Fernhollow critique bullet, use the word directly, for example "Facilitate the weekly design critique and mentor 2 mid-level designers (one has been promoted)." Optionally reference the 2023 Cascadia UX talk in the summary as evidence of communication. Do not write "excellent communication" as a claim.
- S3 (Gap 3): In the accessibility bullet or summary, state the context from the source, for example "Led accessibility audit and remediation to WCAG 2.1 AA on the web app in a healthcare setting, coordinating with legal." In the summary, "health tech" may replace or sit beside "healthcare" since Fernhollow is described as a telehealth company. No named regulations.
- S4 (Gap 1): Do not write product-area ownership or direct-report claims. If the candidate confirms (intake question 7), add an accurate line. Until then, strongest honest framing is already present: built Fern UI used by 5 product teams, mentors 2 designers, runs the critique. Consider "partnered with engineers and clinicians" since both are supported; do not add product-leader partnership without confirmation.
- S5 (A3): Add the Certifications & Awards section for the Ridgecrest Design Prize, or explicitly decide to keep it in Education only.
- S6 (A1): Confirm the portfolio URL with the https:// prefix.
- S7 (years): Leave "since 2017". Add an explicit years figure only after the candidate reconciles "8ish" with the dated history.

## 4. Fabrication Check (D3)

No fabricated claims found. Observations:
- Quillmark ARR bullet keeps the team-effort caveat and does not attribute growth solely to her. Good.
- "$" was dropped from the ARR figures; source also had no symbol. Keep as is until currency is confirmed.
- "coordinating closely with legal" is a mild paraphrase of "extensive coordination with legal"; acceptable.
- Freelance 2015-2016, the 2023 workshop, and the unfinished UX certificate are correctly absent.

## 5. Tags to Resolve Before Design (flagged only; they do not change the verdict)

- [MISSING - LinkedIn URL] (contact line).
- [MISSING - city] on Fernhollow Health, Quillmark, Copperline Transit Authority, and Ridgecrest (4 entries).
- [CONFIRM currency] on the Quillmark ARR bullet.
- [CONFIRM relative vs. percentage points] on the 22% trial-to-paid bullet.

Design should not start until these are resolved or deliberately dropped. Any unresolved bracket tag would be printed into the ATS output and read as literal text by parsers.

## 6. Design Handoff Notes

- Re-verify the FORBIDDEN items that cannot be judged in Markdown: no running header/footer, no embedded images, standard font, no CSS columns or flex layout for body text, URLs as raw text.
- Ship a plain-text version with the same heading names.
