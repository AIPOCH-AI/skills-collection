---
name: grant-funding-scout
description: NIH funding trend analysis to identify high-priority research areas
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

# Grant Funding Scout

**⚠️ Note: This is a demonstration/illustrative version using mock data for educational purposes. For production use, integration with real funding databases (NIH RePORTER, NSF Award Search, etc.) is required.**

Analyze funding patterns to guide research strategy.

## Use Cases
- Identifying "hot" research topics
- Avoiding oversaturated areas
- Strategic grant positioning

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--research-area` | str | Yes | - | Research field to analyze (e.g., "cancer immunotherapy") |
| `--years` | int | No | 3 | Analysis time window in years |
| `--output` | str | No | stdout | Output file path for results |
| `--format` | str | No | json | Output format: json, csv, or text |
| `--top-n` | int | No | 10 | Number of top results to display |

## Returns
- Top-funded institutions and PIs
- Emerging topic identification
- Funding trend analysis

## Example
Input: "cancer immunotherapy", years=3
Output: Funding increased 40% YoY; CAR-T and checkpoint inhibitors dominate

## Data Sources
**Current Version:** Uses mock funding data for demonstration purposes.

**For Production Use:**
- NIH RePORTER API
- NSF Award Search API
- CORDIS (EU research)
- Federal RePORTER
- Private foundation databases

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
