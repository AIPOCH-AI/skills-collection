---
name: translational-gap-analyzer
description: Assess translational gaps between preclinical models and human diseases
  to predict clinical failure risks
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

# Translational Gap Analyzer

**ID**: 209

## Description

Assesses the "translational gap" between basic research models (such as mice, zebrafish, cell lines) and human diseases, providing early warning of clinical translation failure risks. This system helps researchers identify potential translational barriers in preclinical research and improve clinical trial success rates through multi-dimensional analysis.

## Capabilities

- Evaluates anatomical/physiological differences between models and humans
- Analyzes pathological similarity of disease models
- Identifies interspecies differences in molecular pathways
- Evaluates pharmacokinetic differences
- Provides early warning of clinical trial failure risk factors
- Provides improvement recommendations to increase translation success rates

## Usage

```bash
# Full assessment report
python scripts/main.py --model <model_type> --disease <disease_name> --full

# Quick risk assessment
python scripts/main.py --model <model_type> --disease <disease_name> --quick

# Compare multiple models
python scripts/main.py --models mouse,rat,primate --disease <disease_name> --compare

# Specify focus areas
python scripts/main.py --model mouse --disease "Alzheimer's" --focus metabolism,immune
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--model` | Model type (mouse, rat, zebrafish, cell_line, organoid, primate) | Yes (unless --models) |
| `--models` | Multi-model comparison mode, comma-separated | No |
| `--disease` | Disease name or MeSH ID | Yes |
| `--focus` | Focus areas, comma-separated (anatomy, physiology, metabolism, immune, genetics, behavior) | No |
| `--full` | Generate full assessment report | No |
| `--quick` | Quick risk assessment mode | No |
| `--compare` | Multi-model comparison mode | No |
| `--output` | Output file path | No |
| `--format` | Output format (json, markdown, table) | No |

## Example Output

```json
{
  "model": "mouse",
  "disease": "Alzheimer's Disease",
  "overall_gap_score": 6.8,
  "risk_level": "HIGH",
  "dimensions": {
    "genetics": {"score": 8.5, "concerns": ["APOE4 differences", "Different tau pathology patterns"]},
    "physiology": {"score": 7.0, "concerns": ["Brain structure differences", "Lifespan differences"]},
    "metabolism": {"score": 6.5, "concerns": ["Significant drug metabolism differences"]},
    "immune": {"score": 5.5, "concerns": ["Microglia functional differences", "Different neuroinflammation patterns"]},
    "behavior": {"score": 6.0, "concerns": ["Limitations in cognitive assessment methods"]}
  },
  "clinical_failure_predictors": [
    "Immune-related mechanism research may not translate",
    "Drug clearance rate differences may lead to inappropriate dosing"
  ],
  "recommendations": [
    "Consider using humanized mouse models",
    "Add non-human primate validation experiments",
    "Focus on peripheral immune and central immune interactions"
  ]
}
```

## Model Types

### Common Models

| Model | Applicable Scenarios | Typical Gaps |
|------|----------|----------|
| mouse | Genetic manipulation, basic research | Immune, metabolism, brain structure |
| rat | Behavioral studies, cardiovascular | Cognition, drug metabolism |
| zebrafish | Development, high-throughput screening | Anatomy, physiology |
| cell_line | Molecular mechanisms | Microenvironment, systemic |
| organoid | Human-specific research | Maturity, vascularization |
| primate | Preclinical validation | Cost, ethics |

## Gap Scoring System

- **0-3**: Low gap, good translation prospects
- **4-6**: Moderate gap, requires additional validation
- **7-8**: High gap, significant translation risks exist
- **9-10**: Extremely high gap, low translation likelihood

## Dependencies

- Python 3.8+
- Built-in libraries: argparse, json, sys

## Files

- `SKILL.md` - This file
- `scripts/main.py` - Main analysis script

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
