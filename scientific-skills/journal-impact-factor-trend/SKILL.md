---
name: journal-impact-factor-trend
description: Show journal impact factor and quartile trends over 5 years
trigger: journal, impact factor, trend, quartile
tier: C
---

# Journal Impact Factor Trend

Display 5-year impact factor and quartile trends for target journals to identify rising or declining journals.

## Usage

```bash
python scripts/main.py --journal "Nature Medicine"
python scripts/main.py --journal-list journals.txt
```

## Parameters

- `--journal`: Journal name
- `--journal-list`: File with journal names
- `--years`: Number of years to analyze (default: 5)
- `--output`: Output format (table/plot)

## Output

- 5-year IF trend table
- Quartile ranking changes
- Trend analysis (rising/stable/declining)
