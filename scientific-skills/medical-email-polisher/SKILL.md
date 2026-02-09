---
name: medical-email-polisher
description: Polishes draft emails into professional, context-appropriate medical
  correspondence. Supports various scenarios including communication with mentors,
  editors, colleagues, and patients.
version: 1.0.0
category: General
tags:
- email
- communication
- professionalism
- medical-writing
- etiquette
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Medical Email Polisher

Transforms rough email drafts into polished, professional medical correspondence.

## Features

- Multiple context templates (mentor, editor, peer, patient)
- Tone adjustment (formal to semi-formal)
- Opening and closing optimization
- Grammar and clarity improvements
- HIPAA-aware patient communication

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `draft_text` | str | Yes | Rough email draft |
| `recipient_type` | str | Yes | "mentor", "editor", "colleague", "patient" |
| `purpose` | str | No | Email purpose/context |

## Output Format

```json
{
  "polished_email": "string",
  "subject_line": "string",
  "changes_made": ["string"],
  "tone_assessment": "string"
}
```

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
