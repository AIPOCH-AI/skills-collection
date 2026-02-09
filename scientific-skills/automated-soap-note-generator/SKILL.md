---
name: automated-soap-note-generator
description: Transform unstructured clinical notes, dictation, or audio transcripts
  into standardized SOAP (Subjective, Objective, Assessment, Plan) medical documentation.
  Trigger when medical text needs structuring, clinical encounters require documentation,
  or healthcare providers need administrative burden reduction.
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

# Automated SOAP Note Generator

## Overview

Converts unstructured clinical input (dictation, rough notes, or transcripts) into professionally formatted SOAP notes compliant with medical documentation standards.

## Function

**Primary Use Cases:**
- Convert physician dictation to structured SOAP format
- Transform consultation rough notes into clinical documentation
- Generate standardized encounter summaries from audio transcripts
- Reduce administrative burden for healthcare providers

**Input Types Supported:**
- Raw clinical dictation text
- Unstructured consultation notes
- Audio-to-text transcripts
- Patient encounter descriptions

## Usage

### Basic Usage

```python
from scripts.main import SOAPNoteGenerator

generator = SOAPNoteGenerator()
soap_note = generator.generate(
    input_text="Patient presents with 2-day history of chest pain...",
    patient_id="P12345"
)
```

### Command Line

```bash
python scripts/main.py --input "Patient reports headache..." --output soap_note.md
```

### With Audio Input

```python
soap_note = generator.generate_from_audio(
    audio_path="consultation.wav",
    patient_id="P12345"
)
```

## Output Format

**SOAP Structure:**

| Section | Content |
|---------|---------|
| **S** - Subjective | Patient-reported symptoms, history, complaints |
| **O** - Objective | Physical exam findings, vital signs, test results |
| **A** - Assessment | Clinical impression, differential diagnosis |
| **P** - Plan | Treatment plan, medications, follow-up instructions |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_text` | str | Yes* | Raw clinical text to parse |
| `audio_path` | str | Yes* | Path to audio file for transcription |
| `patient_id` | str | No | Patient identifier |
| `encounter_date` | str | No | Date of encounter (ISO 8601) |
| `provider` | str | No | Healthcare provider name |

*Either `input_text` or `audio_path` required

## Technical Approach

### Core NLP Pipeline

1. **Medical Entity Recognition**: Identify symptoms, diagnoses, medications, procedures
2. **Section Classification**: Classify sentences into S/O/A/P categories
3. **Temporal Extraction**: Parse timeline information (onset, duration, frequency)
4. **Negation Detection**: Distinguish positive from negative findings
5. **Relation Extraction**: Link findings to body parts, severity, timing

### NLP Techniques

- **Named Entity Recognition (NER)**: Medical terminology extraction
- **Dependency Parsing**: Understanding relationships between medical concepts
- **Text Classification**: Sentence-level S/O/A/P categorization
- **Template Filling**: Structured output generation

### Difficulty Level: HIGH

⚠️ **Technical Complexity**: This skill requires:
- Medical domain NLP expertise
- Understanding of clinical terminology
- Handling ambiguous clinical language
- Compliance with medical documentation standards

**Status**: Requires human review for clinical accuracy.

## References

- Clinical guidelines: `references/clinical_guidelines.md`
- Sample SOAP notes: `references/sample_soap_notes.md`
- Medical terminology list: `references/medical_terminology.md`

## Evidence

> "89% of evaluators indicated that MediNotes implementation could substantially reduce administrative burden on healthcare providers"
> — [Source](https://arxiv.org/pdf/2410.01841)

## Limitations

- Not a substitute for clinical judgment
- Requires healthcare provider review before use in patient records
- Accuracy depends on input quality and clarity
- Medical terminology coverage may vary by specialty

## Dependencies

```
spacy>=3.6.0
scispacy>=0.5.3
medspacy>=1.1.0
```

## License

Clinical use requires compliance with HIPAA and local medical documentation regulations.

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
