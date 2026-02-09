---
name: data-management-plan-creator
description: Automatically generate NIH 2023-compliant Data Management and Sharing
  Plan (DMSP) drafts following FAIR principles
version: 1.0.0
category: General
tags:
- NIH
- DMP
- DMSP
- FAIR
- research-data
- compliance
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Data Management Plan (DMP) Creator

Automatically generate draft Data Management and Sharing Plans (DMSP) compliant with NIH 2023 policy requirements and FAIR principles.

## Overview

This Skill generates comprehensive Data Management and Sharing Plans (DMSP) that meet NIH's 2023 Final Policy for Data Management and Sharing. The output follows FAIR principles (Findable, Accessible, Interoperable, Reusable) to ensure research data is properly managed and shared.

## Requirements

- Python 3.8+
- No external dependencies required (uses standard library only)

## Usage

### Command Line

```bash
python scripts/main.py \
    --project-title "Your Research Project Title" \
    --pi-name "Principal Investigator Name" \
    --data-types "genomic,imaging,clinical" \
    --repository "GEO,Figshare" \
    --output dmsp_draft.md
```

### Interactive Mode

```bash
python scripts/main.py --interactive
```

### As a Module

```python
from scripts.main import DMSPCreator

creator = DMSPCreator(
    project_title="Cancer Genomics Study",
    pi_name="Dr. Jane Smith",
    institution="National Cancer Institute",
    data_types=["genomic sequencing", "clinical metadata"],
    estimated_size_gb=500,
    repositories=["dbGaP", "GEO"],
    sharing_timeline="6 months after study completion"
)

dmsp = creator.generate_plan()
creator.save_to_file("dmsp_output.md")
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--project-title` | string | Yes | Title of the research project |
| `--pi-name` | string | Yes | Name of the Principal Investigator |
| `--institution` | string | Yes | Research institution or organization |
| `--data-types` | string | Yes | Comma-separated list of data types (e.g., "genomic,imaging,clinical") |
| `--estimated-size` | float | No | Estimated data size in GB |
| `--repository` | string | Yes | Comma-separated list of target repositories |
| `--sharing-timeline` | string | No | When data will be shared (default: "No later than the end of the award period") |
| `--access-restrictions` | string | No | Any access restrictions (e.g., "controlled-access for sensitive data") |
| `--format-standards` | string | No | Data format standards to be used |
| `--output` | string | No | Output file path (default: dmsp_[timestamp].md) |
| `--interactive` | flag | No | Run in interactive mode |

## NIH DMSP Required Elements

The generated plan addresses all six required elements per NIH policy:

1. **Data Type** - Types and estimated amount of scientific data
2. **Related Tools, Software and/or Code** - Tools needed to access/manipulate data
3. **Standards** - Standards for data/metadata to be applied
4. **Data Preservation, Access, and Associated Timelines** - Repository selection and sharing timeline
5. **Access, Distribution, or Reuse Considerations** - Factors affecting subsequent access
6. **Oversight of Data Management and Sharing** - Plans for compliance monitoring

## FAIR Principles Implementation

### Findable
- Persistent identifiers (DOIs)
- Rich metadata with standard vocabularies
- Registration in searchable repositories

### Accessible
- Standardized communication protocols
- Metadata available even if data is no longer available
- Access procedures clearly documented

### Interoperable
- Standard data formats
- Standard terminologies and vocabularies
- Qualified references to other data

### Reusable
- Detailed provenance information
- Clear usage licenses
- Domain-relevant community standards

## Example Output

The generated DMSP includes:
- Executive summary
- NIH-compliant section headers
- Specific language for data type descriptions
- FAIR-aligned metadata standards
- Repository recommendations
- Timeline for data sharing
- Access control procedures
- Roles and responsibilities

## References

- [NIH Data Management and Sharing Policy](https://sharing.nih.gov/data-management-and-sharing-policy)
- [NIH DMSP Template](references/nih_dmp_template.md)
- [FAIR Principles](https://www.go-fair.org/fair-principles/)

## License

MIT License - See project root for details.

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
