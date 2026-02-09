---
name: q-and-a-prep-partner
description: Predict challenging questions for presentations and prepare responses
version: 1.0.0
category: Present
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

# Q&A Prep Partner

Predict challenging questions for presentations and prepare structured responses.

## Usage

```bash
python scripts/main.py --abstract abstract.txt --field oncology
python scripts/main.py --topic "CRISPR therapy" --audience experts
```

## Parameters

- `--abstract`: Abstract text or file
- `--topic`: Research topic
- `--field`: Research field
- `--audience`: Audience type (general/experts/peers)
- `--n-questions`: Number of questions to generate (default: 10)

## Question Types

1. Methodology questions
2. Statistical questions
3. Interpretation questions
4. Limitation questions
5. Future work questions
6. Comparison questions

## Output

- Predicted questions
- Suggested response frameworks
- Key points to address

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
