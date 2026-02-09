---
name: authorship-credit-gen
description: Generate standardized author contribution statements following the CRediT
  taxonomy
version: 1.0.0
category: Writing
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

# Authorship CRediT Gen

ID: 160
Version: 1.0.0
Description: Generate standardized author contribution statements based on CRediT taxonomy

## CRediT 14 Role Standards

| Role Code | English Name | Chinese Name | Description |
|---------|---------|---------|------|
| C1 | Conceptualization | Conceptualization | Ideas, formulation of research goals |
| C2 | Data curation | Data Curation | Management, annotation, cleaning, maintenance of data |
| C3 | Formal analysis | Formal Analysis | Application of statistical, mathematical, or computational techniques |
| C4 | Funding acquisition | Funding Acquisition | Acquisition of research funding support |
| C5 | Investigation | Investigation | Execution of experiments, data collection |
| C6 | Methodology | Methodology | Development or design of methods/procedures |
| C7 | Project administration | Project Administration | Coordination of project plan execution |
| C8 | Resources | Resources | Provision of research materials, reagents, samples, etc. |
| C9 | Software | Software | Programming, software development |
| C10 | Supervision | Supervision | Guidance of research activities, mentoring responsibilities |
| C11 | Validation | Validation | Verification of results, replication experiments |
| C12 | Visualization | Visualization | Preparation of charts, data presentation |
| C13 | Writing – original draft | Writing - Original Draft | Writing the initial draft |
| C14 | Writing – review & editing | Writing - Review & Editing | Critical review and revision |

## Usage Methods

### Method 1: Interactive Mode
```bash
python scripts/main.py --interactive
```

### Method 2: JSON Input
```bash
python scripts/main.py --input authors.json --format json
```

### Method 3: Command Line Parameters
```bash
python scripts/main.py --authors "Zhang San:C1,C5,C13|Li Si:C2,C6,C9,C14"
```

## Input Format

### JSON Format
```json
{
  "authors": [
    {
      "name": "Zhang San",
      "roles": ["C1", "C5", "C13"],
      "affiliation": "Peking University"
    },
    {
      "name": "Li Si",
      "roles": ["C2", "C6", "C9", "C14"],
      "affiliation": "Tsinghua University"
    }
  ],
  "equal_contribution": ["Zhang San", "Li Si"],
  "corresponding": ["Zhang San"],
  "language": "zh"
}
```

### Shorthand Format
```
Name1:Role1,Role2,...|Name2:Role3,Role4,...
```

## Output Format

### Text Format
```
Author Contribution Statement

Zhang San (Peking University): Conceptualization, Investigation, Writing - Original Draft
Li Si (Tsinghua University): Data Curation, Methodology, Software, Writing - Review & Editing

*Zhang Yi and Zhang San contributed equally to this work

Corresponding Author: Zhang San
```

### CRediT XML Format
XML contribution statement format compliant with journal submission standards

### JSON Format
Structured data for subsequent processing

## Examples

```bash
# Generate a simple contribution statement
python scripts/main.py --authors "Prof. Wang:C1,C4,C10|Dr. Li:C2,C5,C9,C13|Student Zhang:C5,C6,C12"

# Generate bilingual statement with institutional information
python scripts/main.py --input team.json --output contribution.txt --bilingual

# Generate journal XML format
python scripts/main.py --input team.json --format xml --output credit.xml
```

## Parameter Description

| Parameter | Description | Default Value |
|-----|------|-------|
| `--authors` | Author roles shorthand | - |
| `--input` | Input JSON file | - |
| `--output` | Output file path | stdout |
| `--format` | Output format: text/json/xml | text |
| `--language` | Language: zh/en/bilingual | zh |
| `--interactive` | Interactive mode | False |
| `--corresponding` | Corresponding author list | - |
| `--equal` | Co-first authors | - |

## Notes

1. Uses standard CRediT taxonomy with 14 roles
2. Supports Chinese and English output
3. Supports co-first author marking
4. Supports corresponding author annotation
5. Output format complies with most journal requirements

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
