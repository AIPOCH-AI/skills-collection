---
name: forest-plot-styler
description: Beautify meta-analysis forest plots with customizable odds ratio points and confidence intervals
---

# Forest Plot Styler

ID: 157

Beautifies Meta-analysis or subgroup analysis forest plots, customizes Odds Ratio point sizes and confidence interval line styles.

---

## Features

- Reads Meta-analysis data (CSV/Excel format)
- Draws high-quality forest plots
- Customizes Odds Ratio point sizes, colors, and shapes
- Customizes confidence interval line styles (color, thickness, endpoint style)
- Supports subgroup analysis display
- Automatically calculates and displays pooled effect values
- Outputs to PNG, PDF, or SVG format

---

## Usage

```bash
python scripts/main.py --input <data.csv> [options]
```

### Parameters

| Parameter | Short | Description | Default |
|------|------|------|--------|
| `--input` | `-i` | Input data file (CSV or Excel) | Required |
| `--output` | `-o` | Output file path | `forest_plot.png` |
| `--format` | `-f` | Output format: png/pdf/svg | `png` |
| `--point-size` | | OR point size | `8` |
| `--point-color` | | OR point color | `#2E86AB` |
| `--ci-color` | | Confidence interval line color | `#2E86AB` |
| `--ci-linewidth` | | Confidence interval line thickness | `2` |
| `--ci-capwidth` | | Confidence interval endpoint width | `5` |
| `--summary-color` | | Pooled effect point color | `#A23B72` |
| `--summary-shape` | | Pooled effect point shape | `diamond` |
| `--subgroup` | | Subgroup analysis column name | None |
| `--title` | `-t` | Chart title | `Forest Plot` |
| `--xlabel` | `-x` | X-axis label | `Odds Ratio (95% CI)` |
| `--reference-line` | | Reference line position (usually 1) | `1` |
| `--width` | `-W` | Image width (inches) | `12` |
| `--height` | `-H` | Image height (inches) | Auto-calculate |
| `--dpi` | | Image resolution | `300` |
| `--font-size` | | Font size | `10` |
| `--style` | `-s` | Preset style: default/minimal/dark | `default` |

---

## Input Data Format

CSV/Excel files must contain the following columns:

| Column Name | Description | Type |
|------|------|------|
| `study` | Study name | Text |
| `or` | Odds Ratio value | Numeric |
| `ci_lower` | Confidence interval lower bound | Numeric |
| `ci_upper` | Confidence interval upper bound | Numeric |
| `weight` | Weight (optional, for point size) | Numeric |
| `subgroup` | Subgroup label (optional) | Text |

### Sample Data

```csv
study,or,ci_lower,ci_upper,weight,subgroup
Study A,0.85,0.65,1.12,15.2,Drug A
Study B,0.72,0.55,0.94,18.5,Drug A
Study C,1.15,0.88,1.50,12.3,Drug B
Study D,0.95,0.75,1.20,14.8,Drug B
```

---

## Examples

### Basic Usage

```bash
python scripts/main.py -i meta_data.csv
```

### Custom Style

```bash
python scripts/main.py -i meta_data.csv \
    --point-color="#E63946" \
    --ci-color="#457B9D" \
    --point-size=10 \
    --ci-linewidth=3 \
    -t "Meta-Analysis of Treatment Effects"
```

### Subgroup Analysis

```bash
python scripts/main.py -i meta_data.csv \
    --subgroup subgroup_column \
    --summary-color="#F4A261" \
    -o subgroup_forest.png
```

### Output PDF Vector Graphic

```bash
python scripts/main.py -i meta_data.csv \
    -f pdf \
    -o forest_plot.pdf
```

---

## Preset Styles

### default
- Blue color scheme
- Standard font size
- White background

### minimal
- Clean lines
- Grayscale color scheme
- No grid lines

### dark
- Dark background
- Bright data points
- Suitable for dark theme presentations

---

## Dependencies

- Python >= 3.8
- matplotlib >= 3.5.0
- pandas >= 1.3.0
- numpy >= 1.20.0
- openpyxl >= 3.0.0 (for reading Excel)

---

## Output Example

Generated forest plot contains:
- Left side: Study name list
- Middle: OR values and confidence intervals
- Right side: Weight percentage (if available)
- Bottom: Pooled effect value (diamond marker)
- Reference line (OR=1)

---

## Notes

1. Ensure input file encoding is UTF-8
2. OR values are automatically converted when log scale is suggested
3. Studies with confidence intervals crossing 1 are not statistically significant
4. Weight values are used to adjust point size, reflecting study contribution
