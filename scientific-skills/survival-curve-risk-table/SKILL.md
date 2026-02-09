---
name: survival-curve-risk-table
description: Automatically align and add "Number at risk" table below Kaplan-Meier
  survival curves, meeting clinical oncology journal standards. Use when generating
  risk tables for survival curves that meet top-tier journal standards such as NEJM/Lancet/JCO,
  automatically calculating the number at risk at each time point.
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

# Survival Curve Risk Table Generator

## Function Overview

Automatically add "Number at risk" tables to Kaplan-Meier survival curves that meet clinical oncology journal standards. Automatically align time points and generate publication-quality combined figures.

## Usage Trigger Conditions

- Need to add number at risk tables to KM survival curves
- Generate survival plots that meet journal requirements such as NEJM, Lancet, JCO
- Risk tables needed in clinical trial reports
- Medical paper chart standardization before submission
- Precise alignment of risk tables with survival curve time axis

## Core Functions

### 1. Automatic Number at Risk Calculation
- Automatically calculate number at risk at each time point from survival data
- Support right-censored data processing
- Count remaining observed subjects by group
- Automatic handling of censoring events

### 2. Journal Standard Formats
- **NEJM Standard**: Clean time axis, groups arranged horizontally
- **Lancet Standard**: Complete statistical information, vertical alignment
- **JCO Standard**: Censoring symbols marked, group comparison
- Support custom journal templates

### 3. Precise Alignment
- Time axis precisely aligned with curve X-axis
- Automatic adjustment of table spacing and font size
- Responsive layout adapts to different image sizes
- Support horizontal/vertical layouts

### 4. Output Formats
- High-quality PNG/JPEG images
- PDF vector graphics
- SVG editable format
- PowerPoint embeddable format

## Usage

### Example 1: Basic Risk Table Generation

```bash
python scripts/main.py \
    --input survival_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --output risk_table.png
```

### Example 2: Specify Journal Style

```bash
python scripts/main.py \
    --input survival_data.csv \
    --time-col time \
    --event-col status \
    --group-col arm \
    --style NEJM \
    --time-points 0,6,12,18,24,30,36 \
    --output figure_1a.pdf
```

### Example 3: Combined Figure Generation (Curve + Risk Table)

```bash
python scripts/main.py \
    --input survival_data.csv \
    --time-col months \
    --event-col death \
    --group-col group \
    --km-plot km_curve.png \
    --combine \
    --output combined_figure.png
```

### Example 4: Batch Generate Multi-Timepoint Tables

```bash
python scripts/main.py \
    --input survival_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --time-points 0,12,24,36,48,60 \
    --format both \
    --output-dir ./output/
```

### Example 5: Using Existing Survival Data (Python API)

```python
from scripts.main import RiskTableGenerator

# Initialize generator
generator = RiskTableGenerator(
    style="JCO",
    time_points=[0, 6, 12, 18, 24, 30],
    figure_size=(8, 6)
)

# Load survival data
generator.load_data(
    df=survival_df,
    time_col="time",
    event_col="event",
    group_col="treatment_arm"
)

# Generate risk table
generator.generate_risk_table(
    output_path="risk_table.png",
    show_censored=True
)

# Generate combined figure (KM curve + risk table)
generator.generate_combined_plot(
    km_plot_path="km_curve.png",
    output_path="combined_figure.pdf"
)
```

## Input Data Format

### CSV Format Example

```csv
time,event,treatment_arm
0,0,Experimental
3.2,1,Experimental
5.1,0,Experimental
12.3,1,Control
18.7,0,Control
24.0,1,Experimental
...
```

### Required Columns

| Column Name | Description | Type |
|------|------|------|
| time | Follow-up time (months) | Numeric |
| event | Event occurrence flag | 0=Censored, 1=Event |
| group | Treatment group (optional) | Text/Categorical |

### Supported Data Formats

- CSV (.csv)
- Excel (.xlsx, .xls)
- SAS (.sas7bdat)
- RData (.rda, .rds)
- Python pickle (.pkl)

## Journal Style Configuration

### NEJM Style

```json
{
  "style": "NEJM",
  "font_family": "Helvetica",
  "font_size": 8,
  "time_points": [0, 6, 12, 18, 24, 30, 36],
  "table_height": 0.15,
  "show_grid": false,
  "separator_lines": true
}
```

### Lancet Style

```json
{
  "style": "Lancet",
  "font_family": "Times New Roman",
  "font_size": 9,
  "time_points": [0, 12, 24, 36, 48, 60],
  "table_height": 0.18,
  "show_grid": true,
  "header_bold": true
}
```

### JCO Style

```json
{
  "style": "JCO",
  "font_family": "Arial",
  "font_size": 8,
  "time_points": [0, 6, 12, 18, 24, 30],
  "table_height": 0.16,
  "show_censored": true,
  "censor_symbol": "+"
}
```

## Command Line Parameters

### Required Parameters

| Parameter | Description | Example |
|------|------|------|
| `--input` | Input data file path | `data.csv` |
| `--time-col` | Time column name | `time` |
| `--event-col` | Event column name | `event` |

### Optional Parameters

| Parameter | Description | Default Value |
|------|------|--------|
| `--group-col` | Group column name | `None` |
| `--output` | Output file path | `risk_table.png` |
| `--style` | Journal style | `NEJM` |
| `--time-points` | Time point list | Auto-calculated |
| `--format` | Output format | `png` |
| `--width` | Image width | `8` (inches) |
| `--height` | Image height | `6` (inches) |
| `--dpi` | Image resolution | `300` |
| `--font-size` | Font size | `8` |
| `--show-censored` | Show censored count | `False` |
| `--combine` | Combine with KM curve | `False` |
| `--km-plot` | KM curve image path | `None` |

## Output Format

### Standalone Risk Table
```
┌─────────────────────────────────────────────────────────┐
│  Number at risk                                         │
├─────────┬─────┬─────┬─────┬─────┬─────┬─────┬───────────┤
│ Group   │  0  │ 12  │ 24  │ 36  │ 48  │ 60  │ 72 (mo)   │
├─────────┼─────┼─────┼─────┼─────┼─────┼─────┼───────────┤
│ Exp     │ 150 │ 142 │ 128 │ 105 │  89 │  72 │  58       │
│ Control │ 148 │ 135 │ 118 │  92 │  76 │  61 │  45       │
└─────────┴─────┴─────┴─────┴─────┴─────┴─────┴───────────┘
```

### Combined Figure Layout
```
┌─────────────────────────────────────┐
│                                     │
│     Kaplan-Meier Survival Curve     │
│                                     │
│    ━━━━━━━━━  Experimental         │
│    ─ ─ ─ ─ ─  Control              │
│                                     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Number at risk                      │
│ Exp    150  142  128  105   89   72 │
│ Ctrl   148  135  118   92   76   61 │
│         0   12   24   36   48   60  │
└─────────────────────────────────────┘
```

## Algorithm Description

### Number at Risk Calculation

```
For each time point t:
    For each group g:
        N_at_risk(t, g) = N_total(g) 
                          - Σ(patients with events occurring ≤ t)
                          - Σ(patients censored occurring < t)
```

### Time Point Selection Strategy

1. **Auto Mode**: Automatically select equally spaced time points based on data distribution
2. **Fixed Interval**: Select at specified intervals (e.g., every 6 months)
3. **Custom**: User-specified specific time points
4. **Event-driven**: Select based on event occurrence density

## Quality Checklist

- [ ] Time axis precisely aligned with X-axis
- [ ] Number at risk calculations correct (can manually spot-check)
- [ ] Group labels clear and readable
- [ ] Font size meets journal requirements (≥8pt)
- [ ] Image resolution ≥300 DPI
- [ ] Color contrast meets accessibility standards
- [ ] Censoring marks (if present) clearly distinguishable
- [ ] Export format meets submission requirements

## Journal-Specific Notes

### NEJM
- Minimum font size 8pt
- Recommended time unit: months
- Fixed spacing between risk table and curve

### Lancet
- Minimum font size 9pt
- Support multi-group display (max 4 groups)
- Table grid lines optional

### JCO
- Need to label censoring information
- Support risk table + censoring table double-layer structure
- Recommend labeling median follow-up time

## FAQ

### Q: How are time points automatically determined?
A: Default uses quantiles in the data (0%, 25%, 50%, 75%, 100%) or fixed intervals (e.g., every 12 months)

### Q: How to handle multiple groups?
A: Automatically detect group column, support up to 6 groups. Exceeding automatically uses pagination or reduced font

### Q: Can it work with KM curves generated by Python/R?
A: Yes, supports importing external KM curve images for combination

## Dependency Requirements

```
numpy >= 1.20.0
pandas >= 1.3.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
lifelines >= 0.27.0  (optional, for survival analysis)
Pillow >= 8.0.0      (image processing)
```

## Related Tools

- lifelines: Python survival analysis library
- survminer: R survival curve visualization
- ggsurvplot: ggplot2 survival plot extension

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
