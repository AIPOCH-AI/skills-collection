---
name: pptx-posters
description: Generate PowerPoint presentations and academic posters from paper content
trigger: powerpoint, poster, pptx, presentation, academic
tier: B
---

# PPTX Posters

Generate PowerPoint presentations and academic posters from paper abstracts or content.

## Usage

```bash
python scripts/main.py --abstract paper.txt --format poster --output poster.pptx
python scripts/main.py --paper paper.pdf --format slides --template academic
```

## Parameters

- `--abstract`: Abstract text or file
- `--paper`: Full paper PDF
- `--format`: Output format (poster/slides)
- `--template`: Design template (academic/minimal/colorful)
- `--output`: Output file

## Features

- Automatic content extraction
- Section layout optimization
- Figure placeholders
- Citation formatting

## Output

- PowerPoint file (.pptx)
- Layout recommendations
- Design guidelines
