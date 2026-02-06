---
name: figure-legend-gen
description: Generate standardized figure legends for scientific charts and graphs. Trigger when user uploads/requesting legend for research figures, academic papers, or data visualizations. Supports bar charts, line graphs, scatter plots, box plots, heatmaps, and microscopy images.
---

# Figure Legend Generator

Generate publication-quality figure legends for scientific research charts and images.

## Supported Chart Types

| Chart Type | Description |
|------------|-------------|
| Bar Chart | Compare values across categories |
| Line Graph | Show trends over time or continuous data |
| Scatter Plot | Display relationships between variables |
| Box Plot | Show distribution and outliers |
| Heatmap | Visualize matrix data intensity |
| Microscopy | Fluorescence/confocal images |
| Flow Cytometry | FACS plots and histograms |
| Western Blot | Protein expression bands |

## Usage

```bash
python scripts/main.py --input <image_path> --type <chart_type> [--output <output_path>]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input` | Yes | Path to chart image |
| `--type` | Yes | Chart type (bar/line/scatter/box/heatmap/microscopy/flow/western) |
| `--output` | No | Output path for legend text (default: stdout) |
| `--format` | No | Output format (text/markdown/latex), default: markdown |
| `--language` | No | Language (en/zh), default: en |

### Examples

```bash
# Generate legend for bar chart
python scripts/main.py --input figure1.png --type bar

# Save to file
python scripts/main.py --input plot.jpg --type line --output legend.md

# Chinese output
python scripts/main.py --image.png --type scatter --language zh
```

## Legend Structure

Generated legends follow academic standards:

1. **Figure Number** - Sequential numbering
2. **Brief Title** - Concise description
3. **Main Description** - What the figure shows
4. **Data Details** - Key statistics/measurements
5. **Methodology** - Brief experimental context
6. **Statistics** - P-values, significance markers
7. **Scale Bars** - For microscopy images

## Technical Notes

- **Difficulty**: Low
- **Dependencies**: PIL, pytesseract (optional OCR)
- **Processing**: Vision analysis for chart type detection
- **Output**: Structured markdown by default

## References

- `references/legend_templates.md` - Templates by chart type
- `references/academic_style_guide.md` - Formatting guidelines
