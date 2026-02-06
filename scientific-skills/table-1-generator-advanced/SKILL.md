---
name: table-1-generator
description: Automated baseline characteristics table generation for clinical papers
trigger: table 1, baseline, characteristics, clinical, demographics
tier: B
---

# Table 1 Generator

Automated generation of baseline characteristics tables (Table 1) for clinical research papers.

## Usage

```bash
python scripts/main.py --data patients.csv --group treatment --output table1.csv
```

## Parameters

- `--data`: Patient data CSV file
- `--group`: Grouping variable (e.g., treatment/control)
- `--vars`: Variables to include
- `--output`: Output file

## Features

- Automatic variable type detection
- Appropriate statistics (mean±SD, median[IQR], n(%))
- Group comparisons (t-test, chi-square)
- Missing data reporting
- APA formatting

## Output

- Table 1 (CSV/Excel)
- Statistical test results
- Formatted for publication
