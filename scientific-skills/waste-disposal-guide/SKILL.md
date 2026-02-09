---
name: waste-disposal-guide
description: Guide for proper chemical waste disposal by waste container color
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

# Waste Disposal Guide

Guide for disposing specific chemical wastes into the correct colored waste containers.

## Usage

```bash
python scripts/main.py --chemical "chloroform"
python scripts/main.py --list-categories
```

## Waste Categories

| Container | Color | Accepts |
|-----------|-------|---------|
| Halogenated | Orange | Chloroform, DCM, halogenated solvents |
| Non-halogenated | Red | Ethanol, acetone, organic solvents |
| Aqueous | Blue | Water-based solutions, buffers |
| Acid | Yellow | Acids (dilute/concentrated) |
| Base | White | Bases, alkali solutions |
| Heavy Metal | Gray | Mercury, lead, cadmium waste |
| Solid | Black | Gloves, paper, solid debris |

## Parameters

- `--chemical`: Chemical name to look up
- `--list-categories`: List all waste categories
- `--safety`: Show safety notes

## Output

- Disposal instructions
- Container color
- Safety precautions

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
