# ClinicalTrials.gov Parser - Usage Examples

## Example 1: Monitor Competitor Trials

```python
from scripts.main import ClinicalTrialsMonitor

monitor = ClinicalTrialsMonitor()

# Find all Pfizer diabetes trials
pfizer_trials = monitor.search_trials(
    sponsor="Pfizer",
    condition="Diabetes",
    limit=50
)

print(f"Found {len(pfizer_trials)} Pfizer diabetes trials")

# Extract NCT IDs for monitoring
nct_ids = [t.nct_id for t in pfizer_trials]

# Check for recent status changes
changes = monitor.check_status_changes(nct_ids, days=7)
for change in changes:
    print(f"{change['nct_id']}: {change['status']}")
```

## Example 2: Track Recruitment Status

```python
# Monitor enrollment progress
for nct_id in ["NCT05108922", "NCT05108923"]:
    recruitment = monitor.get_recruitment_status(nct_id)
    if recruitment:
        print(f"{recruitment['nct_id']}: {recruitment['enrollment_count']} enrolled")
```

## Example 3: Generate Weekly Report

```python
# Weekly competitive intelligence report
report = monitor.generate_summary(
    sponsor="Novartis",
    days=7
)

print(f"Total trials: {report['total_trials']}")
print(f"Recent updates: {report['recent_update_count']}")

# Status breakdown
for status, count in report['status_breakdown'].items():
    print(f"  {status}: {count}")
```

## Example 4: CLI Usage

### Search by sponsor
```bash
python scripts/main.py search --sponsor "Pfizer" --limit 20
```

### Get specific trial
```bash
python scripts/main.py get NCT05108922
```

### Monitor multiple trials
```bash
python scripts/main.py monitor --trials "NCT05108922,NCT05108923" --days 7
```

### Generate JSON report
```bash
python scripts/main.py report --sponsor "Pfizer" --days 30 --output json
```

## Example 5: Batch Processing

```python
# Monitor multiple sponsors
sponsors = ["Pfizer", "Novartis", "Roche"]
all_trials = []

for sponsor in sponsors:
    trials = monitor.search_trials(sponsor=sponsor, limit=100)
    all_trials.extend(trials)

# Find recruiting phase 3 trials
phase3_recruiting = [
    t for t in all_trials 
    if t.status == "RECRUITING" and t.phase == "PHASE3"
]

print(f"Phase 3 recruiting trials: {len(phase3_recruiting)}")
```
