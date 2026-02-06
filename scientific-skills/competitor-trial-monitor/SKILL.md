---
name: competitor-trial-monitor
description: Monitor competitor clinical trial progress and alert on market risks
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
