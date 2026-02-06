---
name: sds-msds-risk-scanner
description: Extract hazard codes and safety info from chemical safety datasheets
version: 1.0.0
category: Safety
---

# SDS/MSDS Risk Scanner

Chemical safety data extraction.

## Use Cases
- Lab safety training
- Hazard communication
- Emergency response
- Compliance documentation

## Parameters
- `sds_document`: PDF or text input
- `chemical_name`: Compound name

## Returns
- H-codes (hazard statements)
- P-codes (precautionary statements)
- Safety summary card
- PPE recommendations

## Example
Acetone → H225, H319, H336 → Flammable, irritant
