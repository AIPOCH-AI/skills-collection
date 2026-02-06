---
name: ib-summarizer
description: Summarize core safety information from Investigator's Brochures for clinical researchers
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
