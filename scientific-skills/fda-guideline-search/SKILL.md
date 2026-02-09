---
name: fda-guideline-search
description: 'Search FDA industry guidelines by therapeutic area or topic.

  Trigger when user requests FDA guidance documents, regulatory guidelines,

  or asks about FDA requirements for specific disease areas, drug development,

  or therapeutic categories (e.g., oncology, cardiology, rare diseases).

  Also triggered by queries about FDA ICH guidelines, FDA guidance documents,

  or regulatory compliance requirements.'
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# FDA Guideline Search

Quickly search and retrieve FDA industry guidelines by therapeutic area.

## Features

- Search FDA guidelines by therapeutic area (oncology, cardiology, neurology, etc.)
- Filter by document type (draft, final, ICH guidelines)
- Download and cache guideline documents
- Search within document content

## Usage

### Python Script

```bash
python scripts/main.py --area <therapeutic_area> [options]
```

### Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--area` | Therapeutic area (e.g., oncology, cardiology, rare-disease) | Yes |
| `--type` | Document type: all, draft, final, ich | No (default: all) |
| `--year` | Filter by year (e.g., 2023, 2020-2024) | No |
| `--download` | Download PDF to local cache | No |
| `--search` | Search term within documents | No |
| `--limit` | Max results (1-100) | No (default: 20) |

### Examples

```bash
# Search oncology guidelines
python scripts/main.py --area oncology

# Search for rare disease draft guidelines
python scripts/main.py --area "rare disease" --type draft

# Search with download
python scripts/main.py --area cardiology --download --limit 10
```

## Technical Details

- **Source**: FDA CDER/CBER Guidance Documents Database
- **API**: FDA Open Data / Web scraping with rate limiting
- **Cache**: Local PDF storage in `references/cache/`
- **Difficulty**: Medium

## Output Format

Results are returned as structured JSON:

```json
{
  "query": {
    "area": "oncology",
    "type": "all",
    "limit": 20
  },
  "total_found": 45,
  "guidelines": [
    {
      "title": "Clinical Trial Endpoints for the Approval of Cancer Drugs...",
      "document_number": "FDA-2020-D-0623",
      "issue_date": "2023-03-15",
      "type": "Final",
      "therapeutic_area": "Oncology",
      "pdf_url": "https://www.fda.gov/.../guidance.pdf",
      "local_path": "references/cache/..."
    }
  ]
}
```

## References

- [FDA Search Strategy](./references/search-strategy.md)
- [Therapeutic Area Mappings](./references/area-mappings.json)
- [FDA API Documentation](./references/fda-api-notes.md)

## Limitations

- Rate limited to 10 requests/minute to respect FDA servers
- Some historical documents may not have digital PDFs
- ICH guidelines require separate search scope

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
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
