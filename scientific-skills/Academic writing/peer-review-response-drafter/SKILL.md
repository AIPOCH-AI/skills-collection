---
name: peer-review-response-drafter
description: Assist in drafting professional peer review response letters. Trigger
  when user mentions "reviewer comments", "response letter", "peer review", "revise
  and resubmit", "R&R", "reviewer feedback", or needs help responding to academic
  journal reviewers.
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

# Peer Review Response Drafter

Assist researchers in crafting professional, polite, and effective responses to peer reviewer comments for academic journal submissions.

## Overview

This skill parses reviewer comments, drafts structured responses, and adjusts tone to ensure:
- Professional and courteous language
- Clear point-by-point addressing of concerns
- Constructive framing of disagreements
- Consistent academic writing style

## When to Use

- Responding to peer reviewer comments after paper revision
- Preparing author response letters for journal resubmission
- Addressing major/minor revision requirements
- Drafting rebuttal letters for conference submissions
- Converting informal notes into formal response language

## Workflow

### Step 1: Parse Input
Collect and structure the following:
- **Reviewer comments**: Original text from reviewers (often numbered/sectioned)
- **Manuscript context**: Title, journal name, revision round (if applicable)
- **Author changes**: Brief notes on what was modified in response to each comment
- **Tone preference**: Formal academic / diplomatic / assertive (default: diplomatic)

### Step 2: Structure Response Letter
Standard academic response letter format:

```
Dear Editor and Reviewers,

Thank you for your constructive feedback on our manuscript titled 
"[Title]" submitted to [Journal]. We have carefully addressed all 
comments and revised the manuscript accordingly. Below is our 
point-by-point response to each reviewer's comments.

Reviewer #1:
[Numbered responses]

Reviewer #2:
[Numbered responses]

...

Sincerely,
[Authors]
```

### Step 3: Draft Individual Responses

For each reviewer comment, generate a response containing:

1. **Acknowledgment**: Thank the reviewer for the observation
2. **Action taken**: Describe the change made (if applicable)
3. **Location indicator**: Page/line number where change appears
4. **Optional rationale**: Brief explanation if no change was made

#### Response Templates

**Accepting a suggestion:**
```
Comment: The methodology section lacks detail on data preprocessing.

Response: We thank the reviewer for this important observation. 
We have expanded the methodology section to include detailed 
descriptions of data preprocessing steps, including normalization, 
outlier removal, and feature selection procedures (Page 5, Lines 120-135).
```

**Partial acceptance with modification:**
```
Comment: The authors should use Method X instead of Method Y.

Response: We appreciate the reviewer's suggestion. While Method X 
is indeed widely used, we found that Method Y is more appropriate 
for our specific dataset due to [brief rationale]. However, we have 
added a comparative discussion of both methods in the revised 
manuscript (Page 8, Lines 200-210) to acknowledge this alternative 
approach.
```

**Politely declining:**
```
Comment: The authors should remove Figure 3 as it seems redundant.

Response: We thank the reviewer for this suggestion. Upon careful 
consideration, we believe Figure 3 provides essential visual 
support for the key finding discussed in Section 4.2. To enhance 
clarity, we have revised the figure caption to better emphasize 
its unique contribution (Page 10, Figure 3 caption).
```

### Step 4: Tone Adjustment

Adjust language based on context:

| Tone | Use Case | Example Phrasing |
|------|----------|------------------|
| Diplomatic | General revisions | "We thank..." / "We appreciate..." / "We have revised..." |
| Assertive | Defending methodology | "We respectfully note..." / "Our approach is justified because..." |
| Grateful | Major improvements | "We are grateful for..." / "This significantly improved..." |

## Input Format

Accept multiple input formats:
- Copy-pasted reviewer comments
- PDF extracted text
- Structured JSON with comment IDs
- Markdown with sections

## Output Format

Returns a complete response letter with:
- Proper salutation and closing
- Numbered responses matching reviewer comments
- Inline citations to manuscript locations
- Professional academic tone throughout

## Usage Example

```
User: Help me draft a response to these reviewer comments:

Reviewer 1:
1. The introduction should better motivate the problem
2. Figure 2 is unclear
3. Have you considered Smith et al. 2023?

My changes:
1. Added motivation paragraph
2. Redrew Figure 2 with clearer labels
3. Added citation and discussion

Journal: Nature Communications
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--interactive` | flag | No | - | **Interactive mode**: Guided wizard with prompts (uses `input()`). Recommended for first-time users or complex responses |
| `--input-file` | str | No | - | Path to reviewer comments file (automation mode) |
| `--output` | str | No | - | Output file path for response letter |
| `--tone` | str | No | "diplomatic" | Response tone: "diplomatic", "formal", or "assertive" |
| `--format` | str | No | "markdown" | Output format: "markdown", "plain_text", or "latex" |
| `--include-diff` | bool | No | true | Whether to summarize changes made |

**Usage Modes:**
- **Interactive Mode**: Use `--interactive` for guided setup with prompts (recommended for first-time users)
- **File Mode (Recommended for automation)**: Use `--input-file` with pre-prepared reviewer comments

## Technical Notes

- **Difficulty**: High - Requires understanding of academic norms, context-aware tone adjustment, and nuanced handling of criticism
- **Limitations**: Does not verify factual accuracy of responses; human review required for technical content
- **Safety**: No external API calls; processes text locally

## References

- `references/response_templates.md` - Common response patterns
- `references/tone_guide.md` - Academic tone guidelines
- `references/examples/` - Sample response letters

## Quality Checklist

Before finalizing, verify:
- [ ] Every reviewer comment has a corresponding response
- [ ] Responses are numbered/lettered consistently with comments
- [ ] All changes are referenced with page/line numbers
- [ ] Disagreements are framed constructively
- [ ] No defensive or confrontational language
- [ ] Professional tone maintained throughout

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
