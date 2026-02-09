---
name: open-source-license-check
description: Check if bioinformatics software/code licenses allow commercial use
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

# Open Source License Check

Check if referenced bioinformatics software/code licenses allow commercial use (GPL vs MIT, etc.).

## Usage

```bash
python scripts/main.py --software "samtools,bwa,bedtools"
python scripts/main.py --check-requirements requirements.txt
```

## Parameters

- `--software`: Comma-separated software names
- `--check-requirements`: Check Python requirements file
- `--check-directory`: Scan directory for license files

## License Types

| License | Commercial Use | Notes |
|---------|---------------|-------|
| MIT | ✅ Yes | Permissive |
| Apache-2.0 | ✅ Yes | Permissive |
| BSD | ✅ Yes | Permissive |
| GPL-3.0 | ⚠️ Copyleft | Must open source derivative |
| GPL-2.0 | ⚠️ Copyleft | Must open source derivative |
| AGPL | ❌ No | Network use is distribution |

## Output

- License compatibility report
- Commercial use warnings
- Compliance recommendations

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
