---
name: medical-scribe-dictation
description: Convert physician verbal dictation into structured SOAP notes. Trigger
  when receiving audio/transcribed medical dictation, clinical encounter recordings,
  or unstructured clinical narratives requiring structured documentation. Supports
  real-time and batch processing of medical speech-to-text.
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

# Medical Scribe Dictation

Convert unstructured physician dictation into professionally formatted SOAP (Subjective, Objective, Assessment, Plan) notes with medical terminology normalization and clinical quality assurance.

## Features

- **Speech-to-Text Processing**: Transcribe audio or process pre-transcribed text
- **SOAP Structure Generation**: Auto-organize clinical content into standard sections
- **Medical Terminology Handling**: Normalize abbreviations, expand acronyms, verify drug names
- **Clinical Quality Checks**: Flag missing required elements, suggest clarifications
- **Multi-Specialty Support**: Adaptable templates for internal medicine, surgery, pediatrics, etc.

## Usage

### Processing Pre-Transcribed Text

```bash
python scripts/main.py --input "patient presents with..." --output-format soap
```

### Processing Audio File (requires whisper/faster-whisper)

```bash
python scripts/main.py --audio consultation.wav --output note.md
```

### Python API

```python
from scripts.main import MedicalScribe

scribe = MedicalScribe(specialty="internal_medicine")
soap_note = scribe.process_dictation(transcription_text)
print(soap_note.to_markdown())
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input` | string | - | Raw transcribed text or path to text file |
| `audio` | string | - | Path to audio file (wav/mp3/m4a) |
| `specialty` | string | "general" | Medical specialty for context hints |
| `output-format` | string | "soap" | Output format: soap, ehr, narrative |
| `language` | string | "auto" | Language code (en/zh/es/...) |
| `confidence-threshold` | float | 0.85 | Minimum confidence for auto-acceptance |

## SOAP Output Structure

```markdown
# Clinical Note - [Date]

## Subjective
Chief Complaint:
History of Present Illness:
Review of Systems:
Past Medical History:
Medications:
Allergies:
Social History:
Family History:

## Objective
Vital Signs:
Physical Examination:
Diagnostic Studies:

## Assessment
Primary Diagnosis:
Differential Diagnoses:
Clinical Reasoning:

## Plan
Diagnostic:
Therapeutic:
Patient Education:
Follow-up:
```

## Technical Architecture

### Components

1. **Transcription Module** (optional): Whisper-based STT with medical vocabulary fine-tuning
2. **Segmentation Engine**: NLP-based section identification and content classification
3. **Terminology Processor**: Medical NER (Named Entity Recognition) and normalization
4. **SOAP Assembler**: Structured output generation with specialty-specific formatting
5. **Quality Validator**: Completeness checks and clinical red-flag detection

### Dependencies

- `openai` or `anthropic` - LLM for structure extraction
- `spacy` + `scispacy` - Medical NLP processing
- `faster-whisper` (optional) - Local STT
- `pydantic` - Data validation

## Technical Difficulty

**High** - Requires medical domain expertise, complex NLP pipelines, and clinical validation.

## Known Limitations

- Medical terminology accuracy depends on speech clarity
- Ambiguous dictation may require human clarification
- Drug name verification recommended before finalizing
- Does not replace physician review for critical cases

## References

See `references/` for:
- `soap-templates.md` - Specialty-specific SOAP templates
- `medical-abbreviations.json` - Common abbreviation mappings
- `terminology-sources.md` - Medical ontology references (SNOMED CT, ICD-10)
- `example-cases.md` - Sample dictations with expected outputs

## Safety Notes

⚠️ **Clinical Validation Required**: All generated notes must be reviewed by the attending physician before entering the medical record.

⚠️ **No Diagnostic Authority**: This tool structures clinical information but does not provide diagnostic suggestions.

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
