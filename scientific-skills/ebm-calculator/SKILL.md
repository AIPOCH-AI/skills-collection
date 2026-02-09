---
name: ebm-calculator
description: Evidence-Based Medicine calculator for sensitivity, specificity, PPV,
  NPV, NNT, and likelihood ratios. Essential for clinical decision making and biostatistics
  education.
version: 1.0.0
category: Education
tags:
- ebm
- biostatistics
- calculator
- sensitivity
- specificity
- clinical-reasoning
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
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

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited
## Prerequisites

No additional Python packages required.

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support
