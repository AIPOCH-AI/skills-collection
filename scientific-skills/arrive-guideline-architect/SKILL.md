---
name: arrive-guideline-architect
description: Design impeccable animal experiment protocols based on ARRIVE 2.0 guidelines.
  Ensures compliance with international animal research reporting standards for transparency,
  reproducibility, and scientific rigor.
version: 1.0.0
category: Wet Lab
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

# ARRIVE Guideline Architect

## Function Description

Based on the ARRIVE 2.0 (Animal Research: Reporting of In Vivo Experiments) international standard, provides impeccable protocol architecture for animal experiment design. Ensures experimental design complies with international animal research reporting standards, improving research transparency, reproducibility, and scientific rigor.

## ARRIVE 2.0 Core Framework

### Essential 10 (Required Ten Items)
1. **Study Design** - Research design: Clear experimental design and number of animals per group
2. **Sample Size** - Sample size: Explanation of sample size calculation basis
3. **Inclusion/Exclusion Criteria** - Inclusion/Exclusion criteria
4. **Randomisation** - Randomization: Methods for allocation and assessment randomization
5. **Blinding** - Blinding: Who, when, and how blinding was implemented
6. **Outcome Measures** - Outcome measures: Primary and secondary endpoints
7. **Statistical Methods** - Statistical methods: Descriptive and inferential statistics
8. **Experimental Animals** - Experimental animals: Species, strain, source, housing conditions
9. **Experimental Procedures** - Experimental procedures: Detailed operation process
10. **Results** - Results: Complete reporting of data for each group

### Recommended Set (Recommended Items)
- Animal welfare ethics approval
- Housing and husbandry conditions
- Animal care and monitoring
- Endpoint setting
- Data sharing statement
- Conflict of interest statement
- Funding statement

## Usage

### Interactive Experiment Design
```bash
python scripts/main.py --interactive
```

### Generate Protocol from Input File
```bash
python scripts/main.py --input study_brief.json --output protocol.md
```

### Validate Existing Protocol
```bash
python scripts/main.py --validate existing_protocol.md
```

### Generate Checklist
```bash
python scripts/main.py --checklist --format pdf
```

## Input Format (study_brief.json)

```json
{
  "title": "Efficacy Study of Drug X on Diabetic Mouse Model",
  "species": "Mus musculus",
  "strain": "db/db",
  "age": "8-10 weeks",
  "sex": "Male",
  "sample_size_per_group": 15,
  "groups": [
    {"name": "Control Group", "treatment": "Saline"},
    {"name": "Low Dose Group", "treatment": "Drug X 10mg/kg"},
    {"name": "High Dose Group", "treatment": "Drug X 50mg/kg"}
  ],
  "primary_endpoint": "Fasting blood glucose level",
  "secondary_endpoints": ["HbA1c", "Weight change", "Insulin sensitivity"],
  "study_duration_days": 28
}
```

## Output Content

- Complete experimental protocol document (Markdown/PDF)
- ARRIVE 2.0 compliance checklist
- Sample size calculation recommendations
- Randomization protocol template
- Statistical analysis method recommendations
- Ethics application auxiliary materials

## Dependencies

- Python 3.8+
- No external dependencies (pure Python implementation)

## References

- ARRIVE 2.0 Guidelines: https://arriveguidelines.org/
- PLOS Biology Publication: doi:10.1371/journal.pbio.3000411

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
