---
name: tone-adjuster
description: Converts medical text between academic rigor and patient-friendly tones.
  Supports bidirectional transformation maintaining accuracy while adjusting accessibility.
version: 1.0.0
category: General
tags:
- tone
- readability
- patient-education
- academic-writing
- translation
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Tone Adjuster

Bidirectional tone converter for medical text - academic to patient-friendly and vice versa.

## Features

- Academic ↔️ Layperson tone conversion
- Medical jargon translation
- Readability scoring
- Preserves medical accuracy
- Multiple adjustment levels

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | str | Yes | Input medical text |
| `target_tone` | str | Yes | "academic", "patient_friendly", "professional" |
| `level` | str | No | "light", "moderate", "heavy" adjustment |

## Output Format

```json
{
  "converted_text": "string",
  "original_tone": "string",
  "target_tone": "string",
  "readability_score": "float",
  "changes_made": ["string"]
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
