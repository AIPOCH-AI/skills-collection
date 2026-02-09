---
name: clinical-data-cleaner
description: Clean and standardize raw clinical trial data for SDTM compliance. Handles
  missing values, outliers, and data validation. Trigger when users need to process
  clinical datasets (DM, LB, VS domains), detect anomalies, or prepare data for regulatory
  submission.
version: 1.0.0
category: General
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

# Clinical Data Cleaner

Clean and standardize raw clinical trial data to meet CDISC SDTM standards.

## Features

- **Missing Value Handling**: Detect and impute missing data using multiple strategies
- **Outlier Detection**: Statistical detection of anomalous values using IQR, Z-score, and domain rules
- **SDTM Compliance**: Validate and transform data to CDISC SDTM standards
- **Domain Support**: DM (Demographics), LB (Laboratory), VS (Vital Signs)
- **Audit Trail**: Generate cleaning reports for regulatory compliance

## Usage

```bash
python scripts/main.py --input <raw_data.csv> --domain <DM|LB|VS> --output <cleaned.csv>
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input` | Yes | Path to raw clinical data file (CSV/Excel) |
| `--domain` | Yes | SDTM domain: DM (Demographics), LB (Laboratory), VS (Vital Signs) |
| `--output` | Yes | Output path for cleaned data |
| `--missing-strategy` | No | Missing value handling: `drop`, `mean`, `median`, `mode`, `forward` (default: `median`) |
| `--outlier-method` | No | Outlier detection: `iqr`, `zscore`, `domain` (default: `iqr`) |
| `--outlier-action` | No | Outlier handling: `flag`, `remove`, `cap` (default: `flag`) |
| `--config` | No | Custom configuration JSON file path |

### Examples

```bash
# Basic cleaning for Demographics domain
python scripts/main.py --input dm_raw.csv --domain DM --output dm_clean.csv

# Laboratory data with custom outlier handling
python scripts/main.py --input lb_raw.csv --domain LB --output lb_clean.csv \
  --missing-strategy mean --outlier-method zscore --outlier-action flag

# Vital Signs with custom config
python scripts/main.py --input vs_raw.csv --domain VS --output vs_clean.csv \
  --config custom_rules.json
```

## Output

Generates:
1. **Cleaned data file**: SDTM-compliant dataset
2. **Cleaning report**: JSON/CSV log of all changes made
3. **Validation summary**: Compliance check results

## Technical Details

**Difficulty**: Medium  
**Dependencies**: pandas, numpy, scipy  
**Standards**: CDISC SDTM IG v3.2+

## References

- `references/sdtm_ig_guide.md` - SDTM Implementation Guide
- `references/domain_specs.json` - Domain-specific validation rules
- `references/outlier_thresholds.json` - Clinical outlier thresholds by parameter

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
