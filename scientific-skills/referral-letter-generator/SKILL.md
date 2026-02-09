---
name: referral-letter-generator
description: Generate medical referral letters with patient summary, reason for referral,
  and relevant history. Trigger when user needs to create a professional medical referral
  document for transferring patient care to another healthcare provider.
version: 1.0.0
category: Clinical
tags:
- medical
- healthcare
- referral
- documentation
- clinical
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Medical Referral Letter Generator

A tool for generating professional medical referral letters for healthcare providers.

## Overview

This skill generates structured medical referral letters containing:
- Patient demographic information
- Reason for referral
- Relevant medical history
- Current medications and treatments
- Contact information for follow-up

## Use Cases

- Referring patients to specialists (cardiology, neurology, oncology, etc.)
- Transferring care between hospitals or clinics
- Urgent referrals for emergency conditions
- Routine specialist consultations

## Usage

### Command Line

```bash
python scripts/main.py --input patient_data.json --output referral_letter.pdf
```

### Python API

```python
from scripts.main import generate_referral_letter

letter = generate_referral_letter(
    patient_data={...},
    referring_provider={...},
    receiving_provider={...},
    reason="...",
    output_format="pdf"  # or "docx", "html", "txt"
)
```

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patient_name | str | Yes | Patient full name |
| patient_dob | str | Yes | Date of birth (YYYY-MM-DD) |
| patient_id | str | Yes | Medical record number |
| diagnosis | str | Yes | Primary diagnosis/reason for referral |
| history | str | No | Relevant medical history |
| medications | list | No | Current medications |
| urgency | str | No | Routine/Urgent/Emergent |
| referring_doctor | str | Yes | Referring physician name |
| receiving_provider | str | Yes | Target specialist/facility |

## Output Formats

- **PDF**: Professional formatted document (default)
- **DOCX**: Editable Word document
- **HTML**: Web-viewable format
- **TXT**: Plain text

## Example

```json
{
  "patient_name": "John Doe",
  "patient_dob": "1975-03-15",
  "diagnosis": "Suspected coronary artery disease",
  "reason": "Cardiology evaluation for chest pain",
  "urgency": "Urgent"
}
```

## Technical Notes

- **Difficulty**: Medium
- **Dependencies**: Python 3.8+, reportlab (PDF), python-docx (DOCX)
- **Compliance**: Follows HIPAA guidelines for PHI handling
- **Validation**: Input validation for required fields

## References

See `references/` folder for:
- Sample referral letter templates
- Medical terminology guidelines
- Privacy compliance checklist

## Safety & Privacy

- All patient data is processed locally
- No external API calls for patient information
- Automatic PHI redaction in logs
- Secure temporary file handling

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
