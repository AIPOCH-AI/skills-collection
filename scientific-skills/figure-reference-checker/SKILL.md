---
name: figure-reference-checker
description: Check figure references in manuscripts
trigger: figure, reference, citation, manuscript
tier: B
---

# Figure Reference Checker

Check consistency of figure references in manuscripts.

## Usage

```bash
python scripts/main.py --manuscript paper.docx
```

## Features

- Detect orphaned figure references
- Check figure-label consistency
- Flag missing citations
