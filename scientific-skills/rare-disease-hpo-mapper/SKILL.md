---
name: rare-disease-hpo-mapper
description: Map patient symptoms to Human Phenotype Ontology terms for gene diagnosis
version: 1.0.0
category: Clinical
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

# Rare Disease HPO Mapper

Clinical phenotype standardization tool.

## Use Cases
- Exome/genome analysis
- Rare disease diagnosis
- Genetic counseling
- Research cohort building

## Parameters
- `symptoms`: Clinical description
- `age_onset`: Pediatric/adult
- `inheritance_pattern`: AD/AR/XL

## Returns
- HPO term suggestions
- Confidence scores
- Differential diagnosis genes
- Literature links

## Example
"Wide-set eyes" → HP:0000316 (Hypertelorism)

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
