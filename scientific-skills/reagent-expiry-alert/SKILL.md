---
name: reagent-expiry-alert
description: Scan reagent barcodes, log expiry dates, and alert before expiration
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# Reagent Expiry Alert

Scan reagent bottle barcodes/QR codes, log expiration dates, and alert before expiry.

## Usage

```bash
python scripts/main.py --scan "REAGENT-001" --expiry 2025-12-31
python scripts/main.py --check-alerts
```

## Parameters

- `--scan`: Reagent barcode/ID
- `--expiry`: Expiration date (YYYY-MM-DD)
- `--check-alerts`: Check for upcoming expirations
- `--alert-days`: Days before expiry to alert (default: 30)

## Features

- Barcode/QR code scanning support
- Automatic expiry date logging
- Multi-level alerts (30/60/90 days)
- Inventory tracking

## Output

- Expiration alerts
- Inventory report
- Reorder recommendations

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

No additional Python packages required.

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
