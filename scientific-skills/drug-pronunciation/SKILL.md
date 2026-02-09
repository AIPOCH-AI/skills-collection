---
name: drug-pronunciation
description: Provides correct pronunciation guides for complex drug generic names.
  Generates phonetic transcriptions using IPA and audio generation markers for medical
  terminology.
version: 1.0.0
category: Education
tags:
- pharmacology
- pronunciation
- medical-terminology
- education
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Drug Pronunciation

Medical drug name pronunciation assistant with IPA phonetics and syllable breakdown.

## Features

- IPA phonetic transcriptions
- Syllable-by-syllable breakdown
- Emphasis markers
- Audio generation markers (SSML-compatible)
- Coverage of 1000+ common medications

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drug_name` | str | Yes | Generic or brand drug name |
| `format` | str | No | Output format: "ipa", "simple", "detailed" |

## Output Format

```json
{
  "drug_name": "string",
  "ipa_transcription": "string",
  "syllable_breakdown": ["string"],
  "emphasis": "string",
  "audio_ssml": "string",
  "common_errors": ["string"]
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
