---
name: survival-analysis-km
description: Generates Kaplan-Meier survival curves, calculates survival statistics
  (log-rank test, median survival time), and estimates hazard ratios for clinical
  and biological survival data analysis. Triggered when user requests survival analysis,
  Kaplan-Meier plots, time-to-event analysis, or asks about survival statistics in
  biomedical contexts.
version: 1.0.0
category: Bioinfo
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

# Survival Analysis (Kaplan-Meier)

Kaplan-Meier survival analysis tool for clinical and biological research. Generates publication-ready survival curves with statistical tests.

## Features

- **Kaplan-Meier Curve Generation**: Publication-quality survival plots with confidence intervals
- **Statistical Tests**: Log-rank test, Wilcoxon test, Peto-Peto test
- **Hazard Ratios**: Cox proportional hazards regression with 95% CI
- **Summary Statistics**: Median survival time, restricted mean survival time (RMST)
- **Multi-group Analysis**: Supports 2+ comparison groups
- **Risk Tables**: Optional at-risk table below curves

## Usage

### Python Script

```bash
python scripts/main.py --input data.csv --time time_col --event event_col --group group_col --output results/
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--input` | Input CSV file path | Yes |
| `--time` | Column name for survival time | Yes |
| `--event` | Column name for event indicator (1=event, 0=censored) | Yes |
| `--group` | Column name for grouping variable | Optional |
| `--output` | Output directory for results | Yes |
| `--conf-level` | Confidence level (default: 0.95) | Optional |
| `--risk-table` | Include risk table in plot | Optional |

### Input Format

CSV with columns:
- **Time column**: Numeric, time to event or censoring
- **Event column**: Binary (1 = event occurred, 0 = censored/right-censored)
- **Group column**: Categorical variable for stratification

Example:
```csv
patient_id,time_months,death,treatment_group
P001,24.5,1,Drug_A
P002,36.2,0,Drug_A
P003,18.7,1,Placebo
```

### Output Files

- `km_curve.png`: Kaplan-Meier survival curve
- `km_curve.pdf`: Vector version for publications
- `survival_stats.csv`: Statistical summary (median survival, confidence intervals)
- `hazard_ratios.csv`: Cox regression results with HR and 95% CI
- `logrank_test.csv**: Pairwise comparison p-values
- `report.txt**: Human-readable summary report

## Technical Details

### Statistical Methods

1. **Kaplan-Meier Estimator**: Non-parametric maximum likelihood estimate of survival function
   - Product-limit estimator: Ŝ(t) = Π(tᵢ≤t) (1 - dᵢ/nᵢ)
   - Greenwood's formula for variance estimation

2. **Log-Rank Test**: Most widely used test for comparing survival curves
   - Null hypothesis: No difference between groups
   - Weighted by number at risk at each event time

3. **Cox Proportional Hazards**: Semi-parametric regression model
   - h(t|X) = h₀(t) × exp(β₁X₁ + β₂X₂ + ...)
   - Proportional hazards assumption checked via Schoenfeld residuals

### Dependencies

- `lifelines`: Core survival analysis library
- `matplotlib`, `seaborn`: Visualization
- `pandas`, `numpy`: Data handling
- `scipy`: Statistical tests

### Technical Difficulty: High ⚠️

This skill involves advanced statistical modeling. Results should be reviewed by a biostatistician, especially for:
- Proportional hazards assumption violations
- Small sample sizes (< 30 per group)
- Heavy censoring (> 50%)
- Time-varying covariates

## References

See `references/` folder for:
- Kaplan EL, Meier P (1958) original paper
- Cox DR (1972) regression models paper
- Sample datasets for testing
- Clinical reporting guidelines (ATN, CONSORT)


## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | str | Required | Input CSV file path |
| `--time` | str | Required | Column name for survival time |
| `--event` | str | Required |  |
| `--group` | str | Required |  |
| `--output` | str | Required | Output directory for results |
| `--conf-level` | float | 0.95 |  |
| `--risk-table` | str | Required | Include risk table in plot |
| `--figsize` | str | '10 |  |
| `--dpi` | int | 300 |  |

## Example

```bash
# Basic survival curve
python scripts/main.py \
  --input clinical_data.csv \
  --time overall_survival_months \
  --event death \
  --group treatment_arm \
  --output ./results/ \
  --risk-table
```

Output includes:
- Survival curves with 95% confidence bands
- Median survival: Drug A = 28.4 months (95% CI: 24.1-32.7), Placebo = 18.2 months (95% CI: 15.3-21.1)
- Log-rank test p-value: 0.0023
- Hazard ratio: 0.62 (95% CI: 0.45-0.85), p = 0.003

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
