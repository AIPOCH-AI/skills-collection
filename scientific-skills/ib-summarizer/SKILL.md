---
name: ib-summarizer
description: Summarize core safety information from Investigator's Brochures for clinical
  researchers
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

# IB Summarizer

## Description

Summarize core safety information from Investigator's Brochures (IB), helping clinical researchers quickly obtain key drug safety data.

## Functions

- Extract Core Safety Information (CSI) from IB documents
- Identify and summarize:
  - Known Adverse Drug Reactions (ADRs) and their incidence rates
  - Contraindications
  - Warnings and Precautions
  - Drug Interactions
  - Special population precautions
  - Overdose Management
  - Important safety updates

## Usage

```bash
python scripts/main.py <input_file> [options]
```

### Parameters

| Parameter | Description | Required |
|------|------|------|
| `input_file` | IB document path (PDF/Word/TXT) | Yes |
| `-o, --output` | Output file path (default: stdout) | No |
| `-f, --format` | Output format: json/markdown/text (default: markdown) | No |
| `-l, --language` | Output language: zh/en (default: zh) | No |

### Examples

```bash
# Basic usage
python scripts/main.py /path/to/IB.pdf

# Output to JSON file
python scripts/main.py /path/to/IB.pdf -o summary.json -f json

# English output
python scripts/main.py /path/to/IB.docx -l en -o summary.md
```

## Output Structure

### Markdown Format

```markdown
# IB Safety Information Summary

## Basic Drug Information
- **Drug Name**: XXX
- **Version**: X.X
- **Date**: YYYY-MM-DD

## Core Safety Information

### Known Adverse Reactions
| System Organ Class | Adverse Reaction | Incidence | Severity |
|-------------|---------|--------|---------|
| ... | ... | ... | ... |

### Contraindications
- ...

### Warnings and Precautions
- ...

### Drug Interactions
- ...

### Special Populations
| Population | Precautions |
|-----|---------|
| Pregnant women | ... |
| Lactating women | ... |
| Children | ... |
| Elderly | ... |
| Hepatic/renal impairment | ... |

### Overdose
- Symptoms: ...
- Management: ...

### Safety Update History
| Version | Date | Update Content |
|-----|------|---------|
| ... | ... | ... |
```

### JSON Format

```json
{
  "drug_info": {
    "name": "Drug Name",
    "version": "Version Number",
    "date": "Date"
  },
  "core_safety_info": {
    "adverse_reactions": [...],
    "contraindications": [...],
    "warnings": [...],
    "drug_interactions": [...],
    "special_populations": {...},
    "overdose": {...},
    "safety_updates": [...]
  }
}
```

## Dependencies

- Python 3.8+
- PyPDF2 / pdfplumber (PDF parsing)
- python-docx (Word parsing)
- Optional: openai / anthropic (for AI-enhanced extraction)

## Installation

```bash
pip install -r requirements.txt
```

## Notes

1. Input documents should be readable PDF or Word format
2. Scanned PDFs require OCR processing first
3. For complex table structures, manual verification may be needed
4. Information extracted by this tool is for reference only and does not constitute medical advice

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
