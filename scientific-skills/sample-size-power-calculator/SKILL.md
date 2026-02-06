---
name: sample-size-power-calculator
description: Advanced sample size and power calculations for complex study designs
trigger: sample size, power, calculation, study design, statistics
tier: B
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
