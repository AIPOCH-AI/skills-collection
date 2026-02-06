---
name: grant-proposal-assistant
description: Grant proposal writing assistant for NIH (R01/R21), NSF and other mainstream
  funding applications. Triggers when user needs help writing specific aims, research
  strategy, budget justification, or other grant sections. Provides templates, section
  generators, and best practice guidance for competitive grant proposals.
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

# Grant Proposal Assistant

A comprehensive tool for writing competitive grant proposals targeting NIH (R01/R21), NSF, and other major funding agencies.

## Capabilities

1. **Section Templates**: Standard templates for all major grant sections
2. **Specific Aims Generator**: Structured approach to crafting compelling Specific Aims pages
3. **Budget Justification Helper**: Equipment, personnel, and other cost justifications
4. **Review & Critique**: Self-assessment checklists for proposal quality

## Usage

### Command Line

```bash
# Generate Specific Aims template
python3 scripts/main.py --section aims --output my_aims.md

# Generate full proposal template
python3 scripts/main.py --section full --agency NIH --type R01 --output proposal.md

# Budget justification helper
python3 scripts/main.py --section budget --category personnel --output budget.md

# Review existing proposal
python3 scripts/main.py --review --input my_proposal.md
```

### As Library

```python
from scripts.main import GrantProposalAssistant

assistant = GrantProposalAssistant(agency="NIH", grant_type="R01")
template = assistant.generate_section("specific_aims")
budget = assistant.generate_budget_justification(category="equipment", items=[...])
```

## Parameters

| Parameter | Description | Options |
|-----------|-------------|---------|
| `--section` | Section to generate | `aims`, `significance`, `approach`, `budget`, `full` |
| `--agency` | Funding agency | `NIH`, `NSF`, `DOD`, `VA` |
| `--type` | Grant mechanism | `R01`, `R21`, `R03`, `SBIR`, `STTR` |
| `--category` | Budget category | `personnel`, `equipment`, `supplies`, `travel`, `other` |
| `--input` | Input file for review | Path to existing proposal |
| `--output` | Output file path | Path for generated content |

## Technical Difficulty

**Medium** - Requires understanding of grant structure, funding agency requirements, and scientific writing best practices.

## References

- `references/NIH_R01_template.md` - NIH R01 full proposal template
- `references/NSF_template.md` - NSF standard grant template
- `references/budget_templates.xlsx` - Budget templates by category
- `references/review_checklist.md` - Proposal quality checklist
- `references/specific_aims_examples.md` - Example Specific Aims pages

## Best Practices

1. **Start with Specific Aims**: This 1-page summary drives the entire proposal
2. **Follow Page Limits**: NIH R01 Research Strategy = 12 pages, Specific Aims = 1 page
3. **Use Significance-Innovation-Approach Structure**: Standard for NIH applications
4. **Justify Everything**: Every budget item needs a clear justification
5. **Review with Checklist**: Use the built-in review tool before submission

## Agency-Specific Notes

### NIH R01/R21
- Page limits strictly enforced
- Significance, Innovation, Approach structure required
- Vertebrate animals and human subjects sections if applicable
- Resubmission strategy for A1 applications

### NSF
- Project Summary (1 page) and Project Description (15 pages)
- Broader impacts criterion weighted equally with intellectual merit
- Data management plan required
- Facilities and resources section

## Version

1.0.0 - Initial release with NIH and NSF support

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
