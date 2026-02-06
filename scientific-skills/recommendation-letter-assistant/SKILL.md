---
name: recommendation-letter-assistant
description: Helps faculty and mentors draft standardized recommendation letters for medical students, residents, and fellows. Ensures comprehensive coverage of applicant strengths.
version: 1.0.0
category: General
tags: [recommendation-letter, lor, faculty, mentorship, career]
author: Medical Science Skills
license: MIT
---

# Recommendation Letter Assistant

Assists mentors and faculty in writing effective recommendation letters.

## Features

- Structured letter templates
- Competency-based content suggestions
- Strength/weakness framing
- Specialty-specific customization
- MSPE/Dean's Letter alignment

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `applicant_name` | str | Yes | Name of applicant |
| `relationship` | str | Yes | "mentor", "course_director", "research_PI" |
| `duration` | str | Yes | Length of relationship |
| `key_strengths` | list | Yes | Applicant's top qualities |
| `context` | str | No | Residency, fellowship, job, etc. |

## Output Format

```json
{
  "letter_draft": "string",
  "opening": "string",
  "body_paragraphs": ["string"],
  "closing": "string",
  "competencies_addressed": ["string"]
}
```
