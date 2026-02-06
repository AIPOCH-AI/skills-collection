---
name: equipment-maintenance-log
description: Track lab equipment calibration dates and send maintenance reminders
trigger: equipment, calibration, maintenance, reminder
tier: C
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
