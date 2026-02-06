---
name: preclinical-pkpd-analyst
description: Calculate PK parameters from blood concentration-time data
version: 1.0.0
category: Pharma
---

# Pre-clinical PK/PD Analyst

Pharmacokinetic analysis automation.

## Use Cases
- IND-enabling studies
- Dose selection
- Drug candidate ranking
- WinNonlin alternative

## Parameters
- `concentration_data`: Time-conc pairs
- `dose`: Administered dose
- `admin_route`: IV/PO/SC

## Returns
- AUC, Cmax, Tmax, T1/2
- Clearance and volume
- Non-compartmental analysis
- PK report template

## Example
Rat PK data → AUC = 1250 ng·h/mL, T1/2 = 4.2h
