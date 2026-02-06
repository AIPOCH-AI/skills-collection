---
name: image-duplication-detector
description: Detect image duplication and tampering in manuscript figures using computer vision algorithms
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
