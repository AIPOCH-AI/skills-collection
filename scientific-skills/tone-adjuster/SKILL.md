---
name: tone-adjuster
description: Converts medical text between academic rigor and patient-friendly tones. Supports bidirectional transformation maintaining accuracy while adjusting accessibility.
version: 1.0.0
category: General
tags: [tone, readability, patient-education, academic-writing, translation]
author: Medical Science Skills
license: MIT
---

# Tone Adjuster

Bidirectional tone converter for medical text - academic to patient-friendly and vice versa.

## Features

- Academic ↔️ Layperson tone conversion
- Medical jargon translation
- Readability scoring
- Preserves medical accuracy
- Multiple adjustment levels

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | str | Yes | Input medical text |
| `target_tone` | str | Yes | "academic", "patient_friendly", "professional" |
| `level` | str | No | "light", "moderate", "heavy" adjustment |

## Output Format

```json
{
  "converted_text": "string",
  "original_tone": "string",
  "target_tone": "string",
  "readability_score": "float",
  "changes_made": ["string"]
}
```
