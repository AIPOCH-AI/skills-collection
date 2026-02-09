---
name: sample-size-basic
description: Basic sample size calculator for clinical research planning with common
  statistical scenarios
version: 1.0.0
category: Utility
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Sample Size (Basic)

Basic sample size estimation for clinical research planning.

## Use Cases
- Quick sample size estimates for grant proposals
- Preliminary study design calculations
- Educational purposes for statistics training

## Parameters
- `test_type`: Type of test (t_test, chi_square, proportion)
- `alpha`: Significance level (default 0.05)
- `power`: Statistical power (default 0.80)
- `effect_size`: Expected effect size
- `baseline_rate`: Baseline proportion (for proportion tests)

## Returns
- Required sample size per group
- Total sample size
- Statistical assumptions summary

## Example
Input: Two-sample t-test, alpha=0.05, power=0.80, effect_size=0.5
Output: n=64 per group, total=128 subjects

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
