# Quick Reference Guide

## Running the Narrative Generator

```bash
# Basic usage
python scripts/main.py --input case_data.json

# Save to file
python scripts/main.py --input case_data.json --output narrative.txt

# Validate input only
python scripts/main.py --input case_data.json --validate-only
```

## Required JSON Structure

```json
{
  "case_id": "string",
  "patient_age": "string (e.g., '45 years')",
  "patient_sex": "Male/Female/Unknown",
  "suspect_drugs": [...],
  "adverse_events": [...]
}
```

## Common Errors and Solutions

| Error | Solution |
|-------|----------|
| Missing required field | Add the missing field to JSON |
| Invalid JSON | Check JSON syntax with validator |
| File not found | Check file path |

## Output Sections

The narrative includes these sections in order:
1. Case identifier and date
2. Patient demographics
3. Medical history
4. Concomitant medications
5. Suspect drug(s)
6. Adverse event(s)
7. Diagnostic tests
8. Treatment
9. Dechallenge/rechallenge
10. Outcome
11. Causality assessment
12. Reporter comments

## CIOMS Compliance Checklist

Ensure your narrative includes:
- [ ] Patient age and sex (anonymized)
- [ ] Suspect drug name and indication
- [ ] Dose and therapy dates
- [ ] Event description with MedDRA term
- [ ] Onset date or latency
- [ ] Seriousness criteria
- [ ] Dechallenge result
- [ ] Final outcome
- [ ] Causality assessment
