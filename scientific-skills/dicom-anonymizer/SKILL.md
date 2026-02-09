---
name: dicom-anonymizer
description: Batch anonymize DICOM medical images by removing patient sensitive information
  (name, ID, birth date) while preserving image data for research use. Trigger when
  users need to de-identify medical imaging data, prepare DICOM files for research
  sharing, or remove PHI from radiology/scanned images.
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

# DICOM Anonymizer

A clinical-grade tool for batch anonymization of DICOM medical images, removing patient identifiable information while preserving essential imaging data for research and analysis.

## Overview

This skill anonymizes DICOM (Digital Imaging and Communications in Medicine) files by removing or replacing Protected Health Information (PHI) while maintaining the integrity of the medical image data. It supports batch processing of entire directories and generates audit logs for compliance documentation.

## Features

- **Batch Processing**: Process single files or entire directories recursively
- **18 PHI Tags Anonymized**: Patient name, ID, birth date, institution, physician, etc.
- **Configurable Anonymization**: Choose between removal, hashing, or replacement strategies
- **Study Linkage Preservation**: Option to maintain study/series relationships using pseudonyms
- **Audit Trail**: Complete logging of all anonymization actions
- **HIPAA Safe Harbor Compliant**: Meets de-identification standards for research use

## Usage

### Command Line

```bash
# Anonymize a single file
python scripts/main.py --input patient_scan.dcm --output anonymized.dcm

# Batch process a directory
python scripts/main.py --input /path/to/dicom/folder/ --output /path/to/output/ --batch

# Preserve study relationships with pseudonyms
python scripts/main.py --input scans/ --output clean/ --batch --preserve-studies

# Custom anonymization (keep age, remove birth date)
python scripts/main.py --input scan.dcm --output clean.dcm --keep-tags PatientAge
```

### Python API

```python
from scripts.main import DICOMAnonymizer

anonymizer = DICOMAnonymizer(preserve_studies=True)
result = anonymizer.anonymize_file("input.dcm", "output.dcm")
print(f"Tags anonymized: {len(result.anonymized_tags)}")

# Batch processing
results = anonymizer.anonymize_directory("input_folder/", "output_folder/")
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input`, `-i` | string | required | Input DICOM file or directory path |
| `--output`, `-o` | string | required | Output DICOM file or directory path |
| `--batch`, `-b` | flag | false | Enable batch/directory processing |
| `--preserve-studies` | flag | false | Maintain study relationships with pseudonyms |
| `--keep-tags` | string | - | Comma-separated list of tags to preserve |
| `--remove-private` | flag | true | Remove private/unknown tags |
| `--audit-log` | string | - | Path for JSON audit log |
| `--overwrite` | flag | false | Overwrite existing output files |

## Anonymized DICOM Tags

The following PHI tags are anonymized by default:

### Patient Information
| Tag | Attribute | Action |
|-----|-----------|--------|
| (0010,0010) | PatientName | Removed / Replaced |
| (0010,0020) | PatientID | Hashed / Pseudonym |
| (0010,0030) | PatientBirthDate | Removed |
| (0010,0040) | PatientSex | Preserved (demographic research) |
| (0010,1010) | PatientAge | Preserved (calculated from birth date) |
| (0010,1020) | PatientSize | Preserved |
| (0010,1030) | PatientWeight | Preserved |

### Institution & Provider
| Tag | Attribute | Action |
|-----|-----------|--------|
| (0008,0080) | InstitutionName | Removed |
| (0008,0081) | InstitutionAddress | Removed |
| (0008,0090) | ReferringPhysicianName | Removed |
| (0008,1048) | PhysiciansOfRecord | Removed |
| (0008,1050) | PerformingPhysicianName | Removed |
| (0008,1060) | NameOfPhysiciansReadingStudy | Removed |
| (0008,1070) | OperatorsName | Removed |

### Study & Series
| Tag | Attribute | Action |
|-----|-----------|--------|
| (0008,0050) | AccessionNumber | Hashed / Removed |
| (0020,0010) | StudyID | Hashed (if preserve-studies) |
| (0020,000D) | StudyInstanceUID | Hashed (if preserve-studies) |
| (0020,000E) | SeriesInstanceUID | Hashed (if preserve-studies) |
| (0020,4000) | ImageComments | Removed |

### Device & Acquisition
| Tag | Attribute | Action |
|-----|-----------|--------|
| (0018,1030) | ProtocolName | Preserved / Anonymized |
| (0018,1000) | DeviceSerialNumber | Removed |
| (0008,1010) | StationName | Removed |
| (0008,0018) | SOPInstanceUID | Regenerated |

## Output Format

### Anonymized DICOM File
- Original PHI tags replaced with empty values, "ANONYMOUS", or hashed pseudonyms
- Image pixel data (7FE0,0010) preserved unchanged
- Essential metadata (modality, dimensions, acquisition params) preserved

### Audit Log JSON
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "input_file": "/path/to/original.dcm",
  "output_file": "/path/to/anonymized.dcm",
  "original_patient_id_hash": "sha256:abc123...",
  "pseudonym": "ANON_0001",
  "tags_anonymized": [
    {"tag": "(0010,0010)", "attribute": "PatientName", "action": "cleared"},
    {"tag": "(0010,0020)", "attribute": "PatientID", "action": "hashed"},
    {"tag": "(0010,0030)", "attribute": "PatientBirthDate", "action": "cleared"}
  ],
  "statistics": {
    "total_tags_processed": 150,
    "phi_tags_removed": 12,
    "private_tags_removed": 5,
    "image_data_preserved": true
  }
}
```

## Technical Architecture

1. **DICOM Loading**: Use pydicom to read DICOM files with validation
2. **Tag Analysis**: Identify and categorize PHI-containing tags
3. **Anonymization Engine**: Apply configured anonymization rules per tag
4. **UID Handling**: Regenerate or hash UIDs to maintain/break linkage
5. **Private Tag Removal**: Strip manufacturer-specific private tags
6. **Validation**: Verify output is valid DICOM and image data intact
7. **Audit Logging**: Record all transformations for compliance

## Dependencies

- Python 3.9+
- pydicom >= 2.3.0 (DICOM file handling)
- cryptography >= 3.0 (for secure hashing, optional)

See `references/requirements.txt` for full dependency list.

## Limitations & Warnings

⚠️ **CRITICAL**: This tool is designed as a helper, not a replacement for institutional review.

- **Burned-in Annotations**: Text/annotations "burned into" the image pixels are NOT removed. Pre-process with OCR-based tools if needed.
- **Structured Reports**: DICOM SR (Structured Reporting) files may contain PHI in narrative text that may not be fully detected.
- **Private Tags**: Some private tags may contain PHI in non-standard formats.
- **Secondary Captures**: Scanned documents/images may have PHI visible in the pixel data.
- **Always perform manual QA** on output before research release.
- **AI Autonomous Acceptance Status**: 需人工检查 (Requires Manual Review)

## References

- `references/dicom_standard_ps3.15.pdf` - DICOM Standard Part 15: Security and System Management
- `references/hipaa_deidentification_guide.pdf` - HIPAA Safe Harbor de-identification standards
- `references/phi_tags.json` - Complete list of PHI-related DICOM tags
- `references/requirements.txt` - Python dependencies

## Technical Difficulty: High

Complex DICOM data structures, UID management, regulatory compliance requirements, potential pixel-data PHI.

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
