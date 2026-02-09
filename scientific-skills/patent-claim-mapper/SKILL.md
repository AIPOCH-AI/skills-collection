---
name: patent-claim-mapper
description: Analyze patent claim texts to identify potential infringement risks,
  support competitive analysis and Freedom to Operate (FTO) studies for IP professionals.
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Patent Claim Mapper

## Purpose
Analyze patent claim texts to identify potential infringement risk points, support competitive analysis and Freedom to Operate (FTO) studies.

## Description
This tool is used to parse patent claim texts, extract key technical features, and compare them with target product/technology features to generate infringement risk assessment reports. Suitable for patent engineers, IP lawyers, and R&D teams for patent risk screening work.

## Features
1. **Claim Parsing** - Automatically identify independent and dependent claims
2. **Technical Feature Extraction** - Extract key limiting words and technical elements
3. **Infringement Comparison Analysis** - Map and compare claims with product features
4. **Risk Rating** - High/Medium/Low three-level risk rating
5. **Visualized Report** - Generate structured risk analysis reports

## Installation
No additional installation required, Python standard library is sufficient.

## Configuration
Create `config.json` in the run directory:
```json
{
  "risk_threshold": 0.7,
  "output_format": "markdown",
  "language": "zh",
  "detailed_analysis": true
}
```

## Usage

### Command Line
```bash
# Analyze single patent file
python scripts/main.py analyze --patent claims.txt --product product_spec.txt

# Batch analysis
python scripts/main.py analyze --patent-dir ./patents/ --product product_spec.txt

# Only parse claim structure
python scripts/main.py parse --patent claims.txt
```

### Python API
```python
from scripts.main import PatentClaimMapper

mapper = PatentClaimMapper()

# Load claims
claims = mapper.load_claims("patent_claims.txt")

# Analyze infringement risk
result = mapper.analyze_infringement(
    claims=claims,
    product_features=["feature1", "feature2"]
)

# Generate report
report = mapper.generate_report(result)
```

## Input Format

### Patent Claim Format
```
1. A [device/method], comprising:
   [technical feature A];
   [technical feature B]; and
   [technical feature C].

2. The [device/method] of claim 1, wherein [additional feature D].
```

### Product Feature Description Format
```
- Feature 1: [description]
- Feature 2: [description]
Or free text description
```

## Output Format

### Risk Assessment Report Structure
```markdown
# Patent Infringement Risk Analysis Report

## Basic Information
- Analysis Date: 2024-XX-XX
- Patent Identifier: [Patent No./Name]
- Target Product: [Product Name]

## Risk Overview
| Claim | Risk Level | Match Rate |
|---------|---------|-------|
| Claim 1 | 🔴 High Risk | 85% |
| Claim 2 | 🟡 Medium Risk | 60% |

## Detailed Analysis
### Claim 1
- Technical feature mapping table
- Infringement analysis explanation
- Design-around suggestions
```

## Risk Levels
- 🔴 **High Risk**: Match rate ≥ 70%, substantial infringement possibility exists
- 🟡 **Medium Risk**: Match rate 40-69%, further evaluation needed
- 🟢 **Low Risk**: Match rate < 40%, infringement possibility is low

## Limitations
1. Based on text similarity analysis, does not constitute legal advice
2. Cannot replace professional patent attorney's infringement determination
3. Requires manual verification of technical feature equivalence judgment
4. Only supports Chinese and English claim texts

## Dependencies
- Python 3.8+
- No third-party dependencies (uses standard library)

## License
MIT

## Author
OpenClaw Skills Team

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
