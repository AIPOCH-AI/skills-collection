---
name: citation-formatter
description: Automatically formats citations to AMA (American Medical Association) style. Trigger when user needs to convert, correct, or standardize references in academic/medical writing. Handles various input formats including APA, MLA, Vancouver, and free-text citations.
---

# Citation Formatter

Formats academic citations to AMA (American Medical Association) standard.

## Overview

This skill parses citations from various formats and reformats them according to AMA 11th edition guidelines.

## Supported Input Formats

- APA style
- MLA style  
- Vancouver style
- Free-text / unstructured citations
- BibTeX entries
- Partial/incomplete citations

## AMA Output Format

**Journal Article:**
```
Author AA, Author BB. Article title. Journal Name. Year;Volume(Issue):Pages. DOI/URL
```

**Book:**
```
Author AA. Book Title. City, State: Publisher; Year.
```

**Website:**
```
Author/Organization. Page Title. Website Name. URL. Published/Updated Date. Accessed Date.
```

## Usage

### Basic Formatting

```python
from scripts.main import format_citation

result = format_citation("Smith J, Jones M. Title here. Journal 2020;1:1-10")
print(result)  # AMA formatted citation
```

### Batch Processing

```bash
python scripts/main.py --input citations.txt --output formatted.txt
```

### Interactive Mode

```bash
python scripts/main.py --interactive
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input` | str | None | Input citation text or file path |
| `output` | str | None | Output file path |
| `format_type` | str | "auto" | Input format: auto, apa, mla, vancouver, bibtex |
| `interactive` | bool | False | Run in interactive mode |

## Technical Details

**Difficulty:** Medium  
**Dependencies:** Python 3.8+, regex, dateutil  
**Validation:** Citation syntax checked against AMA rules

## References

See `references/` directory for:
- AMA 11th Edition Citation Guidelines
- Format conversion rules
- Example citations by type

## Error Handling

- Returns error message for unparseable citations
- Warns about missing required fields
- Suggests corrections for common format errors
