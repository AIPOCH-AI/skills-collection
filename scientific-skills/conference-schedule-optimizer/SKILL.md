---
name: conference-schedule-optimizer
description: Optimize conference schedule to avoid conflicts and maximize attendance
trigger: conference, schedule, optimize, conflict, session
tier: C
---

# Conference Schedule Optimizer

Generate optimal conference listening schedules based on topic interests, avoiding conflicts.

## Usage

```bash
python scripts/main.py --interests "genomics,AI,drug-discovery" --schedule schedule.json
```

## Parameters

- `--interests`: Comma-separated topic interests
- `--schedule`: Conference schedule JSON file
- `--must-attend`: Session IDs that must be included
- `--output`: Optimized schedule output

## Features

- Automatic conflict detection
- Topic relevance scoring
- Travel time between rooms
- Personal schedule export

## Output

- Optimized personal schedule
- Conflict warnings
- Alternative suggestions
