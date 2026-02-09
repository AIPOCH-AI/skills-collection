---
name: alumni-career-tracker
description: Analyze lab alumni career destinations to help new students with career
  planning
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

# Alumni Career Tracker (ID: 186)

## Overview

Analyzes the career destinations of past lab graduates (industry vs academia) to help new students with career planning.

## Use Cases

- Understanding lab graduate career trajectories when new students enroll
- Statistics on industry vs academia distribution ratio
- Identifying popular industry directions and companies
- Tracking academic institutions and research areas
- Providing data support for career planning

## Data Structure

### Input: Alumni Record

```json
{
  "name": "Zhang San",
  "graduation_year": 2023,
  "degree": "PhD|Master|Bachelor",
  "current_status": "industry|academia|startup|other",
  "organization": "Company/School Name",
  "position": "Position/Title",
  "location": "City/Country",
  "field": "Research Area/Industry Direction",
  "salary_range": "optional: Salary Range",
  "notes": "Additional Information"
}
```

### Output: Career Analysis Report

```json
{
  "summary": {
    "total_alumni": 100,
    "industry_ratio": 0.65,
    "academia_ratio": 0.25,
    "startup_ratio": 0.07,
    "other_ratio": 0.03
  },
  "by_degree": {
    "PhD": { "industry": 30, "academia": 20 },
    "Master": { "industry": 25, "academia": 5 },
    "Bachelor": { "industry": 10, "academia": 0 }
  },
  "top_companies": [...],
  "top_academic_institutions": [...],
  "trend_by_year": [...],
  "recommendations": [...]
}
```

## Usage

### Command Line

```bash
# Add alumni record
python scripts/main.py add --name "Zhang San" --year 2023 --degree PhD --status industry --org "Google" --position "Research Scientist"

# Batch import
cat alumni.json | python scripts/main.py import

# Generate analysis report
python scripts/main.py analyze --output report.json

# Filter by year
python scripts/main.py analyze --year-from 2020 --year-to 2024

# Visualization report
python scripts/main.py visualize --output chart.png
```

### Python API

```python
from skills.alumni_career_tracker.scripts.main import AlumniTracker

tracker = AlumniTracker(data_path="alumni.json")

# Add record
tracker.add_alumni({
    "name": "Zhang San",
    "graduation_year": 2023,
    "degree": "PhD",
    "current_status": "industry",
    "organization": "Google",
    "position": "Research Scientist"
})

# Generate report
report = tracker.analyze()
print(report.to_json())

# Get recommendations for new student
recs = tracker.get_recommendations(degree="PhD", interest="AI")
```

## Storage

Uses local JSON file storage by default, can be extended to support:
- SQLite database
- Feishu Bitable
- Google Sheets

## Dependencies

- Python 3.8+
- pandas (data analysis)
- matplotlib/seaborn (visualization)
- rich (command line beautified output)

## Author

Created by OpenClaw Agent

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
