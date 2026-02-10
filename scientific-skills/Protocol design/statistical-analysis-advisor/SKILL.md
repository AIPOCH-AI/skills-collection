---
name: statistical-analysis-advisor
description: Recommends appropriate statistical methods (T-test vs ANOVA, etc.) based
  on dataset characteristics, performs assumption checking, and provides power analysis
  guidance. Trigger when user asks about choosing statistical tests, checking statistical
  assumptions, or needs guidance on experimental design and sample size calculations.
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

# Statistical Analysis Advisor

Intelligent statistical test recommendation engine that guides users through selecting the right statistical methods for their data.

## Capabilities

1. **Statistical Test Selection**
   - Compares and recommends between T-test, ANOVA, Chi-square, Mann-Whitney, Kruskal-Wallis, etc.
   - Considers data type, distribution, sample size, and research question
   - Provides decision tree logic for test selection

2. **Assumption Checking**
   - Normality tests (Shapiro-Wilk, Kolmogorov-Smirnov)
   - Homogeneity of variance (Levene's test, Bartlett's test)
   - Independence verification
   - Outlier detection guidance

3. **Power Analysis & Sample Size**
   - Effect size estimation (Cohen's d, eta-squared, Cramér's V)
   - Sample size calculations for desired power
   - Post-hoc power analysis

## Usage

```python
from scripts.main import StatisticalAdvisor

advisor = StatisticalAdvisor()

# Get test recommendation
recommendation = advisor.recommend_test(
    data_type="continuous",
    groups=2,
    independent=True,
    distribution="normal"
)

# Check assumptions
assumptions = advisor.check_assumptions(
    data=[group1, group2],
    test_type="independent_ttest"
)

# Power analysis
power = advisor.calculate_power(
    effect_size=0.5,
    alpha=0.05,
    sample_size=30
)
```

## Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| data_type | str | "continuous", "categorical", "ordinal" |
| groups | int | Number of groups/comparison levels |
| independent | bool | Independent or paired/related samples |
| distribution | str | "normal", "non-normal", "unknown" |
| sample_size | int | Current or planned sample size |

## Technical Difficulty: High ⚠️

**Warning**: Statistical recommendations have significant implications for research validity. This skill requires human verification of all recommendations before application in published research.

## References

- See `references/statistical_tests_guide.md` for detailed test selection criteria
- See `references/assumption_tests.md` for assumption checking procedures
- See `references/power_analysis_guide.md` for power calculation methods

## Limitations

- Does not perform actual data analysis (recommendations only)
- Cannot access raw data directly
- Complex multivariate designs may require specialized consultation
- Bayesian alternatives not covered comprehensively

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
