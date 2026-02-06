# CDISC SDTM Implementation Guide Reference

## Overview

The Study Data Tabulation Model (SDTM) is a standard for organizing and formatting data to streamline processes in collection, management, analysis and reporting.

## Key Domains

### DM - Demographics
Contains demographic information about study subjects.

**Required Fields:**
- STUDYID: Study Identifier
- USUBJID: Unique Subject Identifier
- SUBJID: Subject Identifier for the Study
- RFSTDTC: Subject Reference Start Date/Time
- RFENDTC: Subject Reference End Date/Time
- SITEID: Study Site Identifier
- AGE: Age
- SEX: Sex
- RACE: Race

### LB - Laboratory Test Results
Contains laboratory test results including chemistry, hematology, urinalysis.

**Required Fields:**
- STUDYID: Study Identifier
- USUBJID: Unique Subject Identifier
- LBTESTCD: Lab Test Short Name
- LBCAT: Category for Lab Test
- LBORRES: Result or Finding in Original Units
- LBORRESU: Original Units
- LBSTRESC: Character Result/Finding in Std Format
- LBDTC: Date/Time of Specimen Collection

### VS - Vital Signs
Contains vital signs measurements like blood pressure, heart rate, temperature.

**Required Fields:**
- STUDYID: Study Identifier
- USUBJID: Unique Subject Identifier
- VSTESTCD: Vital Signs Test Short Name
- VSORRES: Result or Finding in Original Units
- VSORRESU: Original Units
- VSSTRESC: Character Result/Finding in Std Format
- VSDTC: Date/Time of Vital Signs

## Data Quality Requirements

1. **Missing Values**: Must be coded as empty, not as text like "NA" or "N/A"
2. **Dates**: ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
3. **Coded Values**: Use controlled terminology
4. **Units**: Standardize to conventional units

## References

- CDISC SDTM Implementation Guide v3.4
- CDISC Controlled Terminology
- FDA Study Data Technical Conformance Guide
