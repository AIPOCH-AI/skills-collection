---
name: smart-journal-monitor
description: AI-powered journal monitoring with breakthrough article detection and
  key impact summaries
version: 1.0.0
category: Research
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Smart Journal Monitor (RSS+AI)

Personalized research digest from top journals.

## Use Cases
- Staying current with field developments
- Finding high-impact papers efficiently
- Competitive intelligence

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `keywords` | list[str] | Yes | - | Research topics to monitor |
| `journals` | list[str] | No | ["Nature", "Science", "Cell", "NEJM", "Lancet"] | Target journals to monitor |
| `alert_frequency` | str | No | "daily" | Digest frequency: "daily" or "weekly" |

## Returns
- Curated article list with impact scores
- One-sentence key takeaways
- Relevance ranking

## Example
Input: Keywords=["immunotherapy", "checkpoint inhibitor"], frequency=daily
Output: 3-5 most relevant breakthrough papers with summaries

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
