---
name: anatomy-quiz-master
description: Interactive anatomy quiz generator covering gross anatomy, neuroanatomy,
  and clinical anatomy. Supports multiple quiz modes and difficulty levels for medical
  education.
version: 1.0.0
category: Education
tags:
- anatomy
- medical-education
- quiz
- gross-anatomy
- neuroanatomy
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Anatomy Quiz Master

Interactive anatomy quiz generator for medical students.

## Features

- Regional anatomy quizzes (upper limb, lower limb, thorax, abdomen, head/neck)
- Neuroanatomy pathway tracing
- Clinical correlation questions
- Image-based identification
- Difficulty levels: basic, intermediate, advanced

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region` | str | Yes | Body region to quiz on |
| `difficulty` | str | No | "basic", "intermediate", "advanced" |
| `question_type` | str | No | "identification", "function", "clinical" |

## Output Format

```json
{
  "question": "string",
  "options": ["string"],
  "correct_answer": "string",
  "explanation": "string",
  "clinical_note": "string"
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
