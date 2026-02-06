---
name: fda-guideline-search
description: |
  Search FDA industry guidelines by therapeutic area or topic.
  Trigger when user requests FDA guidance documents, regulatory guidelines,
  or asks about FDA requirements for specific disease areas, drug development,
  or therapeutic categories (e.g., oncology, cardiology, rare diseases).
  Also triggered by queries about FDA ICH guidelines, FDA guidance documents,
  or regulatory compliance requirements.
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
