---
name: networking-email-drafter
description: Draft professional follow-up emails to contacts made at conferences
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

# Networking Email Drafter

Draft professional follow-up emails to contacts made at conferences - not too pushy, but memorable.

## Usage

```bash
python scripts/main.py --contact "Dr. Smith" --topic "CRISPR research" --conference "ASGCT 2024"
```

## Parameters

- `--contact`: Contact name
- `--topic`: Discussion topic
- `--conference`: Conference name
- `--your-name`: Your name
- `--tone`: Email tone (formal/casual/warm)

## Email Components

- Professional greeting
- Context reminder
- Value proposition
- Soft ask
- Gracious closing

## Output

- Draft email
- Subject line suggestions
- Follow-up timeline

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
