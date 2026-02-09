---
name: patient-consent-simplifier
description: Rewrite legal-jargon consent forms to 5th-grade reading level
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

# Patient Consent Simplifier

Rewrite legally-dense informed consent forms to 5th-grade reading level for patient comprehension.

## Usage

```bash
python scripts/main.py --input consent_form.pdf --output simple_consent.txt
python scripts/main.py --text "You hereby authorize..." --simplify
```

## Parameters

- `--input`: Input consent form (PDF/TXT/DOCX)
- `--text`: Direct text input
- `--output`: Output file
- `--target-grade`: Target reading grade (default: 5)

## Features

- Simplifies medical/legal terminology
- Shortens complex sentences
- Adds explanatory notes
- Maintains legal accuracy

## Output

- Simplified consent form
- Readability score before/after
- List of key terms explained

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
