---
name: sample-size-basic
description: Basic sample size calculator for clinical research planning with common statistical scenarios
version: 1.0.0
category: Utility
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
