---
name: medical-email-polisher
description: Polishes draft emails into professional, context-appropriate medical correspondence. Supports various scenarios including communication with mentors, editors, colleagues, and patients.
version: 1.0.0
category: General
tags: [email, communication, professionalism, medical-writing, etiquette]
author: Medical Science Skills
license: MIT
---

# Medical Email Polisher

Transforms rough email drafts into polished, professional medical correspondence.

## Features

- Multiple context templates (mentor, editor, peer, patient)
- Tone adjustment (formal to semi-formal)
- Opening and closing optimization
- Grammar and clarity improvements
- HIPAA-aware patient communication

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `draft_text` | str | Yes | Rough email draft |
| `recipient_type` | str | Yes | "mentor", "editor", "colleague", "patient" |
| `purpose` | str | No | Email purpose/context |

## Output Format

```json
{
  "polished_email": "string",
  "subject_line": "string",
  "changes_made": ["string"],
  "tone_assessment": "string"
}
```
