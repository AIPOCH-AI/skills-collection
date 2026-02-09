---
name: western-blot-quantifier
description: Automatically identify Western Blot gel bands, perform densitometric
  analysis, and calculate normalized values relative to loading controls (GAPDH, β-actin,
  Tubulin).
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

# Western Blot Quantifier

Automatically identify Western Blot gel bands, perform densitometric analysis, and calculate normalized values relative to loading controls.

## Features

- **Automatic Band Detection**: Detect protein band positions in gel images
- **Densitometric Analysis**: Calculate grayscale/optical density values for each band
- **Normalization**: Normalize relative to loading control proteins (e.g., GAPDH, β-actin, Tubulin)
- **Data Export**: Output quantitative results in CSV format

## Usage

### Basic Usage

```python
# Call in Python
from skills.western_blot_quantifier.scripts.main import WesternBlotQuantifier

# Create analyzer
analyzer = WesternBlotQuantifier()

# Analyze single image
result = analyzer.analyze(
    image_path="path/to/wb_image.png",
    reference_bands=["GAPDH"],  # Loading control band names
    target_bands=["p53", "Bcl-2"],  # Target protein band names
    lane_positions=[0.2, 0.4, 0.6, 0.8]  # Lane positions (relative to image width)
)

print(result.summary())
result.save("output/quantification_results.csv")
```

### Command Line Usage

```bash
python -m skills.western_blot_quantifier.scripts.main \
    --input path/to/wb_image.png \
    --reference GAPDH \
    --targets p53,Bcl-2 \
    --lanes 4 \
    --output results.csv
```

## Parameter Description

| Parameter | Description | Default |
|------|------|--------|
| `image_path` | Gel image path | Required |
| `reference_bands` | Loading control protein name list | ["GAPDH"] |
| `target_bands` | Target protein name list | [] |
| `lane_positions` | Lane position list | Auto-detect |
| `threshold` | Band detection threshold | 0.1 |
| `background_correction` | Background correction method | "rolling_ball" |

## Output Format

### CSV Output Example

```csv
Lane,Protein,Raw_Intensity,Background,Corrected_Intensity,Normalized_to_Reference
1,GAPDH,125000.5,5000.2,120000.3,1.00
1,p53,85000.2,3000.1,82000.1,0.68
1,Bcl-2,62000.8,2500.5,59500.3,0.50
2,GAPDH,118000.3,4800.2,113200.1,1.00
...
```

### Return Object

```python
{
    "raw_data": DataFrame,           # Raw optical density data
    "normalized_data": DataFrame,    # Normalized data
    "band_regions": List[Dict],      # Detected band region coordinates
    "statistics": Dict,              # Statistical analysis results
    "figures": Dict                  # Visualization chart paths
}
```

## Dependencies

```
numpy>=1.21.0
opencv-python>=4.5.0
pandas>=1.3.0
matplotlib>=3.4.0
scipy>=1.7.0
scikit-image>=0.18.0
```

## Installation

```bash
pip install -r requirements.txt
```

## Notes

1. **Image Quality**: High resolution, good contrast grayscale or black and white gel images are recommended
2. **Loading Control Selection**: Common loading controls include GAPDH, β-actin, Tubulin; selection depends on experimental conditions
3. **Background Correction**: Supports rolling_ball, median, none three background correction methods
4. **Lane Marking**: If auto-detection is inaccurate, lane positions can be manually specified

## Examples

### Example 1: Basic Analysis

```python
from skills.western_blot_quantifier.scripts.main import WesternBlotQuantifier

analyzer = WesternBlotQuantifier()

# Analyze 4-lane Western Blot results
result = analyzer.analyze(
    image_path="experiment_data/wb_gel.png",
    reference_bands=["GAPDH"],
    target_bands=["p53", "p21"],
    lane_count=4
)

# View normalized results
print(result.normalized_data)

# Save charts
result.save_figures("output/")
```

### Example 2: Batch Processing

```python
import glob

analyzer = WesternBlotQuantifier()

for image_path in glob.glob("experiments/*.png"):
    result = analyzer.analyze(
        image_path=image_path,
        reference_bands=["β-actin"],
        target_bands=["Target_Protein"],
        lane_count=6
    )
    result.save(f"output/{Path(image_path).stem}_results.csv")
```

## Algorithm Description

1. **Image Preprocessing**: Grayscale conversion → Background correction → Denoising
2. **Lane Detection**: Automatic lane boundary identification based on vertical projection analysis
3. **Band Detection**: Band localization using 1D Gaussian fitting or peak detection algorithms
4. **Optical Density Calculation**: Integrate grayscale values in band region, subtract background
5. **Normalization**: Target protein value / Loading control protein value

## Author

OpenClaw Skills

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
