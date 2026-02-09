---
name: image-duplication-detector
description: Detect image duplication and tampering in manuscript figures using computer
  vision algorithms
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

# Image Duplication Detector

ID: 195

## Description

Uses Computer Vision (CV) algorithms to scan all images in paper manuscripts to detect potential duplication or local tampering (PS traces).

## Usage

```bash
# Scan single PDF file
python scripts/main.py --input paper.pdf --output report.json

# Scan image folder
python scripts/main.py --input ./images/ --output report.json

# Specify similarity threshold (default 0.85)
python scripts/main.py --input paper.pdf --threshold 0.90 --output report.json

# Enable tampering detection
python scripts/main.py --input paper.pdf --detect-tampering --output report.json

# Generate visualization report
python scripts/main.py --input paper.pdf --visualize --output report.json
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | str | required | Input PDF file or image folder path |
| `--output` | str | `report.json` | Output report path |
| `--threshold` | float | `0.85` | Similarity threshold (0-1), higher is stricter |
| `--detect-tampering` | bool | `false` | Enable tampering/PS trace detection |
| `--visualize` | bool | `false` | Generate visualization comparison images |
| `--temp-dir` | str | `./temp` | Temporary file directory |

## Output Format

```json
{
  "summary": {
    "total_images": 12,
    "duplicates_found": 2,
    "tampering_detected": 1,
    "processing_time": "3.5s"
  },
  "duplicates": [
    {
      "group_id": 1,
      "similarity": 0.98,
      "images": [
        {"page": 2, "index": 1, "path": "..."},
        {"page": 5, "index": 3, "path": "..."}
      ]
    }
  ],
  "tampering": [
    {
      "image": "page_3_img_2.png",
      "suspicious_regions": [
        {"x": 120, "y": 80, "width": 50, "height": 50, "confidence": 0.92}
      ]
    }
  ]
}
```

## Requirements

```
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
PyPDF2>=3.0.0
pdf2image>=1.16.0
imagehash>=4.3.0
scikit-image>=0.21.0
matplotlib>=3.7.0
```

## Algorithm Details

### Duplication Detection
- **Perceptual Hashing**: Uses pHash, dHash, aHash combination to detect visually similar images
- **Feature Matching**: ORB feature point matching to verify similarity
- **SSIM**: Structural similarity index as auxiliary verification

### Tampering Detection
- **ELA (Error Level Analysis)**: Detects JPEG compression level inconsistencies
- **Noise Analysis**: Noise pattern anomaly detection
- **Copy-Move Detection**: Copy-move forgery detection
- **Lighting Inconsistency**: Lighting consistency analysis

## Example

```python
from scripts.main import ImageDuplicationDetector

detector = ImageDuplicationDetector(
    threshold=0.85,
    detect_tampering=True
)

results = detector.scan("paper.pdf")
detector.save_report(results, "report.json")
```

## Notes

- Supports PDF, PNG, JPG, TIFF formats
- Large files recommended for batch processing
- Tampering detection may produce false positives, manual review recommended

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
