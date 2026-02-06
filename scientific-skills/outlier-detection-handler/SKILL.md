---
name: outlier-detection-handler
description: Statistical outlier identification and handling recommendations
version: 1.0.0
category: Data
---

# Outlier Detection & Handling

Identify and manage statistical outliers.

## Use Cases
- Data quality control
- Pre-analysis screening
- Regulatory compliance (FDA data integrity)

## Parameters
- `data`: Dataset to analyze
- `method`: 3-sigma, IQR, or Grubbs test
- `action`: Flag, remove, or winsorize

## Returns
- Outlier flagging with method details
- Handling recommendations
- Documentation for regulatory submission

## Example
Input: Biomarker measurements from 200 patients
Output: 5 outliers identified (2.5%), recommended action: investigate then winsorize
