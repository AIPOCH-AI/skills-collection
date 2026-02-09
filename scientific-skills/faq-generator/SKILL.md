---
name: faq-generator
description: Generates FAQ lists from complex medical policies or protocols. Trigger when user provides medical documents, policies, or protocols and requests FAQ generation, patient education materials, or simplified explanations.
version: 1.0.0
category: Info
tags: [faq, policy, patient-education, protocol, medical-documents]
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: 
last_updated: 2026-02-06
---

# FAQ Generator

Creates FAQ lists from medical documents.

## Features

- Automatic Q&A generation
- Policy interpretation
- Patient-friendly language
- Structured formatting

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document` | str | Yes | Source document |
| `audience` | str | No | "patients", "researchers" |

## Output Format

```json
{
  "faqs": [{"question": "", "answer": ""}],
  "topic": "string"
}
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | No scripts included | Low |
| Network Access | No external API calls | Low |
| File System Access | Read-only within workspace | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Input/output within session | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] No network requests to external services
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place

## Evaluation Criteria

### Success Metrics
- [ ] FAQ accurately represents source document content
- [ ] Language is appropriate for specified audience (patients/researchers)
- [ ] Questions cover key points of the document
- [ ] Answers are clear, concise, and medically accurate
- [ ] Format follows structured JSON schema

### Test Cases
1. **Basic FAQ Generation**: Input simple medical protocol → Output valid FAQ list
2. **Audience Adaptation**: Same input with different audiences → Appropriate tone shift
3. **Complex Document**: Input lengthy policy document → Comprehensive FAQ coverage
4. **Edge Case**: Input ambiguous content → Handles gracefully with clarifying questions

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Add support for multi-language output
  - Enhance medical terminology handling
