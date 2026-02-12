---
name: outlier-detection-handler
description: Statistical outlier identification and handling recommendations
version: 1.0.0
category: Data
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Outlier Detection & Handling

Identify and manage statistical outliers.

## Use Cases
- Data quality control
- Pre-analysis screening
- Regulatory compliance (FDA data integrity)

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data` | str | Yes | - | Path to dataset file (CSV/Excel) |
| `method` | str | No | "3-sigma" | Detection method: "3-sigma", "IQR", or "Grubbs" |
| `action` | str | No | "flag" | Handling action: "flag", "remove", or "winsorize" |

## Returns
- Outlier flagging with method details
- Handling recommendations
- Documentation for regulatory submission

## Example
Input: Biomarker measurements from 200 patients
Output: 5 outliers identified (2.5%), recommended action: investigate then winsorize

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

```bash
# Python dependencies
pip install -r requirements.txt
```

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
