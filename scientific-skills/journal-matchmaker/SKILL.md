---
name: journal-matchmaker
description: Recommend suitable high-impact factor or domain-specific journals for
  manuscript submission based on abstract content. Trigger when user provides paper
  abstract and asks for journal recommendations, impact factor matching, or scope
  alignment suggestions.
version: 1.0.0
category: Research
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

# Journal Matchmaker

Analyzes academic paper abstracts to recommend optimal journals for submission, considering impact factors, scope alignment, and domain expertise.

## Use Cases

- Find the best-fit journal for a new manuscript
- Identify high-impact factor journals in specific research areas
- Compare journal scopes against paper content
- Discover domain-specific publication venues

## Usage

```bash
python scripts/main.py --abstract "Your paper abstract text here" [--field "field_name"] [--min-if 5.0] [--count 5]
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--abstract` | str | Yes | - | Paper abstract text to analyze |
| `--field` | str | No | Auto-detect | Research field (e.g., "computer_science", "biology") |
| `--min-if` | float | No | 0.0 | Minimum impact factor threshold |
| `--max-if` | float | No | None | Maximum impact factor (optional) |
| `--count` | int | No | 5 | Number of recommendations to return |
| `--format` | str | No | table | Output format: table, json, markdown |

## Examples

```bash
# Basic usage
python scripts/main.py --abstract "This paper presents a novel deep learning approach..."

# Specify field and minimum impact factor
python scripts/main.py --abstract "abstract.txt" --field "ai" --min-if 10.0 --count 10

# Output as JSON for integration
python scripts/main.py --abstract "..." --format json
```

## How It Works

1. **Abstract Analysis**: Extracts key terms, methodology, and research focus
2. **Field Classification**: Identifies the primary research domain
3. **Journal Matching**: Compares content against journal scopes and aims
4. **Impact Factor Filtering**: Applies IF constraints if specified
5. **Ranking**: Scores and ranks journals by relevance and impact

## Technical Details

- **Difficulty**: Medium
- **Approach**: Keyword extraction + journal database matching
- **Data Source**: Journal metadata from references/journals.json
- **Algorithm**: TF-IDF + cosine similarity for scope matching

## References

- `references/journals.json` - Journal database with impact factors and scopes
- `references/fields.json` - Research field classifications
- `references/scoring_weights.json` - Algorithm tuning parameters

## Notes

- Journal database should be updated periodically (quarterly recommended)
- Impact factor data sourced from Journal Citation Reports (JCR)
- Scope descriptions parsed from official journal websites
- For emerging fields, manual curation may be needed

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

```bash
# Python dependencies
pip install -r requirements.txt
```

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
