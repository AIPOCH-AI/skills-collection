---
name: ehr-semantic-compressor
description: AI-powered EHR summarization using Transformer architecture to extract
  key clinical information from lengthy medical records
version: 1.0.0
category: Clinical
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# EHR Semantic Compressor

## Overview

AI-powered EHR summarization using Transformer architecture to extract key clinical information from lengthy medical records. This skill processes lengthy Electronic Health Record (EHR) documents and generates structured, clinically accurate summaries.

**Technical Difficulty**: High

## When to Use

- Input contains lengthy EHR documents (1600+ words) requiring summarization
- Clinical records need structured extraction of key information
- Quick review of patient history, medications, allergies, or diagnoses is needed
- Medical documentation requires compression while maintaining accuracy

## Core Features

1. **Fast Processing**: Process lengthy EHR documents (1600+ words) in 10-20 seconds
2. **Structured Summaries**: Generate bullet-point summaries (200-300 words)
3. **Critical Information Extraction**:
   - Patient allergies and adverse reactions
   - Family medical history
   - Current and past medications
   - Diagnoses and conditions
   - Vital signs and lab results
   - Procedures and surgeries
4. **Clinical Accuracy**: Maintains completeness of medical information

## Usage

### Basic Usage

```bash
python scripts/main.py --input ehr_document.txt --output summary.json
```

### Input Format

```json
{
  "ehr_text": "Full EHR document text...",
  "max_length": 300,
  "extract_sections": ["allergies", "medications", "diagnoses", "family_history"]
}
```

### Output Format

```json
{
  "status": "success",
  "data": {
    "summary": "Structured bullet-point summary...",
    "extracted_sections": {
      "allergies": [...],
      "medications": [...],
      "diagnoses": [...],
      "family_history": [...]
    },
    "metadata": {
      "original_length": 2500,
      "summary_length": 280,
      "compression_ratio": 0.89
    }
  }
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ehr_text | string | Yes | Full EHR document text |
| max_length | number | No | Maximum summary length in words (default: 300) |
| extract_sections | array | No | Sections to extract (default: all) |

## Technical Details

### Architecture

- **Base Model**: Transformer-based encoder-decoder architecture
- **Medical Domain Adaptation**: Fine-tuned on clinical text corpora
- **Section Extraction**: Rule-based + ML hybrid approach for structured data
- **Processing Pipeline**: Text segmentation -> Summarization -> Section extraction -> Output formatting

### Dependencies

See `references/requirements.txt` for complete list.

Key dependencies:
- transformers >= 4.30.0
- torch >= 2.0.0
- spacy >= 3.6.0
- scispacy >= 0.5.3

### Performance

- **Processing Time**: 10-20 seconds for 1600+ word documents
- **Memory**: Requires ~2GB RAM
- **Output Length**: 200-300 words (configurable)
- **Compression Ratio**: ~85-90%

## References

- `references/requirements.txt` - Python dependencies
- `references/guidelines.md` - Clinical summarization guidelines
- `references/sample_input.json` - Example input format
- `references/sample_output.json` - Example output format

## Safety & Compliance

- No external API calls or service dependencies
- All processing performed locally
- No patient data transmitted outside the system
- Error messages are semantic and do not expose technical details

## Testing

Run unit tests:
```bash
cd scripts
python test_main.py
```

## Error Handling

All errors return semantic messages:

```json
{
  "status": "error",
  "error": {
    "type": "input_validation_error",
    "message": "EHR text is empty or too short",
    "suggestion": "Provide EHR text with at least 100 words"
  }
}
```

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
