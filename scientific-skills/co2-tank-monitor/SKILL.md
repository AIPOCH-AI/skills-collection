---
name: co2-tank-monitor
description: IoT monitoring simulation to predict CO2 tank depletion and prevent weekend
  cell death
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# CO2 Tank Monitor

Simulates IoT monitoring to predict when cell culture room CO2 cylinders will be depleted, preventing weekend gas outage that leads to cell death.

## Background

Cell culture requires a stable CO2 environment (typically 5% CO2). Cylinder depletion causes CO2 concentration in incubators to drop, pH to rise, and cell death. The risk is particularly high on weekends when laboratories are unmanned.

## Features

- Simulates CO2 cylinder pressure sensor data reading
- Predicts remaining usage time based on consumption rate
- Detects weekend gas outage risk and provides early warning
- Supports multiple cylinder specifications (10L, 40L, etc.)

## Usage

```bash
# Run with default parameters
python scripts/main.py

# Run with specified parameters
python scripts/main.py --pressure 5.5 --capacity 40 --daily-consumption 2.0 --alert-days 2

# Simulation mode (random data generation)
python scripts/main.py --simulate
```

### Parameter Description

| Parameter | Default Value | Description |
|------|--------|------|
| `--pressure` | 8.0 MPa | Current cylinder pressure |
| `--capacity` | 40 L | Cylinder capacity |
| `--daily-consumption` | 1.5 MPa/day | Average daily consumption |
| `--alert-days` | 2 | Early warning days in advance |
| `--simulate` | False | Enable simulation mode (random data) |

## Alert Rules

- 🟢 **Normal**: Remaining days > alert days + 2
- 🟡 **Caution**: Remaining days within alert days + 2 range
- 🔴 **Danger**: Remaining days ≤ alert days, or depletion time falls on weekend

## Output Example

```
========================================
       CO2 Cylinder Monitor Report
========================================
📅 Current Time: 2025-02-06 09:30:00
📊 Sensor Data:
   Current Pressure: 5.20 MPa
   Cylinder Capacity: 40 L
   Daily Consumption: 1.50 MPa/day

⏱️  Prediction Analysis:
   Estimated Remaining Days: 3.5 days
   Estimated Depletion Time: 2025-02-09 21:30 (Sunday night)

🚨 Alert Status: 🔴 Danger
   ⚠️  Cylinder will deplete over the weekend!
   💡 Suggestion: Please replace cylinder immediately or arrange weekend duty
========================================
```

## Return Codes

| Return Code | Meaning |
|--------|------|
| 0 | Normal, no risk |
| 1 | Caution, needs attention |
| 2 | Danger, action required |

## Integration Suggestions

Can add this script to scheduled tasks (e.g., check every morning at 9 AM):

```cron
0 9 * * * cd /path/to/skills/co2-tank-monitor && python scripts/main.py --pressure $(cat /path/to/pressure_sensor.log | tail -1)
```

## Dependencies

- Python 3.7+
- No third-party dependencies (uses only standard library)

## Author

- ID: 182
- Purpose: Biology laboratory CO2 cylinder monitoring

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
