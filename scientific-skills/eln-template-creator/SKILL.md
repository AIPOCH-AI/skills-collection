---
name: eln-template-creator
description: Generate standardized experiment templates for Electronic Laboratory Notebooks
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
