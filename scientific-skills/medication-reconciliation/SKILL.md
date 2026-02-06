---
name: medication-reconciliation
description: Compare pre-admission medication lists with inpatient orders to identify omissions and duplicates
---

# Skill: Medication Reconciliation

**ID**: 164  
**Name**: Medication Reconciliation  
**Version**: 1.0.0  
**Author**: OpenClaw  
**Description**: Compare patient pre-admission medication lists with inpatient orders to automatically identify omitted or duplicated medications and improve medication safety.

---

## Function Overview

This Skill is used for medication reconciliation in medical scenarios. Main functions include:

1. **Data Import**: Support importing pre-admission medication lists and inpatient orders
2. **Medication Comparison**: Intelligent matching and comparison of two sets of medication data
3. **Omission Identification**: Automatically detect medications taken before admission but missing in inpatient orders
4. **Duplicate Detection**: Identify medications duplicated in both lists
5. **Report Generation**: Output structured reconciliation reports containing recommendations and warnings

---

## Input Format

### Pre-Admission Medications

```json
{
  "patient_id": "P001",
  "patient_name": "Zhang San",
  "admission_date": "2026-02-06",
  "medications": [
    {
      "drug_name": "Atorvastatin",
      "generic_name": "Atorvastatin",
      "dosage": "20mg",
      "frequency": "Once daily",
      "route": "Oral",
      "indication": "Hyperlipidemia"
    }
  ]
}
```

### Inpatient Orders

```json
{
  "patient_id": "P001",
  "order_date": "2026-02-06",
  "medications": [
    {
      "drug_name": "Atorvastatin Calcium Tablets",
      "generic_name": "Atorvastatin Calcium",
      "dosage": "20mg",
      "frequency": "qd",
      "route": "po",
      "order_type": "Long-term order"
    }
  ]
}
```

---

## Output Format

### Reconciliation Report

```json
{
  "report_id": "MR-20260206-001",
  "generated_at": "2026-02-06T08:30:00",
  "patient_id": "P001",
  "summary": {
    "pre_admission_count": 5,
    "inpatient_count": 4,
    "continued_count": 3,
    "discontinued_count": 2,
    "new_count": 1,
    "duplicates": []
  },
  "details": {
    "continued": [...],
    "discontinued": [...],
    "new_medications": [...],
    "duplicates": [...],
    "warnings": [...]
  }
}
```

---

## Usage

### Command Line Usage

```bash
# Basic usage
python scripts/main.py --pre-admission pre_meds.json --inpatient orders.json --output report.json

# Use example data
python scripts/main.py --example

# Detailed output
python scripts/main.py --pre-admission pre_meds.json --inpatient orders.json --verbose
```

### Python API

```python
from medication_reconciliation import MedicationReconciler

# Create reconciler
reconciler = MedicationReconciler()

# Load data
reconciler.load_pre_admission("pre_meds.json")
reconciler.load_inpatient_orders("orders.json")

# Execute reconciliation
report = reconciler.reconcile()

# Save report
report.save("report.json")
```

---

## Core Algorithms

### 1. Medication Matching Algorithm

- **Exact Match**: Exact match of generic names
- **Fuzzy Match**: Brand name similarity calculation (using Levenshtein distance)
- **Dosage Standardization**: Unify dosage units for comparison
- **Synonym Library**: Support common medication alias mapping

### 2. Duplicate Detection Rules

- Same generic name + same dosage range
- Same pharmacological class + same indication
- Time-overlapping dosing regimens

### 3. Omission Detection Logic

- Essential medications before admission (such as antihypertensives, hypoglycemics) missing in inpatient orders
- Judging clinical importance based on medication class

---

## Configuration Options

Configurable in `config.json`:

```json
{
  "matching": {
    "fuzzy_threshold": 0.85,
    "enable_generic_name_match": true,
    "enable_brand_name_match": true
  },
  "warnings": {
    "critical_drug_classes": ["Anticoagulants", "Hypoglycemics", "Antihypertensives", "Antiepileptics"],
    "discontinuation_alert": true
  },
  "output": {
    "format": "json",
    "include_recommendations": true
  }
}
```

---

## Notes

1. **Medical Disclaimer**: This tool is for reference only; final medication decisions must be confirmed by medical staff
2. **Data Privacy**: Patient data must comply with HIPAA/medical data protection regulations
3. **Medication Database**: It is recommended to regularly update medication aliases and interaction data

---

## Dependencies

- Python 3.8+
- Standard libraries: json, argparse, difflib, datetime
- Optional: fuzzywuzzy (enhanced fuzzy matching)

---

## Changelog

### v1.0.0 (2026-02-06)
- Initial version release
- Implemented basic medication comparison function
- Support omission and duplicate detection
- Generate structured reports
