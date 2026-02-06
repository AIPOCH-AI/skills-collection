---
name: clinicaltrials-gov-parser
description: 'Monitor and summarize competitor clinical trial status changes from
  ClinicalTrials.gov.

  Trigger: When user asks to track clinical trials, monitor trial status changes,

  get updates on specific trials, or analyze competitor trial activities.

  Use cases: Pharma competitive intelligence, trial monitoring, status tracking,

  recruitment updates, completion alerts.

  '
version: 1.0.0
category: General
tags:
- pharma
- clinical-trials
- monitoring
- api
- competitive-intelligence
author: The King of Skills
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# ClinicalTrials.gov Parser

Monitor and summarize competitor clinical trial status changes from ClinicalTrials.gov.

## Use Cases

- **Trial Monitoring**: Track status changes of specific clinical trials
- **Competitive Intelligence**: Monitor competitor trial activities and milestones
- **Recruitment Tracking**: Get updates on enrollment status
- **Completion Alerts**: Monitor trial completion and results posting

## Usage

```python
from scripts.main import ClinicalTrialsMonitor

# Initialize monitor
monitor = ClinicalTrialsMonitor()

# Search for trials
trials = monitor.search_trials(
    sponsor="Pfizer",
    condition="Diabetes",
    status="Recruiting"
)

# Get trial details
trial = monitor.get_trial("NCT05108922")

# Check for status changes
changes = monitor.check_status_changes(trial_ids=["NCT05108922"])
```

## CLI Usage

```bash
# Search trials
python scripts/main.py search --sponsor "Pfizer" --condition "Diabetes"

# Get trial details
python scripts/main.py get NCT05108922

# Monitor status changes
python scripts/main.py monitor --trials NCT05108922,NCT05108923 --output json

# Generate summary report
python scripts/main.py report --sponsor "Pfizer" --days 30
```

## API Methods

| Method | Description |
|--------|-------------|
| `search_trials()` | Search trials with filters |
| `get_trial(nct_id)` | Get detailed trial information |
| `check_status_changes()` | Check for status updates |
| `get_recruitment_status()` | Get enrollment updates |
| `generate_summary()` | Generate competitor summary |

## Technical Details

- **API**: ClinicalTrials.gov API v2
- **Rate Limit**: 10 requests/second
- **Data Format**: JSON
- **Difficulty**: Medium

## References

- See `references/api-docs.md` for API documentation
- See `references/status-codes.md` for trial status definitions
- See `references/examples.md` for usage examples

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
