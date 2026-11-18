# ats-checklist - ATS Compliance Rule Set

Prevents formatting choices that cause applicant tracking systems to misparse or reject a CV before a human ever reads it. Applied every Review cycle by the ats-optimizer.

## Checklist

Tick each item. A single unchecked item in the FORBIDDEN list is a hard failure.

### FORBIDDEN (any one = ATS fail)

- [ ] Tables (HTML `<table>` or Markdown `| col |` syntax)
- [ ] Multi-column layouts (HTML `<div>` flex/grid, or text faked with tabs)
- [ ] Text boxes or frames
- [ ] Inline images or logos
- [ ] Headers or footers containing name/page number (most ATS strip these)
- [ ] Decorative Unicode (✓ ➤ ★ etc.) used as bullet replacements
- [ ] Non-standard fonts that may not map correctly when parsed
- [ ] Hyperlinks embedded in display text in the ATS-submitted version (URLs must appear as raw text: `https://...`)

### REQUIRED (all must be present)

- [ ] Candidate full name appears as the first line of the document
- [ ] Contact info (email + at least one of: phone, LinkedIn) in the first 5 lines
- [ ] Section headings are plain text (not images) and match the `loop-plugin:cv-section-template` heading names exactly
- [ ] Dates follow a consistent format throughout: `Month YYYY` or `MM/YYYY` - not mixed
- [ ] Experience entries list company name, job title, and dates - all three, every entry

### KEYWORD ALIGNMENT (scored, not pass/fail)

For each keyword cluster in the job description, rate the draft: **High** (appears 2+ times in context), **Medium** (appears once), **Low** (absent or only in skills list).

Clusters to check:
1. Core technical skills named in the job description
2. Seniority/level language (e.g. "senior", "lead", "principal")
3. Domain vocabulary (industry-specific terms)
4. Soft skills explicitly listed as requirements

## When to Apply

`ats-optimizer` applies this checklist during the Review phase. Write results to `ats-report.md`. A passing ATS report requires: zero FORBIDDEN items checked, all REQUIRED items present. Keyword alignment below Medium on more than two clusters triggers a recommendation for a content-writer revision pass before advancing to Design.
