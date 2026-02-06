---
name: ebm-calculator
description: Evidence-Based Medicine calculator for sensitivity, specificity, PPV, NPV, NNT, and likelihood ratios. Essential for clinical decision making and biostatistics education.
version: 1.0.0
category: Education
tags: [ebm, biostatistics, calculator, sensitivity, specificity, clinical-reasoning]
author: Medical Science Skills
license: MIT
---

# EBM Calculator

Evidence-Based Medicine diagnostic test calculator.

## Features

- Sensitivity / Specificity calculation
- PPV / NPV with prevalence adjustment
- Likelihood ratios (LR+ / LR-)
- Number Needed to Treat (NNT)
- Pre/post-test probability conversion

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `true_positives` | int | Yes | True positive count |
| `false_negatives` | int | Yes | False negative count |
| `true_negatives` | int | Yes | True negative count |
| `false_positives` | int | Yes | False positive count |
| `prevalence` | float | No | Disease prevalence (0-1) |

## Output Format

```json
{
  "sensitivity": "float",
  "specificity": "float",
  "ppv": "float",
  "npv": "float",
  "lr_positive": "float",
  "lr_negative": "float",
  "interpretation": "string"
}
```
