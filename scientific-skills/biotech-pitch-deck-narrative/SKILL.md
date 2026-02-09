---
name: biotech-pitch-deck-narrative
description: Transform complex scientific data into investor-friendly narratives for
  biotech fundraising pitches
version: 1.0.0
category: Business
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

# Skill: Biotech Pitch Deck Narrative

## Identity
ID: 132
Name: biotech-pitch-deck-narrative
Purpose: Transform complex scientific data into business stories that investors can understand, optimizing the narrative logic of fundraising pitch decks.

## Description

This Skill is designed for biotechnology startups, helping founding teams transform obscure scientific data, preclinical/clinical data, and technical mechanisms into business narratives that investors can easily understand. Through structured analysis and story reconstruction, improve the success rate of fundraising pitches.

## Capabilities

- **Science Translation**: Transform technical terminology, mechanism pathways, and experimental data into business value language
- **Narrative Reconstruction**: Optimize the story line of the pitch deck (Problem → Solution → Market → Traction → Vision)
- **Investor Perspective**: Adjust narrative focus based on different funding rounds (Angel/VC/PE)
- **Data Visualization Suggestions**: Provide best ways to display complex scientific data
- **Risk Balance**: Narrative balance between scientific rigor and business appeal

## Usage

### CLI

```bash
# Analyze existing pitch deck and provide optimization suggestions
python skills/biotech-pitch-deck-narrative/scripts/main.py analyze \
  --input path/to/pitch.pptx \
  --stage seed \
  --output optimization_report.json

# Generate business narrative based on scientific data
python skills/biotech-pitch-deck-narrative/scripts/main.py generate \
  --science "mRNA vaccine technology, targeting KRAS G12C mutation" \
  --stage series-a \
  --focus market \
  --output narrative.json

# Optimize specific sections
python skills/biotech-pitch-deck-narrative/scripts/main.py rewrite \
  --section "technology" \
  --content "Current content..." \
  --audience "generalist-vc" \
  --output improved_section.md
```

### Python API

```python
from skills.biotech_pitch_deck_narrative.scripts.main import (
    BiotechNarrativeEngine,
    PitchStage,
    AudienceType
)

engine = BiotechNarrativeEngine()

# Generate complete narrative
narrative = engine.generate_narrative(
    science_data={
        "technology": "CRISPR-based gene editing for sickle cell",
        "stage": "Phase II clinical",
        "differentiation": "Higher efficiency, lower off-target"
    },
    target_stage=PitchStage.SERIES_B,
    audience=AudienceType.HEALTHCARE_VC
)
```

## Input Parameters

| Parameter | Type | Description |
|------|------|------|
| `input` | string | Input file path (PPT/PDF/Text) |
| `science` | string | Scientific/technical description |
| `stage` | enum | Funding stage: `pre-seed`, `seed`, `series-a`, `series-b`, `series-c`, `ipo` |
| `focus` | enum | Optimization focus: `market`, `technology`, `traction`, `team`, `financials` |
| `audience` | enum | Target audience: `generalist-vc`, `healthcare-vc`, `pharma-corp`, `angel` |
| `section` | enum | Pitch deck section: `problem`, `solution`, `technology`, `market`, `traction`, `team`, `financials`, `vision` |
| `content` | string | Current section content |

## Output Format

### narrative.json

```json
{
  "narrative_arc": {
    "hook": "Opening hook",
    "problem": "Problem statement (business perspective)",
    "solution": "Solution (concise and powerful)",
    "why_now": "Timing argument",
    "market": "Market size and opportunity",
    "traction": "Key milestones",
    "team": "Team credentials",
    "ask": "Funding needs and use of funds"
  },
  "slide_recommendations": [
    {
      "slide_number": 1,
      "title": "Suggested title",
      "key_message": "Key message",
      "content_guidance": "Content guidance",
      "visual_suggestion": "Visual suggestion",
      "investor_question": "Questions investors may ask"
    }
  ],
  "terminology_mapping": {
    "Original term": "Business expression"
  },
  "risk_mitigation": {
    "scientific_risks": ["Risk description and response"],
    "market_risks": ["Risk description and response"],
    "regulatory_risks": ["Risk description and response"]
  },
  "q_a_preparation": [
    {
      "question": "Anticipated question",
      "suggested_answer": "Suggested answer",
      "key_points": ["Key point 1", "Key point 2"]
    }
  ]
}
```

## Examples

### Example 1: mRNA Cancer Vaccine Company Series A

**Input**:
```json
{
  "science": "Personalized neoantigen mRNA vaccine, based on tumor sequencing and AI prediction, targeting solid tumors",
  "stage": "series-a",
  "clinical_data": "Phase I/IIa data, 12/20 patients showed immune response, 3 PR"
}
```

**Output**:
- Technology translation: "AI-driven personalized cancer vaccine platform" → instead of "Neoantigen prediction algorithm"
- Market narrative: Emphasize personalized medicine mega-trend, Moderna-validated mRNA platform
- Data presentation: Waterfall plot showing individual response differences, highlighting depth of response in responders

### Example 2: Gene Editing Tool Company Seed

**Input**:
```json
{
  "science": "Novel base editor enabling C-to-G editing, 100x reduced off-target rate",
  "stage": "seed",
  "differentiation": "Current CGB editing efficiency <10%, we achieve 60%"
}
```

**Output**:
- Problem framing: "Existing gene editing cannot treat 40% of genetic diseases"
- Solution: "Next-generation base editing platform, tackling the hardest-to-treat mutation types"
- Market angle: Addressing indication gaps not covered by CRISPR Therapeutics, Beam

## Best Practices

1. **Avoid oversimplification**: Maintain scientific credibility, use analogies rather than incorrect statements
2. **Data storytelling**: Every data point should serve the business narrative
3. **Investor thinking**: Answer "Why you", "Why now", "What is the exit path"
4. **Layered information**: Core information (everyone understands) + Deep information (professional investors)
5. **FDA pathway visualization**: Clearly display roadmap from current status to approval

## Dependencies

- python-pptx (PPT parsing)
- PyPDF2 (PDF parsing)
- pandas (data processing)
- pydantic (data validation)

## Author

- Created: 2024
- Version: 1.0.0

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
