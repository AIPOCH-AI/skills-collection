# Clinical Summarization Guidelines

## Overview

This document provides guidelines for EHR (Electronic Health Record) summarization using the EHR Semantic Compressor.

## Input Requirements

### Minimum Length
- EHR documents must contain at least 100 words
- Optimal input: 1600+ words for meaningful compression

### Text Format
- Plain text or JSON format accepted
- UTF-8 encoding required
- Medical abbreviations should be expanded for best results

## Output Specifications

### Summary Format
- Bullet-point format for readability
- 200-300 words by default (configurable)
- Organized by clinical relevance

### Extracted Sections

#### Allergies
Extracts information about:
- Drug allergies
- Food allergies
- Environmental allergies
- Adverse reactions

#### Medications
Extracts information about:
- Current medications
- Dosages
- Frequency
- Prescribed treatments

#### Diagnoses
Extracts information about:
- Current diagnoses
- Past medical history
- Chronic conditions
- Acute conditions

#### Family History
Extracts information about:
- Hereditary conditions
- Family member health status
- Genetic predispositions

#### Procedures
Extracts information about:
- Surgeries
- Medical procedures
- Treatments performed

#### Vitals
Extracts information about:
- Blood pressure readings
- Heart rate
- Temperature
- Respiratory rate
- Other measurements

## Best Practices

### Input Preparation
1. Remove identifying information if de-identification is required
2. Ensure text is properly formatted
3. Check for encoding issues

### Output Review
1. Verify clinical accuracy
2. Check for missing critical information
3. Ensure proper formatting

### Performance Optimization
- Processing time: 10-20 seconds for standard documents
- Memory usage: ~2GB RAM
- Supports batch processing via scripting

## Error Handling

### Common Issues

**Input Too Short**
- Error: "EHR text is too short"
- Solution: Provide more complete documentation

**Invalid JSON**
- Error: "Invalid JSON input format"
- Solution: Check JSON syntax

**Missing Required Fields**
- Error: "Missing required field: ehr_text"
- Solution: Include ehr_text in input

## Safety Considerations

- All processing is performed locally
- No patient data is transmitted externally
- No API keys or credentials required
- Suitable for protected health information (PHI) environments

## Technical Notes

### Algorithm
- Uses extractive summarization with clinical relevance scoring
- Rule-based section extraction with keyword matching
- Sentence scoring based on medical terminology

### Limitations
- Requires sufficient input length for meaningful results
- Section extraction depends on keyword presence
- Does not perform medical interpretation or diagnosis
