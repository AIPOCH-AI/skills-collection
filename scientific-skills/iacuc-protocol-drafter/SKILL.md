---
name: iacuc-protocol-drafter
description: Draft IACUC protocol applications with focus on the 3Rs principles justification
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
