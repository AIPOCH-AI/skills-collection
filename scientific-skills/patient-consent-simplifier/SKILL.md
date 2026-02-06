---
name: patient-consent-simplifier
description: Rewrite legal-jargon consent forms to 5th-grade reading level
trigger: consent, patient, simplify, readability, IRB
tier: C
---

# Patient Consent Simplifier

Rewrite legally-dense informed consent forms to 5th-grade reading level for patient comprehension.

## Usage

```bash
python scripts/main.py --input consent_form.pdf --output simple_consent.txt
python scripts/main.py --text "You hereby authorize..." --simplify
```

## Parameters

- `--input`: Input consent form (PDF/TXT/DOCX)
- `--text`: Direct text input
- `--output`: Output file
- `--target-grade`: Target reading grade (default: 5)

## Features

- Simplifies medical/legal terminology
- Shortens complex sentences
- Adds explanatory notes
- Maintains legal accuracy

## Output

- Simplified consent form
- Readability score before/after
- List of key terms explained
