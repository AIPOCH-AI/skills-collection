---
name: figure-legend-gen
description: Generate standardized figure legends for scientific charts and graphs.
  Trigger when user uploads/requesting legend for research figures, academic papers,
  or data visualizations. Supports bar charts, line graphs, scatter plots, box plots,
  heatmaps, and microscopy images.
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
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

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
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
