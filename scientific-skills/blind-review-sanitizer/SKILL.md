---
name: blind-review-sanitizer
description: One-click removal of author names, affiliations, acknowledgments, and
  excessive self-citations from manuscripts to meet double-blind peer review requirements.
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

# Skill: Blind Review Sanitizer

One-click removal of author names, affiliations, acknowledgments, and excessive self-citations from manuscripts to meet double-blind peer review requirements.

## Features

- **Remove Author Information**: Automatically identify and delete author names, affiliations, contact information
- **Clean Acknowledgments**: Remove Acknowledgments section
- **Self-Citation Detection**: Identify and highlight possible excessive self-citations
- **Supported Formats**: DOCX, TXT, Markdown
- **Preserve Structure**: Maintain original document formatting and layout

## Usage

### Command Line

```bash
openclaw run blind-review-sanitizer --input <input_file> [--output <output_file>] [--authors "Author1,Author2"]
```

### Parameter Description

| Parameter | Description | Required |
|------|------|------|
| `--input` | Input file path (docx/txt/md) | Yes |
| `--output` | Output file path, default adds `-blinded` suffix | No |
| `--authors` | Specify author names (comma-separated) to improve recognition accuracy | No |
| `--keep-acknowledgments` | Keep acknowledgments section | No |
| `--highlight-self-cites` | Only highlight self-citations without deleting | No |

### Usage Examples

```bash
# Basic usage
openclaw run blind-review-sanitizer --input paper.docx

# Specify output file
openclaw run blind-review-sanitizer --input paper.docx --output paper-blinded.docx

# Specify author names
openclaw run blind-review-sanitizer --input paper.docx --authors "Zhang San,Li Si"

# Keep acknowledgments, only highlight self-citations
openclaw run blind-review-sanitizer --input paper.docx --keep-acknowledgments --highlight-self-cites
```

## How It Works

1. **Parse Document**: Use appropriate parser based on file type
2. **Identify Sensitive Information**:
   - Author names (via specification or regex pattern matching)
   - Institution/organization names (universities, research institutes, etc.)
   - Email, phone, address
   - Acknowledgments section titles and content
3. **Process Self-Citations**: Detect patterns like "Author et al.", "our previous work", etc.
4. **Generate Anonymized Document**: Replace sensitive content with `[BLINDED]` or `[AUTHOR NAME]`

## Output Example

Original text:
```
Zhang San¹, Li Si²
¹Tsinghua University Computer Science Department
²Peking University School of Information

*Acknowledgments: Thanks to Professor Wang Wu for guidance...*

As we described in our previous study [1]...
```

After processing:
```
[AUTHOR NAME]¹, [AUTHOR NAME]²
¹[INSTITUTION]
²[INSTITUTION]

[ACKNOWLEDGMENTS REMOVED]

As [BLINDED] described in their previous study [1]...
```

## Dependencies

- Python 3.8+
- python-docx (for DOCX processing)
- Optional: nltk (NLP enhanced recognition)

## Notes

- Manual review is recommended after processing, especially when author names overlap with common words
- Complex document formats may require manual adjustment
- Self-citation detection is based on heuristic rules and may produce false positives

---
ID: 162 | Created: 2026-02-06

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
