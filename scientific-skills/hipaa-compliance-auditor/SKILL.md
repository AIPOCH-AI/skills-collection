---
name: hipaa-compliance-auditor
description: Automatically detect and de-identify PII (Personal Identifiable Information)
  and PHI (Protected Health Information) from clinical/medical text to ensure HIPAA
  compliance. Trigger when processing medical records, patient data, clinical notes,
  insurance information, or any healthcare-related text containing potential patient
  identifiers.
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

# HIPAA Compliance Auditor

A clinical-grade PII/PHI detection and de-identification tool for healthcare text data.

## Overview

This skill analyzes text for HIPAA-protected identifiers and automatically redacts or anonymizes them. It uses a combination of regex patterns, NLP entity recognition, and contextual analysis to identify 18 HIPAA identifier categories.

## Features

- **18 HIPAA Identifiers Detection**: Names, dates, SSN, MRN, phone/fax, email, geographic data, etc.
- **Automatic De-identification**: Replace PII with semantic tokens (e.g., `[PATIENT_NAME]`, `[DATE_1]`)
- **Context-Aware Detection**: Distinguishes between similar patterns (dates vs. lab values)
- **Audit Logging**: Track all redaction actions for compliance documentation
- **Confidence Scoring**: Flag uncertain detections for manual review

## Usage

### Command Line
```bash
python scripts/main.py --input "patient_text.txt" --output "deidentified.txt"
python scripts/main.py --text "Patient John Doe, SSN 123-45-6789..." --audit-log audit.json
```

### Python API
```python
from scripts.main import HIPAAAuditor

auditor = HIPAAAuditor()
result = auditor.deidentify("Patient John Doe was admitted on 2024-01-15...")
print(result.cleaned_text)  # De-identified output
print(result.detected_pii)  # List of found PII entities
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input` | string | - | Path to input text file |
| `text` | string | - | Direct text input (alternative to file) |
| `output` | string | - | Path for de-identified output file |
| `audit-log` | string | - | Path for JSON audit log |
| `confidence` | float | 0.7 | Minimum confidence threshold (0.0-1.0) |
| `preserve-structure` | bool | true | Maintain document structure (paragraphs, lists) |
| `custom-patterns` | string | - | Path to custom regex patterns JSON |

## HIPAA Identifier Categories Detected

1. Names (patient, relatives, employers)
2. Geographic subdivisions smaller than state
3. Dates (except year) related to individual
4. Phone numbers
5. Fax numbers
6. Email addresses
7. SSN
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers
14. URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any other unique identifying numbers

## Output Format

### De-identified Text
Original identifiers replaced with semantic tags:
- `[PATIENT_NAME_1]`, `[PATIENT_NAME_2]` ...
- `[DATE_1]`, `[DATE_2]` ...
- `[SSN_1]`
- `[PHONE_1]`, `[PHONE_2]` ...
- `[EMAIL_1]`
- `[MRN_1]` (Medical Record Number)
- `[ADDRESS_1]`

### Audit Log JSON
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "input_hash": "sha256:abc123...",
  "detections": [
    {
      "type": "PATIENT_NAME",
      "position": [10, 18],
      "confidence": 0.95,
      "replacement": "[PATIENT_NAME_1]",
      "original_length": 8
    }
  ],
  "statistics": {
    "total_pii_found": 5,
    "categories_detected": ["NAME", "DATE", "PHONE", "SSN"]
  }
}
```

## Technical Architecture

1. **Preprocessing**: Normalize text encoding, handle line breaks
2. **Regex Engine**: Pattern matching for structured identifiers (SSN, phone, email, MRN)
3. **NLP Pipeline**: spaCy NER for names, organizations, locations
4. **Context Filter**: Remove false positives (e.g., "Dr. Smith" vs. "smith fracture")
5. **Replacement Engine**: Sequential replacement with semantic tokens
6. **Validation**: Ensure no original PII remains in output

## Dependencies

- Python 3.9+
- spaCy (en_core_web_trf or en_core_web_lg)
- regex (for advanced pattern matching)
- Presidio (optional, for enhanced PII detection)

See `references/requirements.txt` for full dependency list.

## Limitations & Warnings

⚠️ **CRITICAL**: This tool is designed as a helper, not a replacement for human review.

- Context-dependent PII (e.g., rare disease names + location) may not be fully detected
- Unstructured narrative text may contain identifying information not caught by patterns
- Always perform manual QA on output before HIPAA-compliant release
- **AI Autonomous Acceptance Status**: 需人工检查 (Requires Manual Review)

## References

- `references/hipaa_safe_harbor_guide.pdf` - HIPAA Safe Harbor de-identification standards
- `references/pii_patterns.json` - Complete regex pattern definitions
- `references/test_cases/` - Sample clinical texts with expected outputs
- `references/requirements.txt` - Python dependencies

## Technical Difficulty: High

Complex NLP pipelines, contextual disambiguation, regulatory compliance requirements.

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
