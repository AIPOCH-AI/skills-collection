---
name: cover-letter-drafter
description: Generates professional cover letters for journal submissions and job
  applications in medical and academic contexts.
version: 1.0.0
category: Career
tags:
- cover-letter
- job-application
- journal-submission
- academic-writing
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Cover Letter Drafter

Creates tailored cover letters for academic and medical positions.

## Features

- Journal submission cover letters
- Job application cover letters
- Fellowship application letters
- Customizable templates

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `purpose` | str | Yes | "journal", "job", "fellowship" |
| `recipient` | str | Yes | Target journal or institution |
| `key_points` | list | Yes | Main points to highlight |

## Output Format

```json
{
  "cover_letter": "string",
  "subject_line": "string",
  "word_count": "int"
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
