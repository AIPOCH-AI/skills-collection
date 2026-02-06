---
name: lay-summary-gen
description: Converts complex medical abstracts into plain language summaries for patients, caregivers, and the general public. Ensures readability while maintaining scientific accuracy.
version: 1.0.0
category: General
tags: [patient-education, plain-language, health-literacy, communication]
author: Medical Science Skills
license: MIT
---

# Lay Summary Gen

Generates plain-language summaries of medical research for non-expert audiences.

## Features

- Complex to simple language conversion
- Jargon elimination
- Reading level optimization (Grade 6-8)
- Key takeaways extraction
- EU CTR compliance support

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `abstract` | str | Yes | Original medical abstract |
| `target_audience` | str | No | "patients", "public", "media" |
| `max_words` | int | No | Maximum word count (default: 250) |

## Output Format

```json
{
  "lay_summary": "string",
  "reading_level": "string",
  "key_takeaways": ["string"],
  "word_count": "int",
  "jargon_replaced": [{"term": "plain"}]
}
```
