---
name: recommendation-letter-assistant
description: Helps faculty and mentors draft standardized recommendation letters for
  medical students, residents, and fellows. Ensures comprehensive coverage of applicant
  strengths.
version: 1.0.0
category: General
tags:
- recommendation-letter
- lor
- faculty
- mentorship
- career
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Recommendation Letter Assistant

Assists mentors and faculty in writing effective recommendation letters.

## Features

- Structured letter templates
- Competency-based content suggestions
- Strength/weakness framing
- Specialty-specific customization
- MSPE/Dean's Letter alignment

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `applicant_name` | str | Yes | Name of applicant |
| `relationship` | str | Yes | "mentor", "course_director", "research_PI" |
| `duration` | str | Yes | Length of relationship |
| `key_strengths` | list | Yes | Applicant's top qualities |
| `context` | str | No | Residency, fellowship, job, etc. |

## Output Format

```json
{
  "letter_draft": "string",
  "opening": "string",
  "body_paragraphs": ["string"],
  "closing": "string",
  "competencies_addressed": ["string"]
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
