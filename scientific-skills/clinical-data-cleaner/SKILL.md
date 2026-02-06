---
name: clinical-data-cleaner
description: Clean and standardize raw clinical trial data for SDTM compliance. Handles missing values, outliers, and data validation. Trigger when users need to process clinical datasets (DM, LB, VS domains), detect anomalies, or prepare data for regulatory submission.
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
