---
name: nih-biosketch-builder
description: Generate NIH Biosketch documents compliant with the 2022 OMB-approved
  format
version: 1.0.0
category: Grant
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# NIH Biosketch Builder

**ID**: 101  
**Version**: 1.0.0  
**NIH Format**: 2022 OMB-approved version

## Functions

Automatically generate NIH Biosketch documents in the 2022 format for NIH grant applications.

## NIH Biosketch Format Requirements (2022 Version)

### Required Sections
1. **Personal Statement** - Personal statement (max 1 page)
2. **Positions and Honors** - Positions and honors
3. **Contributions to Science** - Scientific contributions (max 4 items)
4. **Research Support** - Research support (optional)

### Format Specifications
- Page count: No more than 5 pages
- Fonts: Arial, Helvetica, Palatino Linotype, or Georgia, ≥11pt
- Margins: ≥0.5 inches
- Line spacing: Single or double

## Usage

### Command Line
```bash
python skills/nih-biosketch-builder/scripts/main.py --input data.json --output biosketch.docx
```

### Input Data Format (JSON)
```json
{
  "personal_info": {
    "name": "Zhang San",
    "position": "Associate Professor",
    "department": "Department of Biology",
    "organization": "University of Example",
    "email": "zhang.san@example.edu"
  },
  "personal_statement": "Your personal statement text here...",
  "positions_and_honors": [
    {"year": "2020-present", "position": "Associate Professor", "institution": "University of Example"}
  ],
  "contributions": [
    {
      "title": "Breakthrough in Cancer Research",
      "description": "Detailed description of contribution...",
      "publications": ["PMID:12345678", "DOI:10.1000/example"]
    }
  ],
  "research_support": [
    {"title": "R01 Grant", "agency": "NIH", "period": "2021-2026", "amount": "$1,500,000"}
  ]
}
```

### SCI Paper Auto-import
```bash
# Automatically retrieve paper information via PMID
python skills/nih-biosketch-builder/scripts/main.py --import-pubmed "12345678,23456789" --output publications.json

# Auto-fill into biosketch
python skills/nih-biosketch-builder/scripts/main.py --input data.json --auto-import-pubmed --output biosketch.docx
```

## Dependencies

- Python 3.8+
- python-docx
- requests (for PubMed API)

Install dependencies:
```bash
pip install python-docx requests
```

## Output Format

Generate DOCX file in NIH official template format, ready to use for grant applications.

## References

- [NIH Biosketch Format Instructions](https://grants.nih.gov/grants/forms/biosketch.htm)
- [SciENcv](https://www.ncbi.nlm.nih.gov/sciencv/) - NIH official tool

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
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
