---
name: time-zone-planner
description: Helps schedule multinational clinical trial meetings across time zones.
version: 1.0.0
category: Utility
tags: [timezone, scheduling, global, trials]
author: Medical Science Skills
license: MIT
---

# Time Zone Planner

Schedules global multi-center trial meetings.

## Features

- Multi-timezone calculation
- Optimal meeting times
- Region visualization
- DST handling

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `regions` | list | Yes | ["US", "EU", "Asia"] |
| `duration` | int | Yes | Meeting duration in minutes |

## Output Format

```json
{
  "suggested_times": [{"region": "", "time": ""}],
  "optimal_window": "string"
}
```
