---
name: semantic-consistency-auditor
description: Evaluate semantic consistency between AI-generated clinical notes and
  expert gold standards using BERTScore and COMET
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Skill: Semantic Consistency Auditor

**ID:** 212  
**Name:** semantic-consistency-auditor  
**Description:** Introduces BERTScore and COMET algorithms to evaluate the semantic consistency between AI-generated clinical notes and expert gold standards from the "semantic entailment" level.

## Overview

Semantic Consistency Auditor is a medical AI evaluation tool used to assess the semantic consistency between AI-generated clinical notes and expert-written gold standards from a semantic level. This tool is not limited to traditional string matching or bag-of-words models, but uses deep learning models to understand semantic entailment relationships, capable of identifying expressions with different wording but similar meaning.

## Algorithms

### 1. BERTScore
BERTScore uses pre-trained BERT model contextual embeddings to calculate similarity between candidate text and reference text:
- **Precision**: How much semantics in the candidate text is covered by the reference text
- **Recall**: How much semantics in the reference text is covered by the candidate text
- **F1 Score**: Harmonic mean of Precision and Recall

### 2. COMET (Cross-lingual Optimized Metric for Evaluation of Translation)
COMET is a neural network-based evaluation metric originally used for machine translation evaluation, applicable to semantic entailment tasks:
- Uses XLM-RoBERTa encoder to capture deep semantics
- Outputs semantic consistency scores between 0-1
- Gives high scores to semantically equivalent but differently expressed text

## Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Or venv\Scripts\activate  # Windows

# Install dependencies
pip install bertscore comet-ml transformers torch
```

## Configuration

Configure in `~/.openclaw/skills/semantic-consistency-auditor/config.yaml`:

```yaml
# BERTScore Configuration
bertscore:
  model: "microsoft/deberta-xlarge-mnli"  # Or "bert-base-chinese" for Chinese
  lang: "zh"  # Language code: zh, en, etc.
  rescale_with_baseline: true
  device: "auto"  # auto, cpu, cuda

# COMET Configuration
comet:
  model: "Unbabel/wmt22-comet-da"  # COMET model
  batch_size: 8
  device: "auto"

# Evaluation Thresholds
thresholds:
  bertscore_f1: 0.85
  comet_score: 0.75
  semantic_consistency: 0.80  # Comprehensive score threshold
```

## Usage

### Command Line

```bash
# Evaluate single case pair
python scripts/main.py \
  --ai-generated "Patient presented with fever for 3 days, highest temperature 39°C, accompanied by cough." \
  --gold-standard "Patient chief complaint of fever for 3 days, highest temperature 39°C, accompanied by cough symptoms." \
  --output results.json

# Batch evaluation from JSON file
python scripts/main.py \
  --input-file batch_cases.json \
  --output results.json \
  --format detailed

# Use specific model
python scripts/main.py \
  --ai-generated "..." \
  --gold-standard "..." \
  --bert-model "bert-base-chinese" \
  --comet-model "Unbabel/wmt20-comet-da"
```

### Python API

```python
from semantic_consistency_auditor import SemanticConsistencyAuditor

# Initialize evaluator
auditor = SemanticConsistencyAuditor(
    bert_model="microsoft/deberta-xlarge-mnli",
    comet_model="Unbabel/wmt22-comet-da",
    lang="zh"
)

# Evaluate single case
result = auditor.evaluate(
    ai_text="Patient presented with fever for 3 days...",
    gold_text="Patient chief complaint of fever for 3 days..."
)

print(f"BERTScore F1: {result['bertscore']['f1']:.4f}")
print(f"COMET Score: {result['comet']['score']:.4f}")
print(f"Consistency: {result['consistency']:.4f}")
print(f"Passed: {result['passed']}")

# Batch evaluation
results = auditor.evaluate_batch([
    {"ai": "...", "gold": "..."},
    {"ai": "...", "gold": "..."}
])
```

## Input Format

### Single Case (Command Line)

Pass text directly through `--ai-generated` and `--gold-standard` parameters.

### Batch Evaluation File (JSON)

```json
[
  {
    "case_id": "CASE001",
    "ai_generated": "Patient presented with fever for 3 days, highest temperature 39°C, accompanied by cough.",
    "gold_standard": "Patient chief complaint of fever for 3 days, highest temperature 39°C, accompanied by cough symptoms.",
    "metadata": {
      "department": "Respiratory",
      "disease_type": "Upper respiratory infection"
    }
  },
  {
    "case_id": "CASE002",
    "ai_generated": "...",
    "gold_standard": "..."
  }
]
```

## Output Format

### Summary Mode

```json
{
  "overall": {
    "total_cases": 100,
    "passed_cases": 85,
    "pass_rate": 0.85,
    "avg_bertscore_f1": 0.8923,
    "avg_comet_score": 0.8234,
    "avg_consistency": 0.8579
  },
  "thresholds": {
    "bertscore_f1": 0.85,
    "comet_score": 0.75,
    "semantic_consistency": 0.80
  }
}
```

### Detailed Mode

```json
{
  "cases": [
    {
      "case_id": "CASE001",
      "ai_generated": "Patient presented with fever for 3 days...",
      "gold_standard": "Patient chief complaint of fever for 3 days...",
      "metrics": {
        "bertscore": {
          "precision": 0.9123,
          "recall": 0.8934,
          "f1": 0.9028
        },
        "comet": {
          "score": 0.8234,
          "system_score": 0.8156
        },
        "semantic_consistency": 0.8631
      },
      "passed": true,
      "details": {
        "semantic_gaps": [],
        "matched_concepts": ["fever for 3 days", "temperature 39°C", "cough"]
      }
    }
  ],
  "summary": { ... }
}
```

## Evaluation Criteria

### Semantic Consistency Grading

| Score Range | Grade | Description |
|---------|------|------|
| 0.90 - 1.00 | Excellent | Highly consistent semantics, almost no difference |
| 0.80 - 0.89 | Good | Basically consistent semantics, minor differences exist |
| 0.70 - 0.79 | Pass | Generally consistent semantics, partial omissions or deviations exist |
| 0.60 - 0.69 | Needs Improvement | Obvious semantic differences exist |
| < 0.60 | Fail | Semantic inconsistency, major omissions or errors exist |

### Pass Criteria

Default pass conditions (configurable):
- BERTScore F1 ≥ 0.85
- COMET Score ≥ 0.75
- Comprehensive semantic consistency ≥ 0.80

## Error Handling

| Error Code | Description | Handling Suggestion |
|-------|------|---------|
| E001 | Input text is empty | Check input data integrity |
| E002 | Model loading failed | Check network connection or local model path |
| E003 | Language not supported | Use supported lang parameter |
| E004 | Insufficient GPU memory | Switch to CPU mode or reduce batch_size |
| E005 | JSON parsing error | Check input file format |

## Performance Notes

- **BERTScore**: First run will download model (approximately 400MB-1GB)
- **COMET**: First run will download model (approximately 500MB-1.5GB)
- **GPU Acceleration**: Significantly improves evaluation speed in CUDA environment
- **Batch Processing**: Recommended for batch evaluation to fully utilize GPU parallel capability

## References

1. Zhang et al. "BERTScore: Evaluating Text Generation with BERT" ICLR 2020
2. Rei et al. "COMET: A Neural Framework for MT Evaluation" EMNLP 2020
3. Medical Record Standardization Evaluation Guidelines (National Health Commission)

## Changelog

- **v1.0.0** (2026-02-06): Initial version, supports dual-algorithm evaluation with BERTScore and COMET

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
