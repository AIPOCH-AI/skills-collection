---
name: shift-handover-summarizer
description: Automatically generate shift handover summaries based on EHR updates,
  highlighting critical events that occurred during the shift for healthcare settings.
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

# Shift Handover Summarizer

Automatically generate shift handover summaries based on EHR updates, highlighting critical events that occurred during the shift.

## Function Overview

This Skill is used in medical care scenarios to analyze EHR update content during the shift, intelligently extract key events, and generate structured handover summaries to help medical staff quickly understand patient status changes and important matters.

## Input Parameters

| Parameter Name | Type | Required | Description |
|--------|------|------|------|
| `patient_records` | array | Yes | List of EHR records updated during this shift |
| `shift_start_time` | string | Yes | Shift start time (ISO 8601 format) |
| `shift_end_time` | string | Yes | Shift end time (ISO 8601 format) |
| `department` | string | No | Department name |
| `include_vitals` | boolean | No | Whether to include vital signs summary (default: true) |
| `include_medications` | boolean | No | Whether to include medication summary (default: true) |
| `include_procedures` | boolean | No | Whether to include procedure/surgery summary (default: true) |
| `language` | string | No | Output language (zh-CN/en, default: zh-CN) |

### patient_records Data Structure

```json
{
  "patient_id": "P001",
  "patient_name": "Zhang San",
  "bed_number": "101",
  "age": 65,
  "gender": "Male",
  "diagnosis": "Acute Myocardial Infarction",
  "records": [
    {
      "timestamp": "2026-02-06T02:30:00Z",
      "type": "vital_signs",
      "data": {
        "heart_rate": 85,
        "blood_pressure": "120/80",
        "temperature": 37.2,
        "respiratory_rate": 18,
        "spo2": 98
      }
    },
    {
      "timestamp": "2026-02-06T04:15:00Z",
      "type": "medication",
      "data": {
        "drug_name": "Aspirin",
        "dosage": "100mg",
        "route": "Oral",
        "status": "Administered"
      }
    },
    {
      "timestamp": "2026-02-06T05:00:00Z",
      "type": "procedure",
      "data": {
        "procedure_name": "ECG Examination",
        "result": "ST elevation",
        "doctor": "Dr. Li"
      }
    },
    {
      "timestamp": "2026-02-06T05:30:00Z",
      "type": "event",
      "severity": "high",
      "data": {
        "description": "Patient chest pain worsened, relieved after sublingual nitroglycerin",
        "action_taken": "Notified on-call doctor, enhanced monitoring"
      }
    }
  ]
}
```

## Output Format

### Success Response

```json
{
  "success": true,
  "shift_summary": {
    "shift_period": {
      "start": "2026-02-06T00:00:00Z",
      "end": "2026-02-06T08:00:00Z"
    },
    "generated_at": "2026-02-06T07:55:00Z",
    "total_patients": 12,
    "critical_patients": 2,
    "summary_text": "...",
    "patients": [
      {
        "patient_id": "P001",
        "patient_name": "Zhang San",
        "bed_number": "101",
        "priority": "high",
        "key_events": [...],
        "vitals_summary": {...},
        "medication_summary": {...},
        "pending_tasks": [...]
      }
    ]
  }
}
```

### Summary Text Example

```
【Night Shift Handover Summary】2026-02-06 00:00 - 08:00

【Patients Requiring Attention】

🔴 Bed 101 Zhang San (Male, 65 years old) - Acute Myocardial Infarction
   ⚠️ Key Event: 05:30 Chest pain worsened, relieved after nitroglycerin treatment
   💊 Medication: Aspirin 100mg Oral
   📋 To-do: Continue cardiac monitoring, observe chest pain condition

🟡 Bed 103 Li Si (Female, 58 years old) - Hypertensive Emergency
   💉 Vital Signs: Blood pressure controlled, currently 135/85 mmHg
   📋 To-do: Morning blood pressure monitoring

【Patients in General Condition】
Beds 105-112: Condition stable, routine treatment in progress

【Shift Overview】
- New admissions: 3
- Transfers: 1  
- Resuscitations: 1
- Surgeries: 0
```

## Usage Examples

### Command Line Call

```bash
python scripts/main.py \
  --records data/shift_records.json \
  --shift-start "2026-02-06T00:00:00Z" \
  --shift-end "2026-02-06T08:00:00Z" \
  --department "Cardiology" \
  --output summary.json
```

### Programmatic Call

```python
from scripts.main import ShiftHandoverSummarizer

summarizer = ShiftHandoverSummarizer(
    shift_start="2026-02-06T00:00:00Z",
    shift_end="2026-02-06T08:00:00Z",
    department="Cardiology"
)

summary = summarizer.generate_summary(patient_records)
print(summary.to_text())  # Text format
print(summary.to_json())  # JSON format
```

## Key Event Classification

| Priority | Event Type | Description |
|--------|----------|------|
| 🔴 High | Resuscitation, deterioration, serious complications, abnormal vital signs | Requires immediate attention |
| 🟡 Medium | New symptoms, abnormal findings, medication adjustments, special procedures | Needs handover attention |
| 🟢 Low | Routine treatment, condition improvement, daily care | General record |

## Configuration Items

```json
{
  "thresholds": {
    "high_heart_rate": 120,
    "low_heart_rate": 50,
    "high_systolic_bp": 180,
    "low_systolic_bp": 90,
    "high_temperature": 38.5,
    "low_spo2": 90
  },
  "event_keywords": {
    "critical": ["resuscitation", "cardiac arrest", "dyspnea", "severe bleeding", "coma"],
    "warning": ["chest pain", "dizziness", "nausea", "fever", "blood pressure fluctuation"]
  }
}
```

## Dependencies

- Python >= 3.8
- No external dependencies (standard library implementation)

## Notes

1. Ensure input medical record timestamps are within the shift time range
2. Key event determination is based on preset thresholds and keywords; can be adjusted according to department characteristics
3. Summary text is recommended to be used with structured data to ensure information integrity
4. Involves patient privacy information; please ensure compliance with medical data protection regulations

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
