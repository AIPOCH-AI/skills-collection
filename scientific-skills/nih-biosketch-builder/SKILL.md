---
name: nih-biosketch-builder
description: Generate NIH Biosketch documents compliant with the 2022 OMB-approved format
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
