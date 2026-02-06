---
name: date-calculator
description: Calculates gestational age and follow-up date windows.
version: 1.0.0
category: Utility
tags: [dates, pregnancy, follow-up, calculator]
author: Medical Science Skills
license: MIT
---

# Date Calculator

Calculates medical date windows.

## Features

- Gestational age
- Follow-up windows
- Visit scheduling
- Date adjustments

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | str | Yes | Start date (YYYY-MM-DD) |
| `calculation_type` | str | Yes | "gestational", "followup" |

## Output Format

```json
{
  "result_date": "string",
  "weeks": "int",
  "window": "string"
}
```
