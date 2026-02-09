---
name: iacuc-protocol-drafter
description: Draft IACUC protocol applications with focus on the 3Rs principles justification
version: 1.0.0
category: Pharma
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

# IACUC Protocol Drafter

**ID**: 105  
**Name**: IACUC Protocol Drafter  
**Description**: Draft Institutional Animal Care and Use Committee (IACUC) protocol applications, especially the justification section for the "3Rs principles" (Replacement, Reduction, Refinement).

## Requirements

- Python 3.8+
- No additional dependencies (uses standard library)

## Usage

```bash
# Generate local file
python skills/iacuc-protocol-drafter/scripts/main.py --input protocol_input.json --output iacuc_protocol.txt

# Use stdin/stdout
cat protocol_input.json | python skills/iacuc-protocol-drafter/scripts/main.py
```

## Input Format (JSON)

```json
{
  "title": "Experiment Title",
  "principal_investigator": "Principal Investigator Name",
  "institution": "Research Institution Name",
  "species": "Experimental Animal Species",
  "number_of_animals": 50,
  "procedure_description": "Brief description of experimental procedures",
  "pain_category": "B",
  "justification": {
    "replacement": {
      "alternatives_considered": ["In vitro experiments", "Computer simulation"],
      "why_animals_needed": "Reasons why animals must be used"
    },
    "reduction": {
      "sample_size_calculation": "Sample size calculation method and rationale",
      "minimization_strategies": "Strategies to minimize animal numbers"
    },
    "refinement": {
      "pain_management": "Pain management measures",
      "housing_enrichment": "Housing environment optimization",
      "humane_endpoints": "Humane endpoint setting"
    }
  }
}
```

## Output

Generate IACUC-standard application text, including a complete 3Rs principles justification section.

## Templates

Built-in standard templates cover:
- **Replacement**: Justification for why live animals must be used
- **Reduction**: Explanation of statistical basis for sample size calculation
- **Refinement**: Description of measures to reduce pain and stress

## Notes

- Generated content should be used as a draft and adjusted according to actual conditions
- It is recommended to consult your institution's IACUC office for specific format requirements
- Ensure all animal experiments comply with local regulations and institutional policies

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
