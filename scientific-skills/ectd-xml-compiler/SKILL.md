---
name: ectd-xml-compiler
description: Convert drug application documents (Word/PDF) into FDA/EMA compliant
  eCTD XML structure
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

# eCTD XML Compiler

ID: 197

Automatically convert uploaded drug application documents (Word/PDF) into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.

## Overview

eCTD (electronic Common Technical Document) is the electronic Common Technical Document standard established by ICH for submitting drug registration applications to regulatory agencies such as FDA and EMA.

This tool parses uploaded drug application documents (Word/PDF) and converts them into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.

## eCTD Structure

```
eCTD/
├── m1/  # Module 1: Administrative Information and Prescribing Information (region-specific)
│   ├── m1.xml
│   └── ...
├── m2/  # Module 2: CTD Summaries
│   ├── m2.xml
│   └── ...
├── m3/  # Module 3: Quality
│   ├── m3.xml
│   └── ...
├── m4/  # Module 4: Nonclinical Study Reports
│   ├── m4.xml
│   └── ...
├── m5/  # Module 5: Clinical Study Reports
│   ├── m5.xml
│   └── ...
├── index.xml      # Master index file
├── index-md5.txt  # MD5 checksum file
└── dtd/           # DTD files
```

## Usage

```bash
python skills/ectd-xml-compiler/scripts/main.py [options] <input_files...>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input_files` | Input Word/PDF file paths (supports multiple) |

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output directory path | `./ectd-output` |
| `--module` | `-m` | Target module (m1-m5, auto) | `auto` |
| `--region` | `-r` | Target region (FDA, EMA, ICH) | `ICH` |
| `--version` | `-v` | eCTD version (3.2.2, 4.0) | `4.0` |
| `--dtd-path` | `-d` | Custom DTD path | Built-in DTD |
| `--validate` |  | Validate generated XML | `False` |

### Examples

```bash
# Basic usage - auto-detect module
python skills/ectd-xml-compiler/scripts/main.py document1.docx document2.pdf

# Specify output directory and module
python skills/ectd-xml-compiler/scripts/main.py -o ./my-ectd -m m3 quality-doc.docx

# FDA submission format
python skills/ectd-xml-compiler/scripts/main.py -r FDA -v 3.2.2 *.pdf

# Validate generated XML
python skills/ectd-xml-compiler/scripts/main.py --validate submission.pdf
```

## Input Document Processing

### Supported Formats
- Microsoft Word (.docx, .doc)
- PDF (.pdf)

### Document Parsing Logic
1. **Title Recognition**: Extract heading hierarchy based on font size and style
2. **TOC Mapping**: Auto-recognize section numbers (e.g., 3.2.S.1.1)
3. **Metadata Extraction**: Extract author, date, version, and other information
4. **Content Classification**: Map to corresponding eCTD modules based on keyword matching

### Module Auto-Recognition Rules

| Keyword Pattern | Target Module |
|------------|----------|
| Administrative, Label, Package Insert | m1 |
| Summary, summary, Overview | m2 |
| Quality, quality, CMC, API, Drug Product | m3 |
| Nonclinical, Toxicology, Pharmacokinetics | m4 |
| Clinical, clinical, Study, Trial | m5 |

## Output Structure

Generated eCTD skeleton contains:

### index.xml
Master index file containing references and sequence information for all modules.

### Module XML (m1.xml - m5.xml)
XML skeleton for each module, containing:
- Document hierarchy structure (`<leaf>`, `<node>`)
- Cross-references (`<cross-reference>`)
- Attribute definitions (ID, version, operation type)

### MD5 Checksums
MD5 checksum values for each file to ensure integrity.

## Dependencies

```
python-docx>=0.8.11    # Word document parsing
PyPDF2>=3.0.0          # PDF text extraction
lxml>=4.9.0            # XML processing
```

## Installation

```bash
# Install dependencies
pip install python-docx PyPDF2 lxml
```

## Validation

Using `--validate` option can validate generated XML:
- DTD structure validation
- Required elements and attributes check
- Cross-reference integrity check

## References

- [ICH eCTD Specification v4.0](https://www.ich.org/page/ectd)
- [FDA eCTD Guidance](https://www.fda.gov/drugs/electronic-regulatory-submission-and-review/ectd-technical-conformance-guide)
- [EMA eCTD Requirements](https://www.ema.europa.eu/en/human-regulatory/marketing-authorisation/application-procedures/electronic-application-forms)

## License

MIT License

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
