---
name: discharge-summary-writer
description: Generate hospital discharge summaries from admission data, hospital course,
  medications, and follow-up plans. Trigger when user needs to create a discharge
  summary, compile inpatient medical records, or generate post-hospitalization documentation
  for patients.
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

# Discharge Summary Writer

Generate standardized, clinically accurate hospital discharge summaries by integrating all inpatient medical data.

## When to Use

- Patient discharge preparation requires comprehensive summary documentation
- Compiling admission, treatment, and discharge data into unified records
- Generating follow-up instructions and medication lists for post-discharge care
- Creating legally compliant discharge documentation for medical records

## Input Requirements

### Required Patient Data
```json
{
  "patient_info": {
    "name": "string",
    "gender": "string",
    "age": "number",
    "medical_record_number": "string",
    "admission_date": "YYYY-MM-DD",
    "discharge_date": "YYYY-MM-DD",
    "department": "string",
    "attending_physician": "string"
  },
  "admission_data": {
    "chief_complaint": "string",
    "present_illness_history": "string",
    "past_medical_history": "string",
    "physical_examination": "string",
    "admission_diagnosis": ["string"]
  },
  "hospital_course": {
    "treatment_summary": "string",
    "procedures_performed": ["string"],
    "significant_findings": "string",
    "complications": ["string"],
    "consultations": ["string"]
  },
  "discharge_status": {
    "discharge_diagnosis": ["string"],
    "discharge_condition": "string",
    "hospital_stay_days": "number"
  },
  "medications": {
    "discharge_medications": [
      {
        "name": "string",
        "dosage": "string",
        "frequency": "string",
        "route": "string",
        "duration": "string"
      }
    ]
  },
  "follow_up": {
    "instructions": "string",
    "follow_up_appointments": ["string"],
    "warning_signs": ["string"],
    "activity_restrictions": "string",
    "diet_instructions": "string"
  }
}
```

## Usage

### Python Script
```bash
python scripts/main.py --input patient_data.json --output discharge_summary.md --format standard
```

### Options
- `--input`: Path to JSON file containing patient data (required)
- `--output`: Output file path (default: discharge_summary.md)
- `--format`: Output format - `standard`, `structured`, or `json` (default: standard)
- `--template`: Custom template file path (optional)
- `--language`: Output language - `zh` or `en` (default: zh)

## Output Formats

### Standard Format
Human-readable markdown document following clinical discharge summary structure:
1. Patient Information
2. Admission Information
3. Hospital Course
4. Discharge Status
5. Discharge Medications
6. Follow-up Instructions
7. Physician Signature

### Structured Format
Sectioned markdown with clear headers for EMR integration.

### JSON Format
Machine-readable structured data for system integration.

## Technical Difficulty

**⚠️ HIGH - Manual Review Required**

This skill handles critical medical documentation. Output requires:
- Physician verification before use
- Compliance with local medical documentation standards
- Review for accuracy and completeness
- Institutional approval for template formats

## Safety Considerations

1. **Never use generated summaries without physician review**
2. **Verify all medication dosages and instructions**
3. **Confirm follow-up appointments with hospital scheduling system**
4. **Ensure discharge diagnoses match official medical records**
5. **Validate patient identifiers and dates**

## References

- `references/discharge_template.md` - Standard discharge summary template
- `references/medical_terms.json` - Standardized medical terminology
- `references/section_guidelines.md` - Guidelines for each section

## Limitations

- Does not access live EMR systems (requires manual data input)
- Medication interactions not validated
- Does not generate ICD-10 codes automatically
- Requires structured input data
- Output format must align with institutional requirements

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
