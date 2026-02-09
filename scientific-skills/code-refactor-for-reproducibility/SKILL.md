---
name: code-refactor-for-reproducibility
description: Refactor messy R/Python scripts into modular, documented, and reproducible
  code for top-tier journals
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

# Skill: Code Refactor for Reproducibility

**ID**: 106

## Purpose
Refactor messy R/Python scripts written by biologists into modular, documented, and reproducible code that meets code open-source requirements of top-tier journals like Nature/Science.

## Overview
Common "one-off script" problems in bioinformatics research: scattered code, lack of documentation, chaotic dependencies, difficult to reproduce. This Skill transforms messy scripts into research code compliant with FAIR principles through a structured refactoring process.

## Usage

```bash
openclaw skills run code-refactor-for-reproducibility \
  --input <original_script_directory> \
  --output <refactored_directory> \
  --language {python|r} \
  --template {nature|science|elife} \
  [--requirements <dependency_list>]
```

## Input Requirements
- Original script files (.py, .R, .ipynb, etc.)
- (Optional) Data file descriptions
- (Optional) Current dependency list

## Output Structure
Refactored codebase includes:
```
output/
├── README.md              # Project overview
├── LICENSE                # Open source license
├── CITATION.cff          # Citation file
├── environment.yml       # Environment configuration (Conda)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Containerization configuration
├── src/                  # Source code
│   ├── __init__.py
│   ├── data_loading.py   # Data loading module
│   ├── analysis.py       # Analysis module
│   ├── visualization.py  # Visualization module
│   └── utils.py          # Utility functions
├── notebooks/            # Jupyter notebooks
├── tests/                # Unit tests
├── data/                 # Data directory
│   ├── raw/              # Raw data (read-only)
│   └── processed/        # Processed data
├── results/              # Output results
└── docs/                 # Documentation
```

## Refactoring Principles

### 1. Modularity
- Single responsibility: Each module does only one thing
- Function granularity: Function length controlled within 50 lines
- Reusability: Avoid hard-coding, use parameter configuration

### 2. Reproducibility
- Fixed random seeds
- Locked dependency versions
- Complete environment records
- Clear data workflow

### 3. Documentation Standards
- Function docstrings (NumPy/Google style)
- README with Quick Start
- CHANGELOG recording modifications
- CODE_OF_CONDUCT.md

### 4. Code Quality
- PEP8 / tidyverse style guides
- Type annotations
- Error handling
- Logging

## Journal Compliance Templates

### Nature Portfolio
- Requirements: Code stored in Zenodo/Figshare
- License: MIT/Apache-2.0
- Documentation: Required README + dependency description

### Science
- Requirements: GitHub repository + permanent archive
- License: OSI-certified license
- Documentation: Required installation instructions

### eLife
- Requirements: Complete executable code
- License: MIT/BSD
- Documentation: Required test instructions

## File Structure

```
skills/code-refactor-for-reproducibility/
├── SKILL.md              # This file
├── scripts/
│   └── main.py          # Main refactoring script
├── templates/           # Journal templates
│   ├── nature/
│   ├── science/
│   └── elife/
└── examples/            # Example code
```

## Dependencies
- Python 3.9+
- ast (code parsing)
- jinja2 (template rendering)
- black/ruff (Python formatting)
- lintr (R formatting)

## Limitations
- Does not modify original logic, only refactors structure
- Complex data analysis workflows require manual confirmation
- Dependency conflicts need manual resolution
- Does not support automatic unit test generation

## References
1. Wilson G, et al. (2017) Good enough practices in scientific computing. PLoS Comp Biol.
2. Piccolo SR & Frampton MB. (2016) Tools and techniques for computational reproducibility. GigaScience.
3. Sandve GK, et al. (2013) Ten simple rules for reproducible computational research. PLoS Comp Biol.

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
