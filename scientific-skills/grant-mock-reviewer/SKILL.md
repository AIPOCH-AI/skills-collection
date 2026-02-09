---
name: grant-mock-reviewer
description: Simulates NIH study section peer review for grant proposals. Triggers
  when user wants mock review, critique, or evaluation of a grant proposal before
  submission. Generates structured critique using official NIH scoring rubric (1-9
  scale), identifies weaknesses, provides actionable revision recommendations, and
  produces a comprehensive review summary similar to actual NIH Summary Statement.
version: 1.0.0
category: General
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Grant Mock Reviewer

A simulated NIH study section reviewer that provides structured, rigorous critique of grant proposals using the official NIH scoring criteria and methodology.

## Capabilities

1. **NIH Scoring Rubric Application**: Official 1-9 scale scoring across all 5 criteria
2. **Weakness Identification**: Systematic detection of common proposal flaws
3. **Critique Generation**: Structured written critiques for each review criterion
4. **Summary Statement**: Complete mock Summary Statement output
5. **Revision Guidance**: Prioritized, actionable recommendations for improvement

## Usage

### Command Line

```bash
# Full mock review with Summary Statement
python3 scripts/main.py --input proposal.pdf --format pdf --output review.md

# Review Specific Aims only
python3 scripts/main.py --input aims.pdf --section aims --output aims_review.md

# Targeted review (specific criterion focus)
python3 scripts/main.py --input proposal.pdf --focus approach --output approach_critique.md

# Generate NIH-style scores only
python3 scripts/main.py --input proposal.pdf --scores-only --output scores.json

# Compare before/after revision
python3 scripts/main.py --original original.pdf --revised revised.pdf --compare
```

### As Library

```python
from scripts.main import GrantMockReviewer

reviewer = GrantMockReviewer()
result = reviewer.review(
    proposal_text=proposal_content,
    grant_type="R01",
    section="full"
)
print(result.summary_statement)
print(result.scores)
```

## Parameters

| Parameter | Description | Options |
|-----------|-------------|---------|
| `--input` | Path to proposal file (PDF, DOCX, TXT, MD) | File path |
| `--format` | Input file format | `pdf`, `docx`, `txt`, `md` |
| `--section` | Section to review | `full`, `aims`, `significance`, `innovation`, `approach` |
| `--grant-type` | Grant mechanism | `R01`, `R21`, `R03`, `K99`, `F32` |
| `--focus` | Focus on specific criterion | `significance`, `investigator`, `innovation`, `approach`, `environment` |
| `--scores-only` | Output scores only (JSON) | Flag |
| `--output` | Output file path | File path |
| `--original` | Original proposal for comparison | File path |
| `--revised` | Revised proposal for comparison | File path |
| `--compare` | Enable comparison mode | Flag |

## NIH Scoring System

### Overall Impact Score (1-9)
The single most important score reflecting the likelihood of the project to exert a sustained, powerful influence on the research field.

| Score | Descriptor | Likelihood of Funding |
|-------|------------|----------------------|
| 1 | Exceptional | Very High |
| 2 | Outstanding | High |
| 3 | Excellent | Good |
| 4 | Very Good | Moderate |
| 5 | Good | Low-Moderate |
| 6 | Satisfactory | Low |
| 7 | Fair | Very Low |
| 8 | Marginal | Unlikely |
| 9 | Poor | Not Fundable |

### Individual Criteria (1-9 each)

1. **Significance**: Does the project address an important problem? Will scientific knowledge be advanced?
2. **Investigator(s)**: Are the PIs well-suited? Adequate experience and training?
3. **Innovation**: Does it challenge current paradigms? Novel concepts, approaches, methods?
4. **Approach**: Sound research design? Appropriate methods? Adequate controls? Address pitfalls?
5. **Environment**: Adequate institutional support? Scientific environment conducive to success?

### Score Interpretation
- **1-3 (High Priority)**: Compelling, well-developed proposals with strong approach
- **4-5 (Medium Priority)**: Good proposals with some weaknesses
- **6-9 (Low Priority)**: Significant weaknesses that diminish enthusiasm

## Review Output Format

### 1. Score Summary
```
Overall Impact: [Score] - [Descriptor]

Criterion Scores:
- Significance: [Score]
- Investigator(s): [Score]
- Innovation: [Score]
- Approach: [Score]
- Environment: [Score]
```

### 2. Strengths
Bullet-point list of major strengths by criterion

### 3. Weaknesses
Bullet-point list of major weaknesses by criterion

### 4. Detailed Critique
Paragraph-form critique for each criterion following NIH style

### 5. Summary Statement
Complete narrative synthesis of the review

### 6. Revision Recommendations
Prioritized, actionable suggestions for improvement

## Common Weaknesses Detected

### Significance
- Insufficient justification for the research problem
- Incremental rather than transformative impact
- Unclear connection to human health/disease
- Overstatement of clinical significance without evidence

### Investigator
- Lack of relevant expertise for proposed aims
- Insufficient track record in key methodologies
- PI overcommitted (excessive effort on other grants)
- Missing key collaborator expertise

### Innovation
- Straightforward extension of published work
- Methods are standard rather than novel
- No challenging of existing paradigms
- Incremental rather than breakthrough potential

### Approach
- Aims too ambitious for timeframe
- Insufficient preliminary data
- Inadequate experimental controls
- No discussion of pitfalls and alternatives
- Statistical analysis plan missing or inadequate
- Sample size/power calculations absent

### Environment
- Inadequate institutional resources
- Missing core facility access
- Lack of relevant equipment
- Insufficient collaborative environment

## Technical Difficulty

**High** - Requires deep understanding of NIH peer review processes, ability to apply standardized scoring rubrics consistently, and generation of clinically/scientifically accurate critique across diverse research domains.

**Review Required**: Human verification recommended before deployment in production settings.

## References

- `references/nih_scoring_rubric.md` - Complete NIH scoring guidelines
- `references/review_criteria_explained.md` - Detailed criterion descriptions
- `references/common_weaknesses_catalog.md` - Database of typical proposal flaws
- `references/summary_statement_templates.md` - NIH-style statement templates
- `references/score_calibration_guide.md` - Score assignment guidelines

## Best Practices for Users

1. **Provide Complete Proposals**: The tool works best with full Research Strategy sections
2. **Include Preliminary Data**: Approach critique depends on feasibility evidence
3. **Review Multiple Times**: Use iteratively as you revise
4. **Compare Versions**: Track improvement between drafts
5. **Consider Multiple Perspectives**: Supplement with human reviewer feedback

## Limitations

1. Cannot access external literature to verify claims
2. May not capture domain-specific methodological nuances
3. Scoring is simulated and may not match actual study section scores
4. Best used as preparatory tool, not replacement for human review

## Version

1.0.0 - Initial release with NIH R01/R21/R03 support

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
