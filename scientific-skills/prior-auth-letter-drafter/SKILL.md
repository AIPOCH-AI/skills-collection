---
name: prior-auth-letter-drafter
description: Draft prior authorization request letters for insurance companies with
  clinical justification. Trigger when user needs insurance pre-authorization for
  medical procedures, medications, or treatments requiring clinical documentation.
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

# Prior Authorization Letter Drafter

Generate professional prior authorization request letters for insurance companies with proper clinical justification and formatting.

## Features

- Insurance company-standard letter formatting
- Clinical justification with evidence-based reasoning
- ICD-10/CPT code integration
- Multiple authorization types (procedures, medications, DME)
- Customizable templates for different insurance carriers

## Usage

```bash
python scripts/main.py --input patient_data.json --output letter.docx
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patient_name | str | Yes | Full name of the patient |
| patient_id | str | Yes | Insurance member ID |
| provider_name | str | Yes | Requesting physician name |
| provider_npi | str | Yes | National Provider Identifier |
| service_type | str | Yes | Procedure, medication, or DME |
| cpt_code | str | No | CPT/HCPCS code |
| icd10_code | str | Yes | Diagnosis code(s) |
| clinical_justification | str | Yes | Medical necessity reasoning |
| insurance_carrier | str | Yes | Insurance company name |

### Service Types

- `procedure` - Surgical or diagnostic procedures
- `medication` - Specialty/brand-name drugs
- `dme` - Durable medical equipment
- `imaging` - Advanced imaging (MRI, CT, PET)

## Output

Generates a formatted prior authorization letter including:
- Header with provider and insurance information
- Patient demographics
- Requested service details with codes
- Clinical justification section
- Provider attestation and signature block

## Technical Notes

- Difficulty: Medium
- Dependencies: python-docx, jinja2
- Output format: DOCX (editable) or PDF

## References

- `references/letter_template.docx` - Base template
- `references/clinical_phrases.md` - Common clinical justification phrases
- `references/carrier_requirements.json` - Insurance-specific formatting rules

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
