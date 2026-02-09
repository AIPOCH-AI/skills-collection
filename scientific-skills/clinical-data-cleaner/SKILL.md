---
name: clinical-data-cleaner
description: Clean and standardize raw clinical trial data for CDISC SDTM compliance. Handles missing values, detects statistical and clinical outliers, validates domain structure, and generates audit trails for regulatory submissions.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
  skill-author: AIPOCH
---

# Clinical Data Cleaner

Clean, validate, and standardize clinical trial data to meet CDISC SDTM (Study Data Tabulation Model) standards for regulatory submissions. Handles missing data imputation, outlier detection using statistical and clinical domain rules, and generates comprehensive audit trails for FDA/EMA compliance.

**Key Capabilities:**
- **SDTM Domain Validation**: Verify required fields for DM (Demographics), LB (Laboratory), and VS (Vital Signs) domains
- **Missing Value Handling**: Multiple imputation strategies (mean, median, mode, forward fill, drop)
- **Outlier Detection**: Statistical methods (IQR, Z-score) and clinical domain-specific thresholds
- **Date Standardization**: Convert dates to ISO 8601 format for regulatory compliance
- **Audit Trail Generation**: Complete logging of all data modifications for regulatory review

---

## When to Use

**✅ Use this skill when:**
- Preparing **clinical trial data for regulatory submission** to FDA or EMA
- **Cleaning SDTM datasets** (DM, LB, VS domains) before analysis
- Handling **missing data** in clinical datasets with appropriate imputation strategies
- **Detecting outliers** in laboratory values or vital signs using clinical thresholds
- **Standardizing date formats** to meet CDISC requirements
- **Validating data integrity** before statistical analysis
- **Creating audit trails** for data cleaning procedures in regulatory submissions
- **Converting raw CRF data** to SDTM-compliant format

**❌ Do NOT use when:**
- Working with **non-clinical research data** (preclinical, in vitro) → Use general data cleaning tools
- Needing **statistical analysis** of cleaned data → Use SAS, R, or Python statistical packages
- Creating **SDTM datasets from scratch** → Use specialized SDTM mapping tools
- Performing **adverse event coding** (MedDRA) → Use `adverse-event-narrative` or coding tools
- Generating **clinical study reports** → Use CSR generation tools
- Handling **patient safety monitoring** during trial → Use safety surveillance systems
- Requiring **21 CFR Part 11 compliance** → Use validated clinical data management systems

**Related Skills:**
- **上游 (Upstream)**: `ecrf-designer`, `clinicaltrials-gov-parser`
- **下游 (Downstream)**: `adverse-event-narrative`, `statistical-analysis-advisor`

---

## Integration with Other Skills

**Upstream Skills:**
- `ecrf-designer`: Design eCRFs to capture data in SDTM-compliant format from the start
- `clinicaltrials-gov-parser`: Extract protocol information to understand expected data structure
- `data-management-plan-creator`: Plan data cleaning procedures before study start

**Downstream Skills:**
- `adverse-event-narrative`: Process adverse event data after cleaning
- `statistical-analysis-advisor`: Analyze cleaned data with appropriate statistical methods
- `regulatory-submission-checker`: Validate final datasets meet submission requirements

**Complete Workflow:**
```
Raw CRF Data → clinical-data-cleaner → SDTM Datasets → statistical-analysis-advisor → Regulatory Submission
```

---

## Core Capabilities

### 1. SDTM Domain Validation

Validate that datasets contain all required fields for specific SDTM domains (DM, LB, VS) per CDISC Implementation Guide.

```python
from scripts.main import ClinicalDataCleaner
import pandas as pd

# Initialize cleaner for Demographics domain
cleaner = ClinicalDataCleaner(domain='DM')

# Load sample demographics data
dm_data = pd.DataFrame({
    'STUDYID': ['STUDY001'] * 5,
    'USUBJID': ['001-001', '001-002', '001-003', '001-004', '001-005'],
    'SUBJID': ['001', '002', '003', '004', '005'],
    'RFSTDTC': ['2023-01-15', '2023-01-16', '2023-01-17', None, '2023-01-19'],
    'RFENDTC': ['2023-07-15', '2023-07-16', None, '2023-07-18', '2023-07-19'],
    'SITEID': ['001'] * 5,
    'AGE': [45, 52, None, 38, 61],
    'SEX': ['M', 'F', 'M', 'F', 'M'],
    'RACE': ['WHITE', 'BLACK', 'ASIAN', 'WHITE', None]
})

# Validate domain structure
is_valid, missing_fields = cleaner.validate_domain(dm_data)

print(f"Domain Validation Results:")
print(f"  Valid: {is_valid}")
if missing_fields:
    print(f"  Missing required fields: {missing_fields}")
else:
    print(f"  ✓ All required fields present")

# Check data completeness
completeness = dm_data.notna().mean() * 100
print(f"\nData Completeness:")
for col, pct in completeness.items():
    status = "✓" if pct > 90 else "⚠" if pct > 70 else "✗"
    print(f"  {status} {col}: {pct:.1f}%")
```

**Required Fields by Domain:**

| Domain | Required Fields | Description |
|--------|----------------|-------------|
| **DM** | STUDYID, USUBJID, SUBJID, RFSTDTC, RFENDTC, SITEID, AGE, SEX, RACE | Demographics |
| **LB** | STUDYID, USUBJID, LBTESTCD, LBCAT, LBORRES, LBORRESU, LBSTRESC, LBDTC | Laboratory |
| **VS** | STUDYID, USUBJID, VSTESTCD, VSORRES, VSORRESU, VSSTRESC, VSDTC | Vital Signs |

**Best Practices:**
- ✅ **Validate early** - check domain structure before cleaning operations
- ✅ **Document missing fields** - note any expected fields not present
- ✅ **Use USUBJID** - ensure unique subject identifiers across domains
- ✅ **Standardize SITEID** - consistent site identification

**Common Issues and Solutions:**

**Issue: Missing required fields**
- Symptom: Validation fails with missing field errors
- Solution: Check data export process; add missing fields from source data

**Issue: Field name mismatches**
- Symptom: Fields exist but with different names
- Solution: Map field names to SDTM standards; document mappings

### 2. Missing Value Handling

Impute or handle missing values using multiple strategies appropriate for clinical data.

```python
from scripts.main import ClinicalDataCleaner
import pandas as pd
import numpy as np

# Create sample data with missing values
data = pd.DataFrame({
    'STUDYID': ['STUDY001'] * 10,
    'USUBJID': [f'001-{i:03d}' for i in range(1, 11)],
    'AGE': [45, 52, np.nan, 38, 61, 55, np.nan, 42, 58, np.nan],
    'WEIGHT': [70.5, 65.2, 82.1, np.nan, 75.8, 68.9, 71.2, np.nan, 79.5, 66.3],
    'HEIGHT': [175, 162, 180, 168, np.nan, 172, 165, 178, np.nan, 170],
    'SEX': ['M', 'F', 'M', 'F', 'M', 'F', None, 'M', 'F', 'M']
})

print("Original Data:")
print(f"  Missing values: {data.isnull().sum().sum()}")
print(f"  Completeness: {(1 - data.isnull().sum().sum() / data.size) * 100:.1f}%")

# Test different imputation strategies
strategies = ['mean', 'median', 'mode', 'forward']

for strategy in strategies:
    cleaner = ClinicalDataCleaner(domain='DM', missing_strategy=strategy)
    cleaned = cleaner.handle_missing_values(data.copy())
    
    missing_after = cleaned.isnull().sum().sum()
    print(f"\nStrategy: {strategy}")
    print(f"  Missing after: {missing_after}")
    print(f"  Actions logged: {len(cleaner.cleaning_log)}")
```

**Imputation Strategies:**

| Strategy | Method | Best For | Caution |
|----------|--------|----------|---------|
| **drop** | Remove rows with any missing values | Small missing % | Reduces sample size |
| **mean** | Replace with column mean | Normally distributed | Affects variance |
| **median** | Replace with column median | Skewed distributions | Default recommendation |
| **mode** | Replace with most frequent value | Categorical data | May not be representative |
| **forward** | Forward fill (LOCF) | Time-series data | Last observation bias |

**Best Practices:**
- ✅ **Prefer median for continuous** - robust to outliers
- ✅ **Document imputation** - record all imputed values in audit trail
- ✅ **Stratify by group** - impute within treatment arms separately if possible
- ✅ **Sensitivity analysis** - test if results change with different strategies

**Common Issues and Solutions:**

**Issue: Too many missing values**
- Symptom: >20% missing for key variables
- Solution: Consider exclusion criteria; investigate data collection issues

**Issue: MNAR (Missing Not At Random)**
- Symptom: Missing values correlated with outcome
- Solution: Use multiple imputation; consult statistician

### 3. Outlier Detection and Handling

Detect anomalous values using statistical methods and clinical domain knowledge.

```python
from scripts.main import ClinicalDataCleaner
import pandas as pd

# Sample laboratory data with outliers
lb_data = pd.DataFrame({
    'STUDYID': ['STUDY001'] * 8,
    'USUBJID': [f'001-{i:03d}' for i in range(1, 9)],
    'LBTESTCD': ['GLUC', 'GLUC', 'GLUC', 'GLUC', 'HGB', 'HGB', 'HGB', 'HGB'],
    'LBORRES': [95, 450, 88, 920, 14.2, 4.8, 13.9, 25.3],  # 450, 920, 4.8, 25.3 are outliers
    'LBORRESU': ['mg/dL'] * 8,
    'LBDTC': ['2023-01-15'] * 8
})

# Test different outlier detection methods
methods = ['iqr', 'zscore', 'domain']

for method in methods:
    cleaner = ClinicalDataCleaner(
        domain='LB',
        outlier_method=method,
        outlier_action='flag'
    )
    
    flagged = cleaner.detect_outliers(lb_data.copy())
    outlier_col = 'LB_OUTLIER_FLAG'
    
    if outlier_col in flagged.columns:
        outlier_count = flagged[outlier_col].sum()
        print(f"\nMethod: {method}")
        print(f"  Outliers detected: {outlier_count}")
        
        # Show which values were flagged
        outliers = flagged[flagged[outlier_col] == 1]
        if not outliers.empty:
            print("  Flagged records:")
            for _, row in outliers.iterrows():
                print(f"    {row['USUBJID']}: {row['LBTESTCD']} = {row['LBORRES']}")
```

**Outlier Detection Methods:**

| Method | Description | Threshold | Best For |
|--------|-------------|-----------|----------|
| **IQR** | Interquartile Range | Q1 - 1.5×IQR, Q3 + 1.5×IQR | General use |
| **Z-score** | Standard deviations from mean | |z| > 3 | Normal distributions |
| **Domain** | Clinical thresholds | Parameter-specific | Clinical validation |

**Clinical Thresholds (Domain Method):**

| Parameter | Normal Range | Unit |
|-----------|--------------|------|
| **Glucose** | 50-500 | mg/dL |
| **Hemoglobin** | 5-20 | g/dL |
| **WBC** | 1,000-50,000 | cells/uL |
| **Creatinine** | 0.3-15 | mg/dL |
| **Systolic BP** | 70-220 | mmHg |
| **Pulse** | 40-180 | beats/min |
| **Temperature** | 94-108 | °F |

**Outlier Actions:**

| Action | Description | Use Case |
|--------|-------------|----------|
| **flag** | Mark outliers but keep data | Most common - preserves all data |
| **remove** | Delete outlier rows | Confirmed data entry errors |
| **cap** | Cap at 1st/99th percentile | Extreme values affect analysis |

**Best Practices:**
- ✅ **Prefer flagging** - don't remove data without investigation
- ✅ **Use domain method** - clinical thresholds most appropriate for LB/VS
- ✅ **Verify outliers** - check CRFs for data entry errors
- ✅ **Document decisions** - record why outliers were handled specific way

**Common Issues and Solutions:**

**Issue: Legitimate extreme values flagged**
- Symptom: Pathologically high/low values marked as outliers
- Solution: Use domain method; verify against normal ranges

**Issue: Too many outliers detected**
- Symptom: >10% of data flagged
- Solution: Adjust thresholds; investigate data quality issues

### 4. Date Standardization

Standardize date formats to ISO 8601 (YYYY-MM-DDTHH:MM:SS) for regulatory compliance.

```python
from scripts.main import ClinicalDataCleaner
import pandas as pd

# Sample data with various date formats
data = pd.DataFrame({
    'STUDYID': ['STUDY001'] * 5,
    'USUBJID': ['001-001', '001-002', '001-003', '001-004', '001-005'],
    'RFSTDTC': [
        '2023-01-15',           # ISO format
        '01/16/2023',           # US format
        '2023-01-17 09:30:00',  # With time
        None,                   # Missing
        '2023-01-19T14:45:00'   # ISO with time
    ],
    'RFENDTC': [
        '2023-07-15',
        '2023-07-16',
        '07/17/2023',
        '2023-07-18',
        None
    ]
})

print("Before standardization:")
print(data[['USUBJID', 'RFSTDTC', 'RFENDTC']])

# Standardize dates
cleaner = ClinicalDataCleaner(domain='DM')
standardized = cleaner.standardize_dates(data)

print("\nAfter standardization:")
print(standardized[['USUBJID', 'RFSTDTC', 'RFENDTC']])

# Check for unparseable dates
unparseable = standardized[['RFSTDTC', 'RFENDTC']].isna().sum()
if unparseable.any():
    print(f"\n⚠ Unparseable dates found:")
    print(unparseable[unparseable > 0])
```

**Date Formats Supported:**

| Input Format | Example | Output Format |
|--------------|---------|---------------|
| ISO Date | 2023-01-15 | 2023-01-15T00:00:00 |
| ISO DateTime | 2023-01-15T09:30:00 | 2023-01-15T09:30:00 |
| US Date | 01/15/2023 | 2023-01-15T00:00:00 |
| European Date | 15/01/2023 | 2023-01-15T00:00:00 |
| With time | 2023-01-15 09:30:00 | 2023-01-15T09:30:00 |

**SDTM Date Requirements:**

| Field Type | Format | Example |
|------------|--------|---------|
| **Date only** | YYYY-MM-DD | 2023-01-15 |
| **DateTime** | YYYY-MM-DDTHH:MM:SS | 2023-01-15T09:30:00 |
| **Partial** | YYYY-MM or YYYY | 2023-01 or 2023 |

**Best Practices:**
- ✅ **Convert all DTC fields** - any field ending in DTC
- ✅ **Handle partial dates** - preserve partial information if available
- ✅ **Flag unparseable dates** - manual review required
- ✅ **Time zone consideration** - document if time zones differ

**Common Issues and Solutions:**

**Issue: Ambiguous date formats**
- Symptom: 01/02/2023 could be Jan 2 or Feb 1
- Solution: Standardize input format; document source format

**Issue: Missing time components**
- Symptom: Only date available, no time
- Solution: Append T00:00:00 for consistency

### 5. Complete Cleaning Pipeline

Execute full cleaning workflow with all steps integrated.

```python
from scripts.main import ClinicalDataCleaner
import pandas as pd
import numpy as np

# Create comprehensive sample dataset
data = pd.DataFrame({
    'STUDYID': ['STUDY001'] * 10,
    'USUBJID': [f'001-{i:03d}' for i in range(1, 11)],
    'SUBJID': [f'{i:03d}' for i in range(1, 11)],
    'RFSTDTC': ['2023-01-15', '2023-01-16', None, '2023-01-18', '2023-01-19'] * 2,
    'RFENDTC': ['2023-07-15', None, '2023-07-17', '2023-07-18', '2023-07-19'] * 2,
    'SITEID': ['001'] * 10,
    'AGE': [45, 52, np.nan, 38, 61, 55, 48, 42, 58, np.nan],
    'SEX': ['M', 'F', 'M', 'F', None, 'M', 'F', 'M', 'F', 'M'],
    'RACE': ['WHITE', 'BLACK', 'ASIAN', 'WHITE', 'WHITE', None, 'BLACK', 'ASIAN', 'WHITE', 'BLACK']
})

# Initialize cleaner with full configuration
cleaner = ClinicalDataCleaner(
    domain='DM',
    missing_strategy='median',
    outlier_method='iqr',
    outlier_action='flag'
)

print("="*70)
print("CLINICAL DATA CLEANING PIPELINE")
print("="*70)
print(f"\nInput Dataset:")
print(f"  Rows: {len(data)}")
print(f"  Columns: {len(data.columns)}")
print(f"  Missing values: {data.isnull().sum().sum()}")

# Execute full cleaning
cleaned_data = cleaner.clean(data)

print(f"\nCleaning Complete:")
print(f"  Output rows: {len(cleaned_data)}")
print(f"  Actions logged: {len(cleaner.cleaning_log)}")

# Display cleaning log summary
print(f"\nCleaning Actions Summary:")
action_counts = {}
for action in cleaner.cleaning_log:
    action_type = action['action']
    action_counts[action_type] = action_counts.get(action_type, 0) + 1

for action, count in action_counts.items():
    print(f"  {action}: {count}")
```

**Pipeline Steps:**

1. **Domain Validation** - Verify required fields present
2. **Missing Value Handling** - Impute using specified strategy
3. **Outlier Detection** - Flag statistical/clinical outliers
4. **Outlier Handling** - Apply specified action (flag/remove/cap)
5. **Date Standardization** - Convert to ISO 8601 format

**Best Practices:**
- ✅ **Review each step** - verify outputs before proceeding
- ✅ **Save intermediate results** - for troubleshooting
- ✅ **Validate final output** - check against SDTM IG
- ✅ **Document parameters** - all cleaning decisions in report

### 6. Audit Trail Generation

Generate comprehensive cleaning reports for regulatory compliance.

```python
from scripts.main import ClinicalDataCleaner
import json

# After cleaning, save report
cleaner = ClinicalDataCleaner(domain='DM')
# ... perform cleaning ...

# Generate and save report
cleaner.save_report('cleaned_data.csv')

# Load and display report
with open('cleaned_data.report.json', 'r') as f:
    report = json.load(f)

print("CLEANING REPORT")
print("="*70)
print(f"Domain: {report['domain']}")
print(f"Timestamp: {report['timestamp']}")
print(f"\nParameters Used:")
for param, value in report['parameters'].items():
    print(f"  {param}: {value}")

print(f"\nActions Performed ({len(report['actions'])} total):")
for i, action in enumerate(report['actions'][:5], 1):  # Show first 5
    print(f"\n{i}. {action['action']}")
    print(f"   Time: {action['timestamp']}")
    for key, value in action.items():
        if key not in ['action', 'timestamp']:
            print(f"   {key}: {value}")

if len(report['actions']) > 5:
    print(f"\n... and {len(report['actions']) - 5} more actions")
```

**Report Contents:**

| Field | Description | Example |
|-------|-------------|---------|
| **domain** | SDTM domain cleaned | "DM" |
| **timestamp** | When cleaning occurred | "2026-02-09T10:30:00" |
| **parameters** | All cleaning settings | missing_strategy, etc. |
| **actions** | Detailed log of changes | imputation, outlier flagging |

**Best Practices:**
- ✅ **Archive all reports** - required for regulatory submissions
- ✅ **Version control** - track changes across cleaning iterations
- ✅ **Review before submission** - ensure all actions justified
- ✅ **Include in SAP** - reference in Statistical Analysis Plan

---

## Complete Workflow Example

**From raw data to SDTM-compliant dataset:**

```bash
# Step 1: Clean demographics data
python scripts/main.py \
  --input dm_raw.csv \
  --domain DM \
  --output dm_clean.csv \
  --missing-strategy median \
  --outlier-method iqr \
  --outlier-action flag

# Step 2: Clean laboratory data with domain thresholds
python scripts/main.py \
  --input lb_raw.csv \
  --domain LB \
  --output lb_clean.csv \
  --missing-strategy median \
  --outlier-method domain \
  --outlier-action flag

# Step 3: Clean vital signs
python scripts/main.py \
  --input vs_raw.csv \
  --domain VS \
  --output vs_clean.csv \
  --missing-strategy median \
  --outlier-method domain \
  --outlier-action flag
```

**Python API Usage:**

```python
from scripts.main import ClinicalDataCleaner
import pandas as pd

def clean_clinical_dataset(
    input_file: str,
    domain: str,
    output_file: str,
    missing_strategy: str = 'median',
    outlier_method: str = 'iqr',
    outlier_action: str = 'flag'
) -> dict:
    """
    Complete workflow for cleaning clinical trial data.
    
    Returns:
        Dictionary with cleaning statistics and file paths
    """
    print("="*70)
    print(f"CLINICAL DATA CLEANING - {domain} Domain")
    print("="*70)
    
    # Initialize cleaner
    cleaner = ClinicalDataCleaner(
        domain=domain,
        missing_strategy=missing_strategy,
        outlier_method=outlier_method,
        outlier_action=outlier_action
    )
    
    # Load data
    print(f"\nLoading data from: {input_file}")
    try:
        df = cleaner.load_data(input_file)
        print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return {"error": str(e)}
    
    # Validate domain
    is_valid, missing = cleaner.validate_domain(df)
    if not is_valid:
        print(f"⚠ Missing required fields: {missing}")
    else:
        print(f"✓ All required fields present")
    
    # Clean data
    print(f"\nCleaning with parameters:")
    print(f"  Missing strategy: {missing_strategy}")
    print(f"  Outlier method: {outlier_method}")
    print(f"  Outlier action: {outlier_action}")
    
    df_cleaned = cleaner.clean(df)
    
    # Save cleaned data
    df_cleaned.to_csv(output_file, index=False)
    print(f"\n✓ Cleaned data saved: {output_file}")
    
    # Save report
    cleaner.save_report(output_file)
    
    # Compile summary
    summary = {
        "input_file": input_file,
        "output_file": output_file,
        "domain": domain,
        "input_rows": len(df),
        "output_rows": len(df_cleaned),
        "rows_removed": len(df) - len(df_cleaned),
        "cleaning_actions": len(cleaner.cleaning_log),
        "validation_passed": is_valid,
        "missing_fields": missing if missing else []
    }
    
    print("\n" + "="*70)
    print("CLEANING SUMMARY")
    print("="*70)
    print(f"Input rows: {summary['input_rows']}")
    print(f"Output rows: {summary['output_rows']}")
    print(f"Rows removed: {summary['rows_removed']}")
    print(f"Cleaning actions: {summary['cleaning_actions']}")
    print(f"Validation: {'✓ Passed' if summary['validation_passed'] else '⚠ Warnings'}")
    print("="*70)
    
    return summary

# Execute workflow
results = clean_clinical_dataset(
    input_file="demographics_raw.csv",
    domain="DM",
    output_file="demographics_clean.csv",
    missing_strategy="median",
    outlier_method="iqr",
    outlier_action="flag"
)
```

**Expected Output Files:**

```
clinical_data/
├── dm_raw.csv                 # Original raw data
├── dm_clean.csv              # Cleaned SDTM data
├── dm_clean.report.json      # Cleaning audit trail
└── cleaning_summary.txt      # Human-readable summary
```

---

## Common Patterns

### Pattern 1: Regulatory Submission Preparation

**Scenario**: Preparing SDTM datasets for FDA submission.

```json
{
  "submission_type": "FDA NDA",
  "domains": ["DM", "LB", "VS", "AE", "MH"],
  "cleaning_approach": "Conservative - flag rather than remove",
  "validation": "CDISC SDTM IG v3.2",
  "audit_requirements": "Complete traceability of all changes",
  "deliverables": [
    "Cleaned datasets",
    "Cleaning reports",
    "Programming specifications"
  ]
}
```

**Workflow:**
1. Load raw data from EDC system
2. Validate against SDTM domain specifications
3. Clean using conservative settings (flag outliers)
4. Generate comprehensive audit trails
5. Validate final datasets with Pinnacle 21
6. Document all cleaning decisions
7. Package for regulatory submission

**Output Example:**
```
FDA Submission Package:
  
Datasets:
  ✓ dm.xpt (1,247 subjects)
  ✓ lb.xpt (45,678 records)
  ✓ vs.xpt (12,470 records)
  
Cleaning Statistics:
  - Missing values imputed: 234
  - Outliers flagged: 89
  - Date formats standardized: 1,247
  
Audit Trail:
  - Cleaning reports: 3 files
  - All actions documented
  - 21 CFR Part 11 compliant
  
Validation:
  ✓ Pinnacle 21: 0 errors, 3 warnings
  ✓ CDISC SDTM IG v3.2 compliant
```

### Pattern 2: Interim Analysis Data Preparation

**Scenario**: Cleaning data for interim analysis during ongoing trial.

```json
{
  "analysis_type": "Interim efficacy",
  "data_cutoff": "2023-12-31",
  "cleaning_priority": "Speed with quality",
  "domains_needed": ["DM", "LB", "VS"],
  "outlier_handling": "Flag for statistician review",
  "timeline": "3 days"
}
```

**Workflow:**
1. Extract data with cutoff date
2. Quick validation of key fields
3. Impute missing values with median
4. Flag outliers (don't remove)
5. Standardize dates
6. Deliver to statistics team
7. Document known issues

**Output Example:**
```
Interim Analysis Dataset:
  Data cutoff: 2023-12-31
  Subjects: 456/500 enrolled
  
Cleaning Summary:
  - Processing time: 2 hours
  - Missing values: 45 (imputed)
  - Outliers flagged: 12
  - Ready for analysis: Yes
  
Notes for Statistician:
  - 3 subjects with incomplete follow-up
  - 1 site with delayed data entry
  - All outliers reviewed and plausible
```

### Pattern 3: Database Migration Cleanup

**Scenario**: Cleaning data when migrating between data management systems.

```json
{
  "migration_type": "EDC system upgrade",
  "source_system": "Legacy EDC",
  "target_system": "New Veeva",
  "challenges": [
    "Different date formats",
    "Field name changes",
    "Encoding issues"
  ],
  "validation": "Compare before/after counts"
}
```

**Workflow:**
1. Export all data from legacy system
2. Map old field names to SDTM
3. Standardize formats (dates, categories)
4. Clean missing/outlier values
5. Validate record counts match
6. Test import to new system
7. Document all transformations

**Output Example:**
```
Database Migration Results:
  Legacy records: 15,678
  Migrated records: 15,678
  Match: ✓ 100%
  
Transformations Applied:
  - Date format: 23,456 fields
  - Field names: 156 mappings
  - Missing values: 234 imputed
  - Outliers: 45 flagged
  
Validation:
  ✓ Subject counts match
  ✓ Record counts match
  ✓ Critical values preserved
  ✓ Import to new system successful
```

### Pattern 4: External Data Integration

**Scenario**: Integrating external lab data with clinical database.

```json
{
  "data_source": "Central lab",
  "integration_type": "LB domain augmentation",
  "challenges": [
    "Different units",
    "Varying reference ranges",
    "Date/time zone issues"
  ],
  "cleaning_focus": "Standardization and validation"
}
```

**Workflow:**
1. Load central lab data export
2. Map local lab codes to LBTESTCD
3. Standardize units (convert if needed)
4. Validate against reference ranges
5. Handle date/time zones
6. Merge with existing LB data
7. Validate no duplicates

**Output Example:**
```
Central Lab Integration:
  External records: 8,234
  Successfully integrated: 8,234 (100%)
  
Standardization:
  - Unit conversions: 234 records
  - Date adjustments: 8,234 records
  - Code mappings: 45 tests
  
Validation:
  ✓ No duplicate records
  ✓ All USUBJID matched
  ✓ Units standardized
  ✓ Reference ranges aligned
  
Data Quality:
  - Outliers flagged: 23
  - Missing values: 0
  - Ready for analysis: Yes
```

---

## Quality Checklist

**Pre-Cleaning:**
- [ ] **CRITICAL**: Verify input data is from validated source (EDC, not draft)
- [ ] Confirm data export date and cutoff
- [ ] Check file format (CSV/Excel) and encoding
- [ ] Verify domain specification (DM, LB, VS)
- [ ] Review study protocol for expected data structure
- [ ] Check for data lock status
- [ ] Confirm access permissions and data security
- [ ] Document raw data file location (for audit)

**Cleaning Configuration:**
- [ ] **CRITICAL**: Select appropriate missing value strategy for data type
- [ ] Choose outlier method appropriate for domain (use 'domain' for LB/VS)
- [ ] Set outlier action based on regulatory requirements (prefer 'flag')
- [ ] Review custom configuration if provided
- [ ] Confirm cleaning parameters with statistician
- [ ] Document rationale for all parameter choices
- [ ] Check if stratification needed (by site, treatment arm)
- [ ] Validate cleaning approach in Statistical Analysis Plan

**During Cleaning:**
- [ ] **CRITICAL**: Review validation warnings (missing fields)
- [ ] Check missing value imputation counts
- [ ] Review outlier detection results
- [ ] Verify flagged outliers are appropriate
- [ ] Check date standardization success rate
- [ ] Monitor for unexpected data loss
- [ ] Review cleaning log for anomalies
- [ ] Compare row counts before/after

**Post-Cleaning:**
- [ ] **CRITICAL**: Validate cleaned data against CDISC SDTM IG
- [ ] Check Pinnacle 21 (or similar) validation results
- [ ] Review all cleaning actions in audit trail
- [ ] Verify SDTM domain structure correct
- [ ] Test import to analysis software (SAS, R)
- [ ] Generate summary statistics for key variables
- [ ] Compare with expected ranges
- [ ] Document any deviations from protocol

**Regulatory Compliance:**
- [ ] **CRITICAL**: All cleaning actions documented with rationale
- [ ] Audit trail complete and archived
- [ ] Cleaning programs under version control
- [ ] Validation documentation complete
- [ ] Reviewed by independent QC (if required)
- [ ] Approved by statistician/medical monitor
- [ ] Aligned with Statistical Analysis Plan
- [ ] Ready for regulatory submission

---

## Common Pitfalls

**Data Quality Issues:**
- ❌ **Cleaning raw/draft data** → Final data different from cleaned
  - ✅ Only clean locked/validated data
  
- ❌ **Removing outliers without investigation** → Lose legitimate extreme values
  - ✅ Flag outliers; review before removing
  
- ❌ **Inappropriate imputation** → Biases statistical analysis
  - ✅ Choose strategy based on missingness mechanism
  
- ❌ **Ignoring missing patterns** → MNAR data treated as MCAR
  - ✅ Analyze missingness patterns; consult statistician

**Regulatory Issues:**
- ❌ **Incomplete audit trail** → Regulatory rejection
  - ✅ Log every single change with rationale
  
- ❌ **Changing data without documentation** → Compliance violation
  - ✅ Never modify raw data; create new cleaned dataset
  
- ❌ **Not validating against SDTM IG** → Submission issues
  - ✅ Always run CDISC validation tools
  
- ❌ **Cleaning after database lock** → Protocol violation
  - ✅ Clean before lock; any post-lock changes need documented approval

**Technical Issues:**
- ❌ **Wrong date parsing** → Incorrect temporal relationships
  - ✅ Validate date formats; check against CRFs
  
- ❌ **Unit conversion errors** → Invalid clinical values
  - ✅ Double-check all unit conversions
  
- ❌ **Subject ID mismatches** → Data linkage failures
  - ✅ Verify USUBJID consistency across domains
  
- ❌ **Overwriting original files** → Data loss
  - ✅ Always save to new file; preserve raw data

---

## Troubleshooting

**Problem: Validation fails with missing required fields**
- Symptoms: Error listing missing SDTM fields
- Causes:
  - Data export missing columns
  - Field names different from SDTM
  - Partial data extract
- Solutions:
  - Check data export settings
  - Map field names to SDTM standards
  - Export complete dataset

**Problem: Too many outliers detected**
- Symptoms: >20% of data flagged as outliers
- Causes:
  - Wrong detection method for data distribution
  - Data quality issues
  - Incorrect units
- Solutions:
  - Use domain-specific thresholds for clinical data
  - Review raw data for systematic errors
  - Verify unit consistency

**Problem: Date parsing errors**
- Symptoms: Many dates converted to NaT (Not a Time)
- Causes:
  - Mixed date formats in source
  - Non-standard date strings
  - International date confusion (DD/MM vs MM/DD)
- Solutions:
  - Standardize date format in source system
  - Specify date format explicitly
  - Manually review unparseable dates

**Problem: Imputation creates unrealistic values**
- Symptoms: Imputed values outside plausible range
- Causes:
  - Wrong imputation strategy
  - Highly skewed data
  - Different subgroups mixed
- Solutions:
  - Use median instead of mean for skewed data
  - Impute within relevant subgroups
  - Consider multiple imputation

**Problem: Cleaned data larger than original**
- Symptoms: Output file bigger than input
- Causes:
  - Outlier flag columns added
  - Date format expanded (added time)
  - String columns widened
- Solutions:
  - Normal behavior - audit columns add size
  - Compress if needed for storage
  - Archive raw and cleaned separately

**Problem: Memory errors with large datasets**
- Symptoms: "MemoryError" or system freeze
- Causes:
  - Dataset too large for available RAM
  - Inefficient data types
  - Memory leaks in processing
- Solutions:
  - Process data in chunks
  - Optimize data types (categorical, smaller floats)
  - Use cloud-based processing for very large datasets
  - Consider database-based cleaning

---

## References

Available in `references/` directory:

- `sdtm_ig_guide.md` - CDISC SDTM Implementation Guide reference
- `domain_specs.json` - Domain-specific field requirements
- `outlier_thresholds.json` - Clinical outlier thresholds by parameter

**External Resources:**
- CDISC SDTM: https://www.cdisc.org/standards/foundational/sdtm
- CDASH: https://www.cdisc.org/standards/foundational/cdash
- FDA Study Data Standards: https://www.fda.gov/industry/study-data-standards-resources
- Pinnacle 21 Community: https://www.pinnacle21.com

---

## Scripts

Located in `scripts/` directory:

- `main.py` - Clinical data cleaning engine with SDTM validation

---

## SDTM Domain Reference

**DM (Demographics):**
- Key fields: USUBJID, AGE, SEX, RACE, RFSTDTC
- One record per subject
- Required for all studies

**LB (Laboratory):**
- Key fields: USUBJID, LBTESTCD, LBORRES, LBDTC
- Multiple records per subject
- Standardized test codes

**VS (Vital Signs):**
- Key fields: USUBJID, VSTESTCD, VSORRES, VSDTC
- Multiple records per subject
- Common tests: SYSBP, DIABP, PULSE, TEMP, WEIGHT, HEIGHT

---

**Last Updated**: 2026-02-09  
**Skill ID**: 189  
**Version**: 2.0 (K-Dense Standard)
