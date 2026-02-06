---
name: interview-mock-partner
description: Simulates behavioral interview questions for medical professionals.
version: 1.0.0
category: Career
tags: [interview, mock, behavioral, career]
author: Medical Science Skills
license: MIT
---

# Interview Mock Partner

Simulates medical job interview scenarios.

## Features

- Behavioral questions
- Response feedback
- Common scenarios
- Improvement tips

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `position` | str | Yes | Target position |
| `experience_level` | str | Yes | "entry", "mid", "senior" |

## Output Format

```json
{
  "questions": ["string"],
  "sample_answers": ["string"],
  "tips": ["string"]
}
```
