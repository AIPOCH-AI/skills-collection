# HIPAA Safe Harbor De-identification Standards

## Overview

The Safe Harbor method is one of two ways to achieve de-identification under the HIPAA Privacy Rule (45 CFR § 164.514(b)). This skill implements the Safe Harbor approach.

## The 18 Identifier Categories

Per HIPAA § 164.514(b)(2), the following identifiers must be removed:

### Direct Identifiers (1-16)
1. Names
2. Geographic data (smaller than state)
3. Dates (except year) related to individual
4. Phone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers
14. Web URLs
15. IP addresses
16. Biometric identifiers

### Quasi-Identifiers (17-18)
17. Full-face photos and comparable images
18. Any other unique identifying numbers, characteristics, or codes

## De-identification Process

### Step 1: Detection
- Pattern matching for structured data (SSN, phone, email)
- NLP entity recognition for names and locations
- Context analysis for date disambiguation

### Step 2: Replacement Strategy
- **Semantic Tokens**: Replace with `[CATEGORY_N]` format
  - Example: "John Smith" → "[PATIENT_NAME_1]"
  - Example: "555-123-4567" → "[PHONE_1]"
- **Consistent Mapping**: Same entity gets same token throughout document
- **Sequential Numbering**: Multiple entities of same type numbered sequentially

### Step 3: Validation
- Regex sweep of output to detect missed patterns
- Confidence threshold filtering
- Manual review flagging for uncertain detections

## Limitations & Expert Determination

### When Safe Harbor May Not Be Sufficient

1. **Rare Diseases**: Patient with rare condition + geographic region may be identifiable
2. **Small Populations**: Unique combinations in small datasets
3. **Longitudinal Data**: Multiple records over time may enable re-identification
4. **Linked Data**: Combination with external datasets

### Expert Determination Alternative

For cases where Safe Harbor is insufficient, HIPAA allows expert determination (§ 164.514(b)(1)):
- Statistical analysis of re-identification risk
- Assessment of data recipient's access to other information
- Documentation of methods and results

## Audit Requirements

Maintain records of:
- De-identification methods used
- Detection confidence scores
- Manual review decisions
- Validation results

## References

- 45 CFR § 164.514 - Other requirements relating to uses and disclosures of protected health information
- HHS Guidance on De-identification: https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
- NIST SP 800-188: De-Identification of Personal Information

## Important Disclaimer

This tool is provided as an aid to HIPAA compliance. It does not constitute legal advice.
Organizations must:
- Validate output through manual review
- Consult legal counsel for compliance decisions
- Document their de-identification procedures
- Consider expert determination for borderline cases
