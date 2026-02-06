---
name: systematic-review-screener
description: 'Automates abstract screening for systematic reviews and meta-analyses.
  Triggers when user needs to: screen multiple academic abstracts against  inclusion/exclusion
  criteria, export PRISMA-compliant screening results, or generate screening reports
  with decision rationale. Supports batch  processing of PubMed/EndNote/CSV formatted
  references with confidence  scoring and conflict detection.'
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Systematic Review Screener

Automated abstract screening tool for systematic literature reviews with PRISMA workflow support.

## Overview

This skill screens academic abstracts against predefined inclusion/exclusion criteria, generating PRISMA-compliant outputs with decision rationale and confidence scores.

**Technical Difficulty: High** ⚠️ Manual verification recommended for final inclusion decisions.

## Features

- **Multi-format Input**: PubMed MEDLINE, EndNote XML, CSV/TSV
- **Criteria Matching**: Configurable inclusion/exclusion rules
- **Confidence Scoring**: 0-100% confidence for each decision
- **Conflict Detection**: Flags abstracts requiring human review
- **PRISMA Export**: Flow diagram data and screening log
- **Batch Processing**: Handles large reference sets efficiently

## Usage

### Basic Screening

```python
# Run with default settings
python scripts/main.py --input references.csv --criteria criteria.yaml
```

### With PRISMA Export

```python
python scripts/main.py --input references.xml --criteria criteria.yaml \
  --output results/ --prisma --format excel
```

### Confidence Threshold

```python
python scripts/main.py --input refs.txt --criteria criteria.yaml \
  --threshold 0.8 --conflict-only
```

## Input Formats

### 1. CSV/TSV
Required columns: `title`, `abstract` (optional: `authors`, `year`, `doi`, `pmid`)

```csv
title,abstract,authors,year
title,abstract,authors,year
```

### 2. PubMed MEDLINE
Standard .txt export from PubMed search.

### 3. EndNote XML
Export from EndNote with abstracts included.

## Criteria File (YAML)

See `references/criteria_template.yaml` for complete example:

```yaml
study_type:
  include:
    - "randomized controlled trial"
    - "systematic review"
  exclude:
    - "case report"
    - "letter"
    - "editorial"

population:
  include_keywords:
    - "adults"
    - "elderly"
  exclude_keywords:
    - "pediatric"
    - "children"

intervention:
  required:
    - "drug therapy"
    - "medication"

language:
  allowed: ["English"]
  
year_range:
  min: 2010
  max: 2024

confidence_threshold: 0.75
```

## Output Files

| File | Description |
|------|-------------|
| `screened_included.csv` | Records passing all criteria |
| `screened_excluded.csv` | Records failing one or more criteria |
| `conflicts.csv` | Low-confidence decisions requiring review |
| `prisma_data.json` | PRISMA flow diagram counts |
| `screening_log.json` | Full decision trail with rationale |

## PRISMA Workflow Support

Generates structured data for PRISMA 2020 flow diagram:

```json
{
  "identification": {
    "database_results": 1250,
    "register_results": 45,
    "other_sources": 12
  },
  "screening": {
    "records_screened": 1307,
    "records_excluded": 1150,
    "full_text_assessed": 157,
    "full_text_excluded": 89
  },
  "included": {
    "qualitative_synthesis": 68,
    "quantitative_synthesis": 42
  }
}
```

## Configuration

### Environment Variables
```bash
export SCREENING_THRESHOLD=0.75  # Default confidence threshold
export BATCH_SIZE=100             # Records per batch
export MAX_WORKERS=4              # Parallel processing workers
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input file path | Required |
| `--criteria` | Criteria YAML path | Required |
| `--output` | Output directory | `./output` |
| `--format` | Output format: csv/excel/json | csv |
| `--threshold` | Confidence threshold | 0.75 |
| `--prisma` | Generate PRISMA data | False |
| `--conflict-only` | Export only conflicts | False |
| `--batch-size` | Processing batch size | 100 |

## Decision Algorithm

1. **Keyword Matching**: Exact and fuzzy keyword matching against title/abstract
2. **Inclusion Scoring**: Points for each inclusion criterion matched
3. **Exclusion Check**: Immediate exclusion if exclusion criterion detected
4. **Confidence Calculation**: Weighted score based on keyword presence and clarity
5. **Conflict Flagging**: Records with confidence < threshold flagged for manual review

## Limitations

- **Not for Final Decisions**: Tool provides recommendations; human review required for inclusion
- **Language Dependent**: Optimized for English abstracts
- **Structured Abstracts**: Performs better on structured abstracts (Background/Methods/Results/Conclusion)
- **Domain Specific**: Criteria must be tailored to research question

## References

- `references/criteria_template.yaml` - Complete criteria configuration example
- `references/prisma_2020_checklist.pdf` - PRISMA 2020 reporting guidelines
- `references/sample_references.csv` - Example input format

## Version

Version: 1.0.0  
Last Updated: 2026-02-05  
Classification: Research Tool - Requires Human Verification

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
