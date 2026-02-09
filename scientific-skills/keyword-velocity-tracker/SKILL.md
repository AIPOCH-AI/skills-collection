---
name: keyword-velocity-tracker
description: Calculate literature growth velocity and acceleration to assess research
  field development stages
version: 1.0.0
category: General
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

# Skill: Keyword Velocity Tracker

## Metadata
- **ID**: 201
- **Name**: Keyword Velocity Tracker
- **Type**: Analysis Tool
- **Version**: 1.0.0

## Description
Calculate the literature growth rate and acceleration of specific keywords to determine the development stage of academic research fields. By analyzing changes in literature volume over different time periods, provide field popularity trends and lifecycle analysis.

## Functions

### Core Functions
1. **Literature Growth Rate Calculation** - Calculate keyword literature growth rate over different time periods
2. **Growth Acceleration Analysis** - Identify trends of literature growth acceleration or deceleration
3. **Field Development Stage Judgment** - Determine field stage based on growth curve characteristics
4. **Trend Prediction** - Predict future development trends based on historical data

### Stage Judgment Criteria
- **Embryonic Stage**: Low base, slow growth
- **Growth Stage**: Growth rate continues to rise (acceleration is positive)
- **Mature Stage**: Growth rate is stable or declining
- **Decline Stage**: Growth rate is negative

## Input

### Required Parameters
| Parameter | Type | Description |
|------|------|------|
| `keyword` | string | Keyword to analyze |
| `data` | array | Time series literature data, format: `[{"year": 2020, "count": 100}, ...]` |

### Optional Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `time_window` | int | 3 | Time window for calculating growth rate (years) |
| `smoothing` | boolean | true | Whether to smooth the data |
| `predict_years` | int | 3 | Number of future years to predict |

## Output

### Return Value
```json
{
  "keyword": "artificial intelligence",
  "analysis_period": {"start": 2015, "end": 2023},
  "current_velocity": 0.35,
  "current_acceleration": -0.05,
  "stage": "mature",
  "stage_confidence": 0.85,
  "trend": "stable",
  "velocity_series": [
    {"year": 2016, "velocity": 0.20, "acceleration": null},
    {"year": 2017, "velocity": 0.25, "acceleration": 0.05},
    ...
  ],
  "prediction": {
    "2024": {"estimated_count": 1850, "confidence": 0.80},
    "2025": {"estimated_count": 1980, "confidence": 0.70},
    "2026": {"estimated_count": 2100, "confidence": 0.60}
  },
  "insights": [
    "Field has entered mature stage, growth slowing",
    "Recent slight deceleration trend, needs attention"
  ]
}
```

### Stage Definitions
- `current_velocity`: Current annual growth rate (0-1)
- `current_acceleration`: Current acceleration (growth rate change rate)
- `stage`: Field development stage (embryonic/growth/mature/decline)
- `stage_confidence`: Stage judgment confidence (0-1)
- `trend`: Trend direction (growth/stable/decline)

## Usage Examples

### Command Line
```bash
python scripts/main.py --keyword "artificial intelligence" --data-file data.json
```

### Python API
```python
from skills.keyword_velocity_tracker.scripts.main import KeywordVelocityTracker

tracker = KeywordVelocityTracker()
result = tracker.analyze(
    keyword="artificial intelligence",
    data=[
        {"year": 2019, "count": 500},
        {"year": 2020, "count": 650},
        {"year": 2021, "count": 900},
        {"year": 2022, "count": 1100},
        {"year": 2023, "count": 1250}
    ]
)
```

## Dependencies
- Python >= 3.8
- numpy
- scipy

## Configuration

### Environment Variables
| Variable | Description | Default |
|------|------|--------|
| `KVT_SMOOTHING_FACTOR` | Smoothing coefficient | 0.3 |
| `KVT_MIN_CONFIDENCE` | Minimum confidence threshold | 0.7 |

## Algorithm Description

### Growth Rate Calculation
```
velocity(t) = (count(t) - count(t-1)) / count(t-1)
```

### Acceleration Calculation
```
acceleration(t) = velocity(t) - velocity(t-1)
```

### Stage Judgment Logic
1. Average growth rate in last 3 years < 0.1 → Embryonic/Decline stage
2. Acceleration > 0 and growth rate > 0.2 → Growth stage
3. Growth rate stable (fluctuation < 0.1) → Mature stage
4. Growth rate < 0 → Decline stage

## Version History
- 1.0.0 (2024-02-06): Initial version, basic growth rate and acceleration calculation

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
