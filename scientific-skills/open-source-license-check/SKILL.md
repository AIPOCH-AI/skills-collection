---
name: open-source-license-check
description: Check if bioinformatics software/code licenses allow commercial use
trigger: license, open source, GPL, MIT, commercial, compliance
tier: C
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
