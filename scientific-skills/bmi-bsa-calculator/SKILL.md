---
name: bmi-bsa-calculator
description: Calculates Body Mass Index and Body Surface Area for dosing.
version: 1.0.0
category: Utility
tags: [bmi, bsa, dosing, calculator]
author: Medical Science Skills
license: MIT
---

# BMI & BSA Calculator

Calculates BMI and BSA for clinical use.

## Features

- BMI calculation
- BSA (DuBois formula)
- Dosing recommendations
- Category classification

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `weight_kg` | float | Yes | Weight in kg |
| `height_cm` | float | Yes | Height in cm |

## Output Format

```json
{
  "bmi": "float",
  "bsa": "float",
  "bmi_category": "string"
}
```
