---
name: bio-ontology-mapper
description: Map unstructured biomedical data (symptoms, diseases, procedures) to
  standardized SNOMED CT or MeSH vocabulary. Trigger when user needs to normalize
  medical terms, convert clinical notes to ontology codes, or standardize biomedical
  terminology.
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Bio-Ontology Mapper

Map unstructured biomedical text to standardized ontologies (SNOMED CT / MeSH).

## Function

- Extract medical entities from free text
- Map terms to SNOMED CT concepts (clinical terminology)
- Map terms to MeSH descriptors (biomedical indexing)
- Provide confidence scores for mappings
- Handle synonyms and lexical variants

## Technical Difficulty

**High** - Requires understanding of biomedical NLP, ontology structures, and fuzzy matching algorithms.

## Usage

```bash
# Map single term
python scripts/main.py --term "myocardial infarction" --ontology snomed

# Map from file
python scripts/main.py --input clinical_notes.txt --output mapped_terms.json --ontology mesh

# Batch processing with confidence threshold
python scripts/main.py --input terms.csv --threshold 0.8 --format json
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--term` | string | - | Single term to map |
| `--input` | path | - | Input file with terms |
| `--output` | path | stdout | Output file path |
| `--ontology` | enum | both | Target: `snomed`, `mesh`, or `both` |
| `--threshold` | float | 0.7 | Minimum confidence score (0-1) |
| `--format` | enum | json | Output format: `json`, `csv`, `tsv` |
| `--language` | string | en | Source language (en, zh, etc.) |

## Output Format

```json
{
  "input": "heart attack",
  "mappings": [
    {
      "ontology": "SNOMED CT",
      "concept_id": "22298006",
      "term": "Myocardial infarction",
      "confidence": 0.95,
      "semantic_tag": "disorder"
    },
    {
      "ontology": "MeSH",
      "descriptor_id": "D009203",
      "term": "Myocardial Infarction",
      "confidence": 0.92,
      "tree_numbers": ["C14.907.489.500"]
    }
  ]
}
```

## Dependencies

- Python 3.8+
- `requests` - API calls to ontology services
- `fuzzywuzzy` or `rapidfuzz` - String similarity matching
- `spacy` or `transformers` - Optional NER preprocessing

## Implementation Notes

1. **No hardcoded API keys** - Configure via environment variables
2. **Offline mode** - Uses local reference files when APIs unavailable
3. **Rate limiting** - Built-in delays for external API calls
4. **Caching** - Results cached to reduce redundant lookups

## Reference Files

- `references/snomed_sample.json` - Sample SNOMED CT mappings
- `references/mesh_sample.json` - Sample MeSH mappings
- `references/synonyms.json` - Common term synonyms

## Limitations

- Requires internet for full SNOMED CT/MeSH lookups
- Large ontologies may require local database setup
- Best effort matching for ambiguous abbreviations

## Safety & Compliance

- **Do not** use for clinical decision-making without expert review
- **Do not** process PHI (Protected Health Information)
- Results should be validated by domain experts

## Version

- Created: 2026-02-05
- Status: Requires human review

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
