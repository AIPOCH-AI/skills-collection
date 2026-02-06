---
name: lay-press-release-writer
description: Transform academic papers into university press releases for general audiences and media
---

# Lay Press Release Writer

## Metadata
- **ID**: 144
- **Name**: Lay Press Release Writer
- **Description**: Transform academic papers into university press center style press releases
- **Version**: 1.0.0
- **Author**: OpenClaw
- **Entry Point**: scripts/main.py

## Purpose
Transforms complex academic papers into press releases for general audiences, alumni, and media. Maintains scientific accuracy while conveying research highlights and value in accessible language.

## Capabilities
- Extracts core findings and innovation points from papers
- Generates press releases in university press center style
- Adds compelling headlines and leads
- Provides researcher quotes
- Includes relevant background information

## Input Parameters

| Parameter Name | Type | Required | Description |
|--------|------|------|------|
| `paper_text` | string | Yes | Full paper text or abstract text |
| `paper_title` | string | No | Paper title |
| `authors` | array | No | Author list |
| `institution` | string | No | Institution/University name |
| `publication_venue` | string | No | Publication journal/conference name |
| `target_audience` | string | No | Target audience (general/alumni/media) |
| `tone` | string | No | Tone style (formal/friendly/inspiring) |

## Output Format

Returns JSON format:
```json
{
  "headline": "Compelling Headline",
  "subheadline": "Subheadline",
  "dateline": "Location, Date",
  "lead": "Lead paragraph",
  "body": "Body content",
  "quotes": ["Researcher quote 1", "Researcher quote 2"],
  "boilerplate": "Institution introduction",
  "media_contact": "Media contact information"
}
```

## Usage

```bash
python scripts/main.py --paper-text "Paper content..." --institution "XX University"
```

## Dependencies
- Python 3.8+
- Dependencies see requirements.txt

## Examples

### Example 1: Basic Usage
```bash
python scripts/main.py \
  --paper-text "..." \
  --paper-title "New Breakthrough in Quantum Computing" \
  --institution "Tsinghua University" \
  --authors "Zhang San,Li Si"
```

## Notes
- Generated content should maintain scientific accuracy
- Avoid oversimplification that leads to misunderstanding
- Highlight practical application value of research
- Comply with standard press release structure (inverted pyramid structure)
