---
name: lay-summary-gen
description: Converts complex medical abstracts into plain language summaries for
  patients, caregivers, and the general public. Ensures readability while maintaining
  scientific accuracy.
version: 1.0.0
category: General
tags:
- patient-education
- plain-language
- health-literacy
- communication
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Lay Summary Gen

Generates plain-language summaries of medical research for non-expert audiences.

## Features

- Complex to simple language conversion
- Jargon elimination
- Reading level optimization (Grade 6-8)
- Key takeaways extraction
- EU CTR compliance support

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `abstract` | str | Yes | Original medical abstract |
| `target_audience` | str | No | "patients", "public", "media" |
| `max_words` | int | No | Maximum word count (default: 250) |

## Output Format

```json
{
  "lay_summary": "string",
  "reading_level": "string",
  "key_takeaways": ["string"],
  "word_count": "int",
  "jargon_replaced": [{"term": "plain"}]
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
