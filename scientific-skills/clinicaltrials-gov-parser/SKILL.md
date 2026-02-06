---
name: clinicaltrials-gov-parser
description: |
  Monitor and summarize competitor clinical trial status changes from ClinicalTrials.gov.
  Trigger: When user asks to track clinical trials, monitor trial status changes,
  get updates on specific trials, or analyze competitor trial activities.
  Use cases: Pharma competitive intelligence, trial monitoring, status tracking,
  recruitment updates, completion alerts.
tags: [pharma, clinical-trials, monitoring, api, competitive-intelligence]
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
