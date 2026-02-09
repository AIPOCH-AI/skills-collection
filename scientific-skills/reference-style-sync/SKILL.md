---
name: reference-style-sync
description: One-click synchronization and standardization of reference formats in
  Zotero/EndNote. Automatically fixes metadata errors from web scraping. Supports
  batch processing, format standardization, missing field detection and completion.
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

# Reference Style Sync

One-click synchronization and standardization of reference formats in literature management tools, intelligently fixing metadata errors.

## Overview

Reference Style Sync can:
- Automatically detect and fix erroneous metadata scraped in Zotero/EndNote
- Unify literature formats to standard citation styles (APA, MLA, AMA, Vancouver, etc.)
- Batch process entire literature libraries
- Intelligently complete missing fields (DOI, page numbers, volume/issue, etc.)
- Detect duplicate entries and merge them

## Supported Literature Management Tools

- **Zotero**: Supports RDF, BibTeX, CSL JSON, RIS format export
- **EndNote**: Supports XML, RIS, BibTeX format export
- **Universal Formats**: BibTeX, RIS, CSV, JSON

## Features

### 🔧 Metadata Repair
- Author name format standardization
- Journal name abbreviation/full name unification
- DOI format validation and completion
- Page number format normalization
- Date format unification

### 🎨 Format Sync
- Batch conversion to target citation format
- Field order standardization
- Punctuation unification
- Case normalization

### 🔍 Quality Check
- Missing field detection
- Duplicate entry identification
- Invalid DOI/URL marking
- Journal name spell checking

## Usage

### Command Line Interface

```bash
# Process single file
python scripts/main.py --input library.bib --output fixed.bib --style apa

# Fix metadata and convert to AMA format
python scripts/main.py --input zotero.rdf --output fixed.ris --style ama --fix-metadata

# Batch processing and duplicate detection
python scripts/main.py --input library.json --output cleaned.json --deduplicate --style vancouver

# Quality check only
python scripts/main.py --input library.bib --check-only
```

### Python API

```python
from scripts.main import ReferenceSync

# Initialize
sync = ReferenceSync()

# Load library
sync.load('library.bib')

# Fix metadata
sync.fix_metadata()

# Convert to target format
sync.convert_style(target_style='apa')

# Export
sync.export('output.bib')
```

## Parameter Description

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--input` | str | Required | Input file path (.bib, .ris, .json, .xml) |
| `--output` | str | Required | Output file path |
| `--style` | str | ama | Target format: apa, mla, ama, vancouver, chicago |
| `--fix-metadata` | bool | False | Enable metadata repair |
| `--deduplicate` | bool | False | Detect and merge duplicate entries |
| `--check-only` | bool | False | Check only, no output |
| `--format` | str | auto | Input format auto-detect or specify |

## Repair Rules

### Author Names
```python
# Before repair
Smith, John, Doe, Jane M.
Smith J., Doe J.M.

# After repair (AMA)
Smith J, Doe JM.
```

### Journal Names
```python
# Before repair
journal of the american medical association
J. Am. Med. Assoc.

# After repair
JAMA
```

### DOI
```python
# Before repair
www.doi.org/10.1234/example
doi:10.1234/example
10.1234/example

# After repair
doi:10.1234/example
```

### Page Numbers
```python
# Before repair
123-127
123 -- 127
123–127

# After repair
123-127
```

## Output Example

### Before Repair (Zotero Export)
```
@article{smith2020,
  author = {Smith, John and Doe, Jane M.},
  title = {A Study of Something},
  journal = {journal of clinical medicine},
  year = {2020},
  volume = {15},
  pages = {123-127},
  doi = {10.1234/example}
}
```

### After Repair (AMA Format)
```
@article{smith2020,
  author = {Smith J, Doe JM},
  title = {A Study of Something},
  journal = {J Clin Med},
  year = {2020},
  volume = {15},
  pages = {123-127},
  doi = {doi:10.1234/example}
}
```

## Technical Details

**Difficulty**: Medium  
**Dependencies**: Python 3.8+, regex, titlecase  
**Data Processing**: Supports 10000+ entries batch processing

## Supported Citation Formats

- **AMA**: American Medical Association (11th Edition)
- **APA**: American Psychological Association (7th Edition)
- **MLA**: Modern Language Association (9th Edition)
- **Vancouver**: ICMJE Recommended Format
- **Chicago**: Chicago Manual of Style (17th Edition)
- **IEEE**: Institute of Electrical and Electronics Engineers

## Error Handling

- Invalid file format returns detailed error messages
- Failed parsing entries recorded in error.log
- Partial failure supports breakpoint resume
- Large files automatically processed in chunks

## Notes

1. It is recommended to backup the original library before processing
2. Metadata repair is based on built-in rule library; complex cases may require manual review
3. Journal abbreviations follow ISO 4 standard
4. DOI validation uses regex patterns, does not actually resolve and verify

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
