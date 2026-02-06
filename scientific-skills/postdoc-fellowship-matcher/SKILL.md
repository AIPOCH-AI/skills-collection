---
name: postdoc-fellowship-matcher
description: Match postdoc applicants to eligible fellowships based on nationality and research area
trigger: postdoc, fellowship, eligibility, match, funding
tier: C
---

# Postdoc Fellowship Matcher

Filter postdoctoral fellowships based on applicant nationality, years since PhD, and research area.

## Usage

```bash
python scripts/main.py --nationality US --years-post-phd 1 --field "immunology"
```

## Parameters

- `--nationality`: Applicant nationality
- `--years-post-phd`: Years since PhD completion
- `--field`: Research field
- `--institution`: Current/potential institution

## Fellowship Database

- NIH F32
- NSF Postdoctoral Fellowships
- HFSP Fellowship
- EMBO Fellowship
- Marie Curie Fellowships
- Schmidt Science Fellows

## Output

- Eligible fellowships list
- Deadlines and requirements
- Success rate estimates
