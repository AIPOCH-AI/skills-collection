---
name: sample-size-power-calculator
description: Advanced sample size and power calculations for complex study designs
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Sample Size & Power Calculator (Advanced)

Advanced sample size and power calculations for complex study designs including survival analysis, clustered designs, and multiple comparisons.

## Usage

```bash
python scripts/main.py --test ttest --effect 0.5 --alpha 0.05 --power 0.8
python scripts/main.py --test survival --hazard-ratio 0.7 --alpha 0.05
```

## Test Types

- t-test (paired/independent)
- Chi-square test
- Log-rank test (survival)
- ANOVA
- Regression
- Clustered designs
- Non-inferiority trials

## Parameters

- `--test`: Statistical test type
- `--effect`: Effect size (Cohen's d, hazard ratio, etc.)
- `--alpha`: Significance level
- `--power`: Desired power
- `--allocation`: Group allocation ratio

## Output

- Required sample size
- Power curve data
- Sensitivity analysis
- Dropout-adjusted N

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
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
