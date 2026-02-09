---
name: citation-formatter
description: Automatically formats citations to AMA (American Medical Association)
  style. Trigger when user needs to convert, correct, or standardize references in
  academic/medical writing. Handles various input formats including APA, MLA, Vancouver,
  and free-text citations.
version: 1.0.0
category: Research
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

No additional Python packages required.

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
