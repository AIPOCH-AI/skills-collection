---
name: residency-interview-prep
description: Mock interview preparation tool for residency Match interviews. Generates common behavioral and clinical scenario questions with structured response frameworks and feedback.
version: 1.0.0
category: Education
tags: [residency, interview-prep, medical-education, match, career]
author: Medical Science Skills
license: MIT
---

# Residency Interview Prep

Residency interview preparation assistant for the NRMP Match process.

## Features

- Behavioral question generation (STAR format)
- Clinical scenario questions
- Program-specific research questions
- Response structure feedback
- Common question bank (100+ questions)

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question_type` | str | Yes | Type: "behavioral", "clinical", "program", "ethical" |
| `specialty` | str | No | Target specialty (e.g., "internal_medicine", "surgery") |
| `experience` | str | No | User's experience context |

## Output Format

```json
{
  "question": "string",
  "category": "string",
  "suggested_structure": "string",
  "key_points": ["string"],
  "common_pitfalls": ["string"]
}
```
