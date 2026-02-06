---
name: medical-unit-converter
description: Converts between medical laboratory units (mg/dL to mmol/L, etc.).
version: 1.0.0
category: Utility
tags: [units, conversion, laboratory, calculator]
author: Medical Science Skills
license: MIT
---

# Medical Unit Converter

Converts laboratory value units.

## Features

- Common lab conversions
- Glucose, cholesterol, creatinine
- Error checking
- Reference ranges

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | float | Yes | Value to convert |
| `from_unit` | str | Yes | Source unit |
| `to_unit` | str | Yes | Target unit |

## Output Format

```json
{
  "converted_value": "float",
  "formula": "string",
  "reference_range": "string"
}
```
