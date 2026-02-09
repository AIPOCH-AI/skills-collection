---
name: medical-device-mdr-auditor
description: Audit medical device technical files against EU MDR 2017/745 regulations
  for compliance
version: 1.0.0
category: Pharma
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

# Medical Device MDR Auditor

**ID**: 130  
**Version**: 1.0.0  
**Description**: Check whether medical device technical files contain required documents according to EU MDR (2017/745) regulations

---

## Overview

This Skill is used to audit the compliance of medical device technical files, checking whether documents contain necessary Clinical Evaluation Reports and Post-Market Surveillance plans according to EU MDR 2017/745 regulatory requirements.

## Usage

```bash
# Check single technical file directory
python3 /Users/z04030865/.openclaw/workspace/skills/medical-device-mdr-auditor/scripts/main.py --input /path/to/technical/file --class IIa

# Batch check using JSON configuration file
python3 /Users/z04030865/.openclaw/workspace/skills/medical-device-mdr-auditor/scripts/main.py --config /path/to/config.json

# Output detailed report
python3 /Users/z04030865/.openclaw/workspace/skills/medical-device-mdr-auditor/scripts/main.py --input /path/to/technical/file --class III --verbose --output report.json
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--input` | string | Conditional | Technical file directory path |
| `--config` | string | Conditional | JSON configuration file path |
| `--class` | string | Yes | Device classification (I, IIa, IIb, III) |
| `--output` | string | No | Output report path |
| `--verbose` | flag | No | Output detailed information |

## MDR 2017/745 Check Points

### 1. Clinical Evaluation Report (CER)

According to MDR Annex XIV Part A, must include:
- [ ] Clinical Evaluation Plan
- [ ] Clinical Data Assessment (Literature review / Clinical investigation data)
- [ ] Clinical Evidence Analysis
- [ ] Benefit-risk Conclusion

### 2. Post-Market Surveillance Plan (PMS)

According to MDR Article 83 & Annex III, must include:
- [ ] PMS procedure description
- [ ] Data collection methods
- [ ] Risk assessment update mechanism
- [ ] Trend reporting mechanism

### 3. Post-Market Clinical Follow-up Plan (PMCF Plan)

According to MDR Annex XIV Part B, for Class IIa and above devices:
- [ ] PMCF plan document
- [ ] Clinical data continuous collection methods
- [ ] Safety and performance monitoring procedures

### 4. Other Key Documents

- [ ] Risk Management File (ISO 14971)
- [ ] Usability Engineering File
- [ ] Biological Evaluation Report
- [ ] Labeling & Instructions for Use

## Output Format

### Compliance Report Example

```json
{
  "audit_date": "2026-02-06T06:00:00Z",
  "device_class": "IIa",
  "compliance_status": "PARTIAL",
  "findings": [
    {
      "category": "CRITICAL",
      "regulation": "MDR Annex XIV Part A",
      "item": "Clinical Evaluation Report",
      "status": "MISSING",
      "description": "Clinical evaluation report file not found"
    },
    {
      "category": "MAJOR",
      "regulation": "MDR Article 83",
      "item": "PMS Plan",
      "status": "INCOMPLETE",
      "description": "PMS plan lacks trend reporting mechanism"
    }
  ],
  "summary": {
    "total_checks": 12,
    "passed": 8,
    "warnings": 2,
    "failed": 2
  }
}
```

## Compliance Levels

| Level | Description |
|-------|-------------|
| `COMPLIANT` | Fully compliant with MDR requirements |
| `PARTIAL` | Partially compliant, with correctable deficiencies |
| `NON_COMPLIANT` | Seriously non-compliant, critical documents missing |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Audit passed, fully compliant |
| 1 | Audit passed, with warnings |
| 2 | Audit failed, with deficiencies |
| 3 | Execution error |

## References

- Regulation (EU) 2017/745 (MDR)
- MDCG Guidance Documents
- EN ISO 14971:2019
- EN ISO 13485:2016

## Author

OpenClaw Skill Development Team

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

```bash
# Python dependencies
pip install -r requirements.txt
```

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
