---
name: microscopy-scale-bar-adder
description: Add scale bars to microscopy images
trigger: microscopy, scale bar, image, measurement
tier: B
---

# Microscopy Scale Bar Adder

Add accurate scale bars to microscopy images.

## Usage

```bash
python scripts/main.py --image image.tif --scale 50 --unit um
```

## Features

- Automatic scale bar calculation
- Support for common microscopy formats
- Configurable bar size and style
