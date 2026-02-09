---
name: multi-panel-figure-assembler
description: Automatically assemble 6 sub-figures (A-F) into a high-resolution composite
  figure with aligned edges, unified fonts, and labels.
version: 1.0.0
category: Visual
tags:
- image-processing
- figure
- PIL
- OpenCV
- composite
- scientific-figures
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Multi-panel Figure Assembler

A Python-based tool for assembling multi-panel scientific figures. Automatically arranges 6 sub-figures (A-F) into a composite image with consistent styling, labels, and high-resolution output.

## Features

- **Automatic Layout**: Supports 2×3 or 3×2 grid arrangements
- **Edge Alignment**: Intelligently crops/pads images to match dimensions
- **Unified Typography**: Consistent font sizing across all panels
- **Auto Labeling**: Adds panel labels (A-F) with customizable position
- **High Resolution**: Output at 300+ DPI for publication quality

## Installation

Requires Python 3.8+ and the following packages:

```bash
pip install Pillow numpy
```

Optional for advanced features:
```bash
pip install opencv-python-headless
```

## Usage

```bash
python scripts/main.py --input A.png B.png C.png D.png E.png F.png --output figure.png [OPTIONS]
```

### Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--input` / `-i` | Yes | - | 6 input image paths (A-F) |
| `--output` / `-o` | Yes | - | Output file path |
| `--layout` / `-l` | No | `2x3` | Layout: `2x3` or `3x2` |
| `--dpi` / `-d` | No | `300` | Output DPI (dots per inch) |
| `--label-font` | No | `Arial` | Font family for labels |
| `--label-size` | No | `24` | Font size for panel labels |
| `--label-position` | No | `topleft` | Label position: `topleft`, `topright`, `bottomleft`, `bottomright` |
| `--padding` / `-p` | No | `10` | Padding between panels (pixels) |
| `--border` / `-b` | No | `2` | Border width around each panel (pixels) |
| `--bg-color` | No | `white` | Background color (white/black/hex) |
| `--label-color` | No | `black` | Label text color (black/white/hex) |

### Examples

**Basic usage:**
```bash
python scripts/main.py -i A.png B.png C.png D.png E.png F.png -o figure.png
```

**3×2 layout with custom DPI:**
```bash
python scripts/main.py -i A.png B.png C.png D.png E.png F.png -o figure.png --layout 3x2 --dpi 600
```

**Custom styling:**
```bash
python scripts/main.py -i A.png B.png C.png D.png E.png F.png -o figure.png \
  --label-size 32 --label-position topright --padding 20 --border 4
```

**Programmatic usage:**
```python
from scripts.main import FigureAssembler

assembler = FigureAssembler(
    layout="2x3",
    dpi=300,
    label_size=24,
    padding=10
)

assembler.assemble(
    inputs=["A.png", "B.png", "C.png", "D.png", "E.png", "F.png"],
    output="figure.png",
    labels=["A", "B", "C", "D", "E", "F"]
)
```

## Output

The script generates a high-resolution composite figure with:
- All panels resized to uniform dimensions
- Panel labels (A-F) in specified positions
- Consistent padding and borders
- DPI metadata embedded in output file

## Supported Formats

**Input:** PNG, JPG, JPEG, BMP, TIFF, GIF
**Output:** PNG (recommended), JPG, TIFF

## Notes

- Input images are automatically resized to match the largest dimension while maintaining aspect ratio
- For best results, use input images with similar aspect ratios
- Label fonts require the font to be available on your system
- PNG output preserves transparency if any input images have alpha channels

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
