---
name: adverse-event-narrative
description: Generate CIOMS-compliant adverse event narratives for Individual Case
  Safety Report (ICSR). Trigger when user provides adverse event data, patient information,
  suspect drug details, or requests pharmacovigilance narrative writing. Outputs structured
  ICSR-ready narrative following CIOMS I and E2B standards.
version: 1.0.0
category: Pharma
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

# Adverse Event Narrative Generator

Generate CIOMS-compliant adverse event narratives for Individual Case Safety Report (ICSR) submissions.

## Overview

This skill creates structured, medically accurate narratives that meet international pharmacovigilance standards (CIOMS I, ICH E2B R3). The narrative synthesizes patient demographics, medical history, concomitant medications, suspect product details, adverse events, and outcome information into a standardized format suitable for regulatory reporting.

## Use Cases

- Draft ICSR narratives for regulatory submissions
- Convert raw case data into CIOMS-compliant text
- Standardize adverse event documentation across teams
- Prepare safety reports for health authorities
- Generate case summaries for signal detection

## Input Requirements

### Required Fields

| Field | Description | Format |
|-------|-------------|--------|
| `case_id` | Unique case identifier | String |
| `patient_age` | Patient age at event | Number + unit (years/months) |
| `patient_sex` | Biological sex | Male/Female/Unknown |
| `suspect_drugs` | Suspected medications | Array of drug objects |
| `adverse_events` | Reported reactions | Array of MedDRA PT terms |

### Drug Object Structure

```json
{
  "drug_name": "Brand/Generic name",
  "indication": "Medical condition treated",
  "dose": "Dosage amount",
  "frequency": "Dosing frequency",
  "route": "Administration route",
  "start_date": "YYYY-MM-DD",
  "stop_date": "YYYY-MM-DD or ongoing",
  "lot_number": "Batch/lot number (if known)"
}
```

### Optional Fields

| Field | Description |
|-------|-------------|
| `medical_history` | Significant pre-existing conditions |
| `concomitant_drugs` | Other medications at time of event |
| `diagnostic_tests` | Lab results, imaging, procedures |
| `dechallenge` | Effect after suspect drug withdrawal |
| `rechallenge` | Effect after re-administration |
| `outcome` | Final status (recovered/fatal/ongoing) |
| `causality` | Reporter's causality assessment |

## Output Format

The generated narrative follows CIOMS I standard sections:

1. **Patient Demographics** - Age, sex, relevant characteristics
2. **Medical History** - Significant past conditions
3. **Suspect Drug(s)** - Details of medication(s) in question
4. **Adverse Event** - Detailed description of reaction(s)
5. **Diagnostic Results** - Relevant test findings
6. **Treatment** - Medical management of the event
7. **Outcome** - Final patient status
8. **Causality Assessment** - Reporter's opinion on relationship

## Usage

```python
python scripts/main.py --input case_data.json --output narrative.txt
```

### JSON Input Example

```json
{
  "case_id": "2024-ICSR-001",
  "patient_age": "58 years",
  "patient_sex": "Female",
  "weight_kg": 65,
  "height_cm": 165,
  "medical_history": ["Hypertension", "Type 2 diabetes mellitus"],
  "suspect_drugs": [
    {
      "drug_name": "Metformin",
      "indication": "Type 2 diabetes mellitus",
      "dose": "1000 mg",
      "frequency": "twice daily",
      "route": "oral",
      "start_date": "2024-01-15",
      "stop_date": "2024-02-01"
    }
  ],
  "concomitant_drugs": [
    {
      "drug_name": "Lisinopril",
      "indication": "Hypertension"
    }
  ],
  "adverse_events": [
    {
      "meddra_pt": "Lactic acidosis",
      "onset_date": "2024-01-28",
      "severity": "Severe",
      "seriousness": "Hospitalization"
    }
  ],
  "diagnostic_tests": [
    {
      "test": "Serum lactate",
      "value": "8.5 mmol/L",
      "reference_range": "0.5-2.2 mmol/L",
      "date": "2024-01-29"
    }
  ],
  "dechallenge": "Positive - lactate normalized after discontinuation",
  "rechallenge": "Not performed",
  "outcome": "Recovered with sequelae",
  "causality": "Probable"
}
```

## Technical Notes

**Difficulty:** High ⚠️

This skill requires:
- Medical domain knowledge for accurate terminology
- Understanding of pharmacovigilance regulations
- Temporal relationship assessment
- MedDRA coding awareness
- Causality evaluation principles

**Limitations:**
- Does not replace qualified healthcare professional review
- Requires verification of medical facts
- Causality assessment is based on reporter input, not independent evaluation
- Temporal associations do not establish causation

## References

- CIOMS I: International Reporting of Adverse Drug Reactions
- ICH E2B(R3): Electronic Transmission of Individual Case Safety Reports
- MedDRA: Medical Dictionary for Regulatory Activities
- GVP Module VI: Collection, Management and Submission of Reports of Suspected Adverse Reactions

See `references/` folder for detailed guidelines and templates.

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

No additional Python packages required.

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
