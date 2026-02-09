---
name: equipment-maintenance-log
description: Track lab equipment calibration dates and send maintenance reminders
version: 1.0.0
category: Operations
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

# Equipment Maintenance Log

Track calibration dates for pipettes, balances, centrifuges and send maintenance reminders.

## Usage

```bash
python scripts/main.py --add "Pipette P100" --calibration-date 2024-01-15 --interval 12
python scripts/main.py --check
```

## Parameters

- `--add`: Add new equipment
- `--calibration-date`: Last calibration date (YYYY-MM-DD)
- `--interval`: Calibration interval in months
- `--check`: Check for upcoming maintenance
- `--list`: List all equipment

## Output

- Maintenance schedule
- Overdue alerts
- Upcoming reminders (30/60/90 days)

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
