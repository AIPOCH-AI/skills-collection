---
name: eln-template-creator
description: Generate standardized experiment templates for Electronic Laboratory
  Notebooks
version: 1.0.0
category: Data
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

# ELN Template Creator

ID: 139

Generate standardized experiment record templates for Electronic Laboratory Notebooks (ELN).

## Description

This Skill is used to generate standardized experiment record templates that comply with laboratory specifications, supporting multiple experiment types and custom fields.

## Usage

```bash
# Generate molecular biology experiment template
python scripts/main.py --type molecular-biology --output experiment_template.md

# Generate chemistry synthesis experiment template
python scripts/main.py --type chemistry --output chemistry_template.md

# Generate cell culture experiment template
python scripts/main.py --type cell-culture --output cell_culture_template.md

# Generate general experiment template
python scripts/main.py --type general --output general_template.md

# Custom template parameters
python scripts/main.py --type general --title "Protein Purification Experiment" --researcher "Zhang San" --output protein_purification.md
```

## Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| `--type` | string | Yes | Experiment type: general, molecular-biology, chemistry, cell-culture, animal-study |
| `--output` | string | No | Output file path, default output to stdout |
| `--title` | string | No | Experiment title |
| `--researcher` | string | No | Researcher name |
| `--date` | string | No | Experiment date (YYYY-MM-DD) |
| `--project` | string | No | Project name/number |

## Supported Experiment Types

1. **general** - General experiment template
2. **molecular-biology** - Molecular biology experiments (PCR, cloning, electrophoresis, etc.)
3. **chemistry** - Chemical synthesis experiments
4. **cell-culture** - Cell culture experiments
5. **animal-study** - Animal experiments

## Output Format

Generated templates are in Markdown format, containing the following standard sections:

- Basic experiment information
- Experiment purpose
- Experiment materials and reagents
- Experiment equipment
- Experiment procedures
- Results recording
- Data analysis
- Conclusions and discussion
- Attachments and raw data

## Requirements

- Python 3.8+

## Author

OpenClaw

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

No additional Python packages required.

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
