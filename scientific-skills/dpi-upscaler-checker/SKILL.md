---
name: dpi-upscaler-checker
version: 1.0.0
description: Check image DPI and intelligently upscale low-resolution images using super-resolution
category: Image Processing
author: OpenClaw
tags: [dpi, upscaling, super-resolution, image-quality, 300dpi]
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
