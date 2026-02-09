---
name: icd10-cpt-coding-assistant
description: 'Automatically recommend ICD-10 diagnosis codes and CPT procedure codes
  from clinical notes. Trigger when: user provides clinical notes, patient encounter
  summaries, discharge summaries, or asks for medical coding assistance. Use for healthcare
  providers, medical coders, and billing professionals who need accurate code recommendations.'
version: 1.0.0
category: Clinical
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

# ICD-10 & CPT Coding Assistant

A medical coding assistant that parses clinical notes and recommends appropriate ICD-10 diagnosis codes and CPT procedure codes with confidence scoring.

## Overview

This skill analyzes clinical documentation to extract relevant medical information and map it to standardized coding systems:

- **ICD-10-CM**: International Classification of Diseases, 10th Revision, Clinical Modification (diagnosis codes)
- **CPT**: Current Procedural Terminology (procedure/service codes)

## Technical Difficulty: **HIGH** ⚠️

> **⚠️ HUMAN REVIEW REQUIRED**: Medical coding directly impacts billing, reimbursement, and clinical documentation. All recommendations must be verified by a certified medical coder or healthcare provider.

## Usage

```bash
python scripts/main.py --input "clinical_note.txt" [--format json|text]
```

Or use programmatically:

```python
from scripts.main import CodingAssistant

assistant = CodingAssistant()
result = assistant.analyze("Patient presents with acute bronchitis...")
print(result.icd10_codes)
print(result.cpt_codes)
```

## Input Format

Accepts clinical notes in various formats:
- Free-text narrative
- SOAP notes (Subjective, Objective, Assessment, Plan)
- Discharge summaries
- Progress notes
- Procedure reports

## Output Format

### ICD-10 Recommendations
```json
{
  "icd10_codes": [
    {
      "code": "J20.9",
      "description": "Acute bronchitis, unspecified",
      "confidence": 0.92,
      "evidence": ["cough for 5 days", "wheezing on exam"],
      "alternatives": ["J20.0", "J44.9"]
    }
  ]
}
```

### CPT Recommendations
```json
{
  "cpt_codes": [
    {
      "code": "99213",
      "description": "Office visit, established patient, moderate complexity",
      "confidence": 0.85,
      "evidence": ["detailed history", "low complexity decision making"],
      "time": "20 minutes"
    }
  ]
}
```

## Confidence Scoring

- **0.90-1.00**: High confidence - Clear documentation, unambiguous mapping
- **0.70-0.89**: Medium confidence - Good documentation, some interpretation required
- **0.50-0.69**: Low confidence - Incomplete documentation, multiple possibilities
- **<0.50**: Very low confidence - Insufficient information, manual review essential

## Limitations

1. **No Medical Advice**: This tool does not provide clinical advice or diagnoses
2. **Coding Complexity**: Cannot handle all coding nuances (comorbidities, sequencing, modifiers)
3. **Regional Variations**: May not account for payer-specific coding requirements
4. **Updates**: Code sets may not reflect the latest annual updates

## References

See `references/` folder for:
- `icd10_common_codes.json`: Frequently used ICD-10 codes by specialty
- `cpt_common_codes.json`: Frequently used CPT codes by specialty
- `coding_guidelines.md`: General coding guidelines and conventions

## Safety & Compliance

- **HIPAA Awareness**: Ensure de-identification of PHI before processing
- **Audit Trail**: Maintain records of automated recommendations for compliance
- **Human Oversight**: All codes must be reviewed and approved by qualified personnel

## Dependencies

- Python 3.8+
- See `requirements.txt` for package dependencies

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
