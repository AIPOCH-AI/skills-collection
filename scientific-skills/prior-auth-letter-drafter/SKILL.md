---
name: prior-auth-letter-drafter
description: Draft prior authorization request letters for insurance companies with clinical justification. Trigger when user needs insurance pre-authorization for medical procedures, medications, or treatments requiring clinical documentation.
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
