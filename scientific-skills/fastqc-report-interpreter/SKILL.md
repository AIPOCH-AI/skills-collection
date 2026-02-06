---
name: fastqc-report-interpreter
description: Interpret NGS quality control reports in plain language
version: 1.0.0
category: Bioinfo
---

# FastQC Report Interpreter

NGS QC report translation tool.

## Use Cases
- Novice researcher guidance
- Troubleshooting failed runs
- Data quality assessment
- Pipeline optimization

## Parameters
- `fastqc_data`: QC report content
- `library_type`: DNA/RNA/single-cell

## Returns
- Plain language explanations
- Severity assessment (PASS/WARN/FAIL)
- Actionable recommendations
- Impact on downstream analysis

## Example
"K-mer Content Fail → Adapter contamination detected → Trim adapters"
