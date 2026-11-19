---
name: cv-section-template
description: Canonical Markdown section schema for cv-draft.md and raw-material.md. Apply when the intake-analyst organizes raw material, the content-writer writes or revises the draft, and the graphical-designer anchors the HTML layout.
---

# cv-section-template - Canonical CV Section Schema

Enforces a consistent Markdown structure for all CV files so every agent reads and writes to the same schema without ambiguity.

## Template

Use this exact structure for `cv-draft.md` and `raw-material.md`. Omit a section only if the candidate genuinely has no content for it - never omit Contact, Summary, or Experience.

```markdown
# [Full Name]

**[Target Role Title]**

[City, Country] | [email] | [phone] | [LinkedIn URL] | [Portfolio/GitHub URL if relevant]

---

## Professional Summary

[2-4 sentences. What the candidate does, at what level, for what type of organization, and what makes them distinctive. No buzzwords without evidence.]

---

## Experience

### [Job Title] | [Company Name] | [City] | [Start Month Year] - [End Month Year or Present]

- [Action verb + what you did + measurable result or scale]
- [Action verb + what you did + measurable result or scale]
- [Action verb + what you did + measurable result or scale]

*(Repeat for each role, most recent first)*

---

## Education

### [Degree, Field of Study] | [Institution Name] | [City] | [Graduation Year]

- [Relevant coursework, honors, thesis, GPA if strong - optional]

*(Repeat for each qualification, most recent first)*

---

## Skills

**[Category, e.g. Languages]:** [skill], [skill], [skill]
**[Category, e.g. Frameworks]:** [skill], [skill]
**[Category, e.g. Tools]:** [skill], [skill]

---

## Certifications & Awards *(omit section if empty)*

- [Certification/Award Name] | [Issuing Body] | [Year]

---

## Publications & Projects *(omit section if empty)*

- [Title] - [one-line description] | [URL or venue] | [Year]
```

## When to Apply

- `intake-analyst`: use this template as the target schema when organizing raw-material.md.
- `content-writer`: use this template as the exact structure for cv-draft.md. Do not add, rename, or reorder sections without an orchestrator decision.
- `graphical-designer`: use section headings from this template as anchors for the HTML layout.
- Compliant: all required sections present, headings match exactly (case-sensitive), most-recent-first ordering, no placeholder text remaining (replace with `[MISSING]` tags instead).
