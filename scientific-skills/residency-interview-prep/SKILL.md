---
name: residency-interview-prep
description: Mock interview preparation tool for residency Match interviews. Generates
  common behavioral and clinical scenario questions with structured response frameworks
  and feedback.
version: 1.0.0
category: Education
tags:
- residency
- interview-prep
- medical-education
- match
- career
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Residency Interview Prep

Residency interview preparation assistant for the NRMP Match process.

## Features

- Behavioral question generation (STAR format)
- Clinical scenario questions
- Program-specific research questions
- Response structure feedback
- Common question bank (100+ questions)

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question_type` | str | Yes | Type: "behavioral", "clinical", "program", "ethical" |
| `specialty` | str | No | Target specialty (e.g., "internal_medicine", "surgery") |
| `experience` | str | No | User's experience context |

## Output Format

```json
{
  "question": "string",
  "category": "string",
  "suggested_structure": "string",
  "key_points": ["string"],
  "common_pitfalls": ["string"]
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
