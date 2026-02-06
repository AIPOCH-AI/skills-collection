---
name: grant-gantt-chart-gen
description: Create project timeline visualizations for grant proposals
trigger: gantt, chart, timeline, grant, project plan, visualization
tier: B
---

# Grant Gantt Chart Generator

Create project timeline visualizations for grant proposals.

## Usage

```bash
python scripts/main.py --milestones milestones.csv --duration 36 --output gantt.png
```

## Parameters

- `--milestones`: Milestone data file
- `--duration`: Project duration in months
- `--start-date`: Project start date
- `--output`: Output file
- `--format`: Output format (png/pdf/svg)

## Features

- Timeline visualization
- Milestone markers
- Task dependencies
- Personnel allocation
- Quarterly breakdown

## Output

- Gantt chart image
- Timeline data (CSV)
- Milestone summary
