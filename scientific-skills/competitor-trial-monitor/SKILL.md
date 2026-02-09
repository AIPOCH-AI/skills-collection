---
name: competitor-trial-monitor
description: Monitor competitor clinical trial progress and alert on market risks
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Competitor Trial Monitor (ID: 178)

Monitor competitor clinical trial progress and alert on market risks.

## Features

- Monitor changes in clinical trial status for specified competitors
- Track key milestones: enrollment completion, data unblinding, final results publication
- Alert on potential market competition risks

## Data Sources

- **ClinicalTrials.gov** - US Clinical Trials Registry
- **EU Clinical Trials Register** - EU Clinical Trials Registry
- **WHO ICTRP** - International Clinical Trials Registry Platform

## Usage

### Add Monitoring Target

```bash
python scripts/main.py add --nct NCT05108922 --company "Pfizer" --drug "PF-07321332" --indication "COVID-19"
```

### Scan for Updates

```bash
python scripts/main.py scan
```

### View Monitoring List

```bash
python scripts/main.py list
```

### Remove Monitoring Target

```bash
python scripts/main.py remove --nct NCT05108922
```

### Generate Risk Report

```bash
python scripts/main.py report --days 30
```

## Data Storage

Monitoring configuration and data stored in `~/.openclaw/competitor-trial-monitor/`:
- `watchlist.json` - Monitoring list
- `history/` - Historical snapshots
- `alerts/` - Alert records

## Alert Rules

| Event | Risk Level | Description |
|------|----------|------|
| Enrollment Completion | 🟡 Medium | Competitor enters next phase |
| Data Unblinding | 🔴 High | Results about to be announced |
| Results Publication | 🔴 High | Direct impact on market competition |
| Regulatory Submission | 🔴 High | Marketing application in progress |
| Approval Granted | 🔴 Critical | Direct competition begins |

## Dependencies

```bash
pip install requests python-dateutil
```

## Configuration File

`~/.openclaw/competitor-trial-monitor/config.json`:

```json
{
  "alert_channels": ["feishu"],
  "scan_interval_hours": 24,
  "risk_threshold": "medium"
}
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
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
