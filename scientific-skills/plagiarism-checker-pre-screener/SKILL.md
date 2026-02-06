---
name: plagiarism-checker-pre-screener
description: |
  Use when: User provides text/document and asks to check originality, 
  detect plagiarism, assess similarity, or rewrite high-duplicate content.
  Triggers: "check plagiarism", "originality check", "similarity detection",
  "改写重复内容", "降重", "查重", "原创性检测", "抄袭检查"
  Input: Text content or document (txt, md, docx support via text extraction)
  Output: Originality score, highlighted duplicate/similar paragraphs, paraphrasing suggestions
---

# Plagiarism Checker Pre-Screener

Pre-screens text for potential plagiarism by detecting similarity patterns and providing paraphrasing suggestions for high-duplicate sections.

## Technical Difficulty: High ⚠️
> **AI自主验收状态**: 需人工检查
> This skill uses advanced NLP techniques. Results should be manually reviewed before submission.

## Features

1. **Text Similarity Detection**: Identifies potentially plagiarized or highly similar text segments
2. **Originality Scoring**: Provides overall originality percentage (0-100%)
3. **Paraphrasing Suggestions**: Offers AI-powered rewriting for flagged sections
4. **Segment Analysis**: Breaks text into sentences/paragraphs for granular checking

## Usage

### Basic Check
```bash
python scripts/main.py --input "Your text here" --threshold 0.75
```

### File Analysis
```bash
python scripts/main.py --file document.txt --output report.json
```

### With Paraphrasing
```bash
python scripts/main.py --input "text" --paraphrase --style academic
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | string | - | Direct text input (alternative to --file) |
| `--file` | path | - | Path to text file to analyze |
| `--threshold` | float | 0.70 | Similarity threshold (0.0-1.0) for flagging |
| `--paraphrase` | flag | false | Enable paraphrasing suggestions |
| `--style` | string | neutral | Paraphrasing style: academic/formal/casual/neutral |
| `--output` | path | stdout | Output file path (JSON format) |
| `--segments` | string | sentence | Analysis unit: sentence/paragraph |

## Output Format

```json
{
  "originality_score": 85.5,
  "total_segments": 12,
  "flagged_segments": 2,
  "segments": [
    {
      "index": 1,
      "text": "Original sentence text...",
      "similarity_score": 0.92,
      "flagged": true,
      "paraphrase_suggestion": "Rewritten version..."
    }
  ],
  "summary": "Text shows high originality with minor flagged sections"
}
```

## Implementation Notes

- Uses TF-IDF + Cosine Similarity for local similarity detection
- Employs semantic embeddings for meaning-based comparison
- Paraphrasing uses transformer-based models
- No external API calls required; runs locally

## References

- `references/algorithm.md` - Technical algorithm details
- `references/paraphrasing_guide.md` - Paraphrasing methodology

## Limitations

1. Cannot access external databases (internet search required for comprehensive checking)
2. Local similarity only - won't catch plagiarism from external sources
3. Paraphrasing quality depends on input text complexity
4. Processing time increases with document length

## Safety & Privacy

- All processing is local - no text sent to external APIs
- Suitable for sensitive/confidential documents
- No data retention after analysis completes