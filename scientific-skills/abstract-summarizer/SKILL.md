---
name: abstract-summarizer
description: Summarize long academic papers into structured abstracts within 250 words. Trigger when user provides a paper (PDF, text, or URL) and requests a summary, abstract, or TL;DR. Optimized for research papers, theses, and technical reports.
version: 1.0.0
category: Info
tags: [abstract, summarization, academic-papers, research, nlp]
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: 
last_updated: 2026-02-06
---

# Abstract Summarizer

A specialized skill for condensing lengthy academic papers into concise, structured abstracts while preserving scientific accuracy.

## Purpose

Transform complex academic documents (research papers, theses, technical reports) into standardized 250-word structured abstracts that capture:
- Research background and motivation
- Methodology and approach
- Key findings and results
- Conclusions and implications

## Trigger Conditions

Activate this skill when:
1. User provides a paper (PDF, text, URL) and asks for summary/abstract
2. User explicitly requests "TL;DR" or "executive summary"
3. User needs to quickly understand a paper's core contribution
4. Processing academic or technical documents >1000 words

## Input Format

Accepted inputs:
- PDF file path or content
- Plain text of paper content
- URL to paper (will fetch content)
- Clipboard text containing paper

## Output Format

Structured abstract with exactly these sections:

```
**Background**: [1 sentence on context and problem]

**Objective**: [1 sentence on research goal]

**Methods**: [1-2 sentences on methodology]

**Results**: [2-3 sentences on key findings]

**Conclusion**: [1 sentence on implications]

---
Word count: XXX/250
```

## Technical Approach

### Extraction Strategy
1. **Identify structure**: Parse paper sections (Abstract, Intro, Methods, Results, Discussion)
2. **Key sentence extraction**: Use positional and semantic cues to identify critical sentences
3. **Core concept identification**: Extract research questions, hypotheses, main findings
4. **Redundancy elimination**: Remove citations, methodological details, minor results

### Condensation Rules
- Preserve technical terminology and quantitative results
- Maintain logical flow between sections
- Ensure standalone comprehensibility
- Strict 250-word limit with counter validation

## Difficulty Level

**High** - Requires understanding of:
- Academic writing conventions across disciplines
- Scientific methodology terminology
- Context-dependent information prioritization
- Cross-domain knowledge integration

## Quality Criteria

A successful abstract must:
- [ ] Accurately represent the paper's core contribution
- [ ] Be understandable without reading the original
- [ ] Include specific quantitative results where present
- [ ] Maintain scientific rigor and precision
- [ ] Stay within 250-word limit
- [ ] Follow the structured format consistently

## Limitations

- May miss nuanced arguments in humanities papers
- Complex mathematical proofs may be oversimplified
- Domain-specific jargon requires contextual understanding
- Multi-study papers need selective focus

## Example Usage

```python
# Direct usage
python scripts/main.py --input paper.pdf --output summary.txt

# From text
python scripts/main.py --text "[paste paper content]" --format structured
```

## References

See `references/` for:
- `abstract-templates.md`: Discipline-specific abstract templates
- `evaluation-rubric.md`: Quality assessment criteria
- `example-abstracts/`: Sample inputs and outputs for testing

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | No scripts included | Low |
| Network Access | URL fetching only with user consent | Low |
| File System Access | Read-only within workspace | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Input/output within session | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] URL fetching requires explicit user confirmation
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place

## Evaluation Criteria

### Success Metrics
- [ ] Accurately represents the paper's core contribution
- [ ] Abstract is understandable without reading the original
- [ ] Includes specific quantitative results where present
- [ ] Maintains scientific rigor and precision
- [ ] Strictly within 250-word limit
- [ ] Follows structured format consistently

### Test Cases
1. **Basic Summarization**: Input research paper → Output valid structured abstract
2. **Word Count Limit**: Verify strict 250-word compliance
3. **Multi-disciplinary**: Test papers from different fields (biology, physics, humanities)
4. **Complex Data**: Input paper with heavy statistics → Accurate representation
5. **URL Input**: Fetch and summarize from valid academic URL

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: May miss nuanced arguments in humanities papers
- **Planned Improvements**:
  - Enhance handling of mathematical proofs
  - Improve multi-study paper summarization
