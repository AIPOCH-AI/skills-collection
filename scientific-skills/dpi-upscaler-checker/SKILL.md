---
name: dpi-upscaler-checker
description: Check image DPI and intelligently upscale low-resolution images using
  super-resolution
version: 1.0.0
category: Image Processing
tags:
- dpi
- upscaling
- super-resolution
- image-quality
- 300dpi
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# DPI Upscaler & Checker

Check if images meet 300 DPI printing standards, and intelligently restore blurry low-resolution images using AI super-resolution technology.

## Features

- **DPI Detection**: Read and verify image DPI information
- **Intelligent Analysis**: Calculate actual print size and pixel density
- **Super-Resolution Restoration**: Use Real-ESRGAN algorithm to enhance image clarity
- **Batch Processing**: Support single image and batch folder processing
- **Format Support**: JPG, PNG, TIFF, BMP, WebP

## Use Cases

- Academic paper figure DPI checking
- Print image quality pre-inspection
- Low-resolution material restoration
- Document scan enhancement

## Usage

### Check Single Image DPI
```bash
python scripts/main.py check --input image.jpg
```

### Batch Check Folder
```bash
python scripts/main.py check --input ./images/ --output report.json
```

### Super-Resolution Restoration
```bash
python scripts/main.py upscale --input image.jpg --output upscaled.jpg --scale 4
```

### Batch Fix Low DPI Images
```bash
python scripts/main.py upscale --input ./images/ --output ./output/ --min-dpi 300 --scale 2
```

## Parameter Description

### Check Command
- `--input`: Input image path or folder (required)
- `--output`: Output report path (optional, default stdout)
- `--target-dpi`: Target DPI (default 300)

### Upscale Command
- `--input`: Input image path or folder (required)
- `--output`: Output path (required)
- `--scale`: Scale factor (2/3/4, default 2)
- `--min-dpi`: Only process images below this DPI (optional)
- `--denoise`: Denoise level (0-3, default 0)
- `--face-enhance`: Enable face enhancement (optional)

## Output Description

### DPI Check Report
```json
{
  "file": "image.jpg",
  "dpi": [72, 72],
  "width_px": 1920,
  "height_px": 1080,
  "print_width_cm": 67.7,
  "print_height_cm": 38.1,
  "meets_300dpi": false,
  "recommended_scale": 4.17
}
```

### Restored Image
- Automatically saved as `<original_filename>_upscaled.<extension>`
- Preserves original EXIF information
- Sets DPI to 300

## Dependencies

- Python >= 3.8
- Pillow >= 9.0.0
- opencv-python >= 4.5.0
- numpy >= 1.21.0
- realesrgan (optional, for best results)

## Algorithm Description

### DPI Calculation
```
Actual DPI = Pixel dimensions / Physical dimensions
Print size (cm) = Pixel count / DPI * 2.54
```

### Super-Resolution
- Default use of Real-ESRGAN model
- Support lightweight bicubic interpolation fallback
- Intelligent model selection (general/anime/face)

## Notes

1. Input image DPI information may be inaccurate; actual pixel calculation shall prevail
2. Super-resolution cannot create non-existent information; extremely blurry images have limited improvement
3. Large file processing requires more memory
4. GPU acceleration requires CUDA environment (optional)

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
