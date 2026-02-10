#!/usr/bin/env python3
"""
Grant Proposal Assistant
Main script for generating grant proposal sections and templates.
Supports NIH (R01/R21), NSF, and other funding agencies.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class GrantProposalAssistant:
    """Main class for grant proposal assistance."""
    
    AGENCIES = {
        "NIH": {
            "R01": {
                "duration": "5 years",
                "budget_direct": "$500K/year",
                "pages_research": 12,
                "pages_aims": 1,
                "structure": ["Specific Aims", "Significance", "Innovation", "Approach"]
            },
            "R21": {
                "duration": "2 years",
                "budget_direct": "$275K total",
                "pages_research": 6,
                "pages_aims": 1,
                "structure": ["Specific Aims", "Significance", "Innovation", "Approach"]
            },
            "R03": {
                "duration": "2 years",
                "budget_direct": "$100K/year",
                "pages_research": 6,
                "pages_aims": 1,
                "structure": ["Specific Aims", "Significance", "Innovation", "Approach"]
            }
        },
        "NSF": {
            "standard": {
                "duration": "3 years",
                "budget": "varies",
                "pages_summary": 1,
                "pages_description": 15,
                "structure": ["Project Summary", "Project Description", "References", "Bio Sketches"]
            }
        }
    }
    
    def __init__(self, agency: str = "NIH", grant_type: str = "R01"):
        self.agency = agency.upper()
        self.grant_type = grant_type.upper() if grant_type else "R01"
        self.base_path = Path(__file__).parent.parent
        
    def generate_section(self, section: str, **kwargs) -> str:
        """Generate a specific grant section."""
        generators = {
            "aims": self._generate_specific_aims,
            "specific_aims": self._generate_specific_aims,
            "significance": self._generate_significance,
            "innovation": self._generate_innovation,
            "approach": self._generate_approach,
            "budget": self._generate_budget_template,
            "full": self._generate_full_proposal,
            "project_summary": self._generate_project_summary,
            "project_description": self._generate_project_description
        }
        
        if section not in generators:
            raise ValueError(f"Unknown section: {section}. Available: {list(generators.keys())}")
        
        # Only pass num_aims to functions that accept it
        if section in ["aims", "specific_aims", "full"]:
            return generators[section](**kwargs)
        else:
            return generators[section]()
    
    def _generate_specific_aims(self, title: str = "[Project Title]", 
                                 hypothesis: str = "[Working Hypothesis]",
                                 num_aims: int = 3) -> str:
        """Generate Specific Aims page template (1 page for NIH)."""
        aims_list = []
        for i in range(1, num_aims + 1):
            aims_list.append(f"""
**Aim {i}**: [One sentence describing Aim {i}]
- **Hypothesis**: [Testable hypothesis for Aim {i}]
- **Rationale**: [2-3 sentences explaining why this aim is important]
- **Expected Outcome**: [What you expect to learn/demonstrate]
""")
        
        aims_text = "\n".join(aims_list)
        
        return f"""# SPECIFIC AIMS

**Title**: {title}

## Summary

[1-2 paragraphs providing overview of the problem, gap in knowledge, and your overall approach]

**Central Hypothesis**: {hypothesis}

## Specific Aims

{aims_text}

## Impact

[1 paragraph explaining how successful completion of these aims will advance the field, impact human health, or contribute to scientific knowledge]

---
*Page limit: 1 page (NIH). Use 0.5" margins, Arial/Helvetica 11pt or larger.*
"""
    
    def _generate_significance(self) -> str:
        """Generate Significance section template."""
        return """# SIGNIFICANCE

## Current State of the Field

[Describe the current understanding of the problem. What is known?]

## Critical Gap

[What critical knowledge gap or barrier does your proposal address? 
Why is this problem important to solve?]

## How This Research Addresses the Gap

[Specifically explain how your proposed work will fill the identified gap]

## Impact on the Field

1. **Scientific Impact**: [How will findings advance basic science?]
2. **Clinical/Translational Impact**: [Relevance to patients, if applicable]
3. **Methodological Impact**: [New methods or approaches developed]

---
*NIH R01: ~3 pages within 12-page Research Strategy limit*
"""
    
    def _generate_innovation(self) -> str:
        """Generate Innovation section template."""
        return """# INNOVATION

## Conceptual Innovation

[Describe innovative concepts, paradigms, or theories being tested]

## Technical Innovation

[Novel methods, technologies, or approaches you will employ]

## Distinction from Current Practice

| Aspect | Current Standard | Your Innovation |
|--------|------------------|-----------------|
| [Aspect 1] | [Current approach] | [Your novel approach] |
| [Aspect 2] | [Current approach] | [Your novel approach] |

## Risk-Benefit Consideration

[Acknowledge risks but explain why potential benefits justify the approach]

---
*NIH R01: ~1 page within 12-page limit*
"""
    
    def _generate_approach(self, num_aims: int = 3) -> str:
        """Generate Approach section template with subsections per aim."""
        approach_sections = []
        
        for i in range(1, num_aims + 1):
            approach_sections.append(f"""## Aim {i}: [Aim Title]

### Rationale
[Why this approach was chosen]

### Experimental Design

#### Study Design
[Detailed description of experiments]

#### Variables
- **Independent variables**: [...]
- **Dependent variables**: [...]
- **Controls**: [...]

#### Timeline
| Period | Activity | Milestone |
|--------|----------|-----------|
| Months 1-6 | [Activity] | [Milestone] |
| Months 7-12 | [Activity] | [Milestone] |

### Potential Pitfalls and Alternatives

| Pitfall | Likelihood | Alternative Approach |
|---------|------------|----------------------|
| [Issue 1] | High/Medium/Low | [Alternative plan] |

### Expected Outcomes and Interpretation

[What results would support/refute your hypothesis?]

""")
        
        approaches = "\n".join(approach_sections)
        
        return f"""# APPROACH

## Overview
[Brief overview of your overall experimental strategy]

## Preliminary Data
[Summary of key preliminary data supporting feasibility]

{approaches}

## Statistical Analysis Plan

[Statistical methods, power analysis, significance thresholds]

## Data Management and Sharing

[NIH Data Management and Sharing Plan requirements]

---
*NIH R01: ~6-8 pages within 12-page limit*
"""
    
    def generate_budget_justification(self, category: str, 
                                       items: Optional[List[Dict]] = None) -> str:
        """Generate budget justification for specific categories."""
        
        justifications = {
            "personnel": """# Personnel Justification

## Key Personnel

| Name | Role | % Effort | Institutional Base | Requested Salary | Benefits |
|------|------|----------|-------------------|------------------|----------|
| [PI Name] | Principal Investigator | [X%] | $[amount] | $[amount] | $[amount] |
| [Name] | [Role] | [X%] | $[amount] | $[amount] | $[amount] |

## Justification

### Principal Investigator ([Name])
The PI will provide overall scientific leadership, supervise research staff, 
analyze data, and prepare manuscripts. [X]% effort is requested for Year 1, 
decreasing to [Y]% in subsequent years as trainees become more independent.

### [Other Personnel]
[Describe role and justification for each team member]

## Recruitment Plan
[How you will recruit personnel if not yet identified]
""",
            "equipment": """# Equipment Justification

## Equipment Items

| Item | Purpose | Cost | Justification |
|------|---------|------|---------------|
| [Item 1] | [Purpose] | $[amount] | [Why needed] |

## Justification Detail

### [Major Item Name] - $[Amount]

**Purpose**: [Detailed explanation of scientific need]

**Why Not Available**: 
- [Explain why existing equipment cannot be used]
- [Why other labs cannot provide access]

**Usage Plan**:
- % of time dedicated to this project: [X]%
- Other projects using equipment: [List]
- Location: [Where it will be housed]

**Maintenance**: [Annual maintenance costs and source of funds]
""",
            "supplies": """# Supplies Justification

## Supply Categories

| Category | Year 1 | Year 2 | Year 3 | Justification |
|----------|--------|--------|--------|---------------|
| Reagents | $[amount] | $[amount] | $[amount] | [Brief justification] |
| Consumables | $[amount] | $[amount] | $[amount] | [Brief justification] |
| Animals | $[amount] | $[amount] | $[amount] | [Strain, number, cost per animal] |

## Detailed Justification

### Reagents
[Specific reagents needed, quantities, and costs]

### Consumables
[Plates, tubes, tips, etc. with estimated usage]

### Animal Costs (if applicable)
- Strain: [Strain name]
- Number requested: [X] animals
- Cost per animal: $[amount]
- Justification for number: [Power calculation or experimental design basis]
""",
            "travel": """# Travel Justification

## Domestic Travel

| Purpose | Destination | Frequency | Cost/Trip | Total |
|---------|-------------|-----------|-----------|-------|
| [Conference] | [Location] | [X/year] | $[amount] | $[amount] |

**Justification**: [Why this travel is essential to the project]

## Foreign Travel (if applicable)

[Justification for any foreign travel - must be exceptional for NIH]

## Training/Workshop Travel

[Travel for training on specific techniques relevant to aims]
""",
            "other": """# Other Direct Costs Justification

## Subcontracts

| Institution | PI | Amount | Scope |
|-------------|-----|--------|-------|
| [Institution] | [Name] | $[amount] | [Brief description of work] |

**Justification**: [Why this collaboration is necessary and not duplicative]

## Consultants

| Name | Role | Rate | Hours | Total |
|------|------|------|-------|-------|
| [Name] | [Expertise] | $[rate]/hr | [X hrs] | $[amount] |

**Justification**: [Why consultant expertise is needed vs. personnel]

## Publication Costs

[Page charges, open access fees - estimate based on planned publications]

## Tuition (if training grant component)

[Justification for tuition remission]
"""
        }
        
        return justifications.get(category.lower(), justifications["other"])
    
    def _generate_budget_template(self, category: str = "all", **kwargs) -> str:
        """Generate full budget section."""
        categories = ["personnel", "equipment", "supplies", "travel", "other"] \
                     if category == "all" else [category]
        
        sections = []
        for cat in categories:
            sections.append(self.generate_budget_justification(cat))
        
        return "\n\n---\n\n".join(sections)
    
    def _generate_project_summary(self) -> str:
        """Generate NSF-style Project Summary (1 page)."""
        return """# PROJECT SUMMARY

## Overview

[1-2 sentences on what you propose to do]

## Intellectual Merit

[How the proposed activity advances knowledge]

## Broader Impacts

1. **Education**: [Training students, curriculum development]
2. **Societal Impact**: [Benefits to society beyond the research]
3. **Diversity**: [How project promotes participation of underrepresented groups]
4. **Dissemination**: [How results will be shared]

## Key Words
[3-5 keywords for classification]

---
*NSF: 1 page limit. Must address both Intellectual Merit and Broader Impacts.*
"""
    
    def _generate_project_description(self) -> str:
        """Generate NSF-style Project Description."""
        return """# PROJECT DESCRIPTION

## 1. Introduction and Background

[Context and importance of the research problem]

## 2. Research Objectives

### Objective 1: [Title]
[Description, methods, expected outcomes]

### Objective 2: [Title]
[Description, methods, expected outcomes]

### Objective 3: [Title]
[Description, methods, expected outcomes]

## 3. Methodology and Approach

### Experimental Design
[Detailed methods]

### Data Analysis
[Statistical approaches]

### Timeline
[Gantt chart or table of activities]

## 4. Results from Prior NSF Support (if applicable)

[Summary of prior grants and outcomes]

## 5. Broader Impacts Activities

[Specific activities beyond the research itself]

---
*NSF: 15 pages maximum for most programs*
"""
    
    def _generate_full_proposal(self, **kwargs) -> str:
        """Generate full proposal template based on agency/type."""
        if self.agency == "NIH":
            return f"""# NIH {self.grant_type} RESEARCH PROPOSAL

{self._generate_specific_aims()}

---

{self._generate_significance()}

{self._generate_innovation()}

{self._generate_approach()}

---

## BUDGET JUSTIFICATION

{self.generate_budget_justification(category='all')}

---

## ADDITIONAL REQUIRED SECTIONS

### Vertebrate Animals (if applicable)
- Description of procedures
- Justification for species/numbers
- Veterinary care
- Euthanasia methods

### Human Subjects (if applicable)
- Protection of human subjects
- Inclusion of women and minorities
- Inclusion of children

### Authentication of Key Resources
- List of key biological resources
- Authentication plan

### Data Management and Sharing Plan
- Data types and standards
- Repository selection
- Timeline

---
*Generated for NIH {self.grant_type}*
*Submission Date: {datetime.now().strftime('%Y-%m-%d')}*
"""
        else:
            return f"""# {self.agency} RESEARCH PROPOSAL

{self._generate_project_summary()}

---

{self._generate_project_description()}

---

## BUDGET JUSTIFICATION
{self.generate_budget_justification(category='all')}

---

## ADDITIONAL SECTIONS

### References Cited
[Standard bibliographic format]

### Biographical Sketches
- Senior Personnel only
- Use current NSF format

### Facilities and Resources
- Laboratory facilities
- Equipment available
- Institutional resources

### Data Management Plan
[NSF-specific requirements]

### Postdoctoral Mentoring Plan (if applicable)
[If postdocs are on the project]

---
*Generated for {self.agency}*
*Submission Date: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    def review_proposal(self, content: str) -> Dict:
        """Review proposal against quality criteria."""
        checklist = {
            "Specific Aims": {
                "One page only": None,
                "Clear hypothesis stated": None,
                "Aims are independent but related": None,
                "Expected outcomes specified": None
            },
            "Significance": {
                "Gap in knowledge identified": None,
                "Importance to field explained": None,
                "Impact statements are specific": None
            },
            "Innovation": {
                "Novelty clearly stated": None,
                "Distinction from existing work": None
            },
            "Approach": {
                "Adequate preliminary data": None,
                "Appropriate controls described": None,
                "Potential pitfalls addressed": None,
                "Alternative approaches proposed": None,
                "Statistical methods appropriate": None
            },
            "Budget": {
                "All items justified": None,
                "Costs are reasonable": None,
                "Multi-year budget appropriate": None
            }
        }
        
        # Automated checks (basic)
        content_lower = content.lower()
        
        if "specific aims" in content_lower:
            # Rough page estimate based on word count
            aims_section = content_lower.split("specific aims")[1].split("#")[0] \
                          if len(content_lower.split("specific aims")) > 1 else ""
            word_count = len(aims_section.split())
            checklist["Specific Aims"]["One page only"] = word_count < 600  # Rough estimate
            checklist["Specific Aims"]["Clear hypothesis stated"] = \
                "hypothesis" in aims_section
        
        if "significance" in content_lower:
            sig_section = content_lower.split("significance")[1].split("#")[0] \
                         if len(content_lower.split("significance")) > 1 else ""
            checklist["Significance"]["Gap in knowledge identified"] = \
                any(term in sig_section for term in ["gap", "unknown", "unclear", "limited understanding"])
        
        if "approach" in content_lower:
            app_section = content_lower.split("approach")[1].split("#")[0] \
                         if len(content_lower.split("approach")) > 1 else ""
            checklist["Approach"]["Potential pitfalls addressed"] = \
                "pitfall" in app_section or "alternative" in app_section
        
        return {
            "checklist": checklist,
            "word_count": len(content.split()),
            "estimated_pages": len(content.split()) // 500,
            "suggestions": self._generate_suggestions(checklist)
        }
    
    def _generate_suggestions(self, checklist: Dict) -> List[str]:
        """Generate improvement suggestions based on checklist."""
        suggestions = []
        
        for section, items in checklist.items():
            for criterion, passed in items.items():
                if passed is False:
                    suggestions.append(f"[{section}] {criterion}: Needs attention")
                elif passed is None:
                    suggestions.append(f"[{section}] {criterion}: Could not verify")
        
        return suggestions


def main():
    parser = argparse.ArgumentParser(
        description="Grant Proposal Assistant - Generate and review grant proposals"
    )
    parser.add_argument("--section", "-s", 
                       choices=["aims", "specific_aims", "significance", "innovation",
                               "approach", "budget", "full", "project_summary", 
                               "project_description"],
                       help="Section to generate")
    parser.add_argument("--agency", "-a", default="NIH",
                       choices=["NIH", "NSF", "DOD", "VA"],
                       help="Funding agency")
    parser.add_argument("--type", "-t", default="R01",
                       help="Grant type (R01, R21, R03, etc.)")
    parser.add_argument("--category", "-c",
                       choices=["personnel", "equipment", "supplies", "travel", "other", "all"],
                       default="all",
                       help="Budget category")
    parser.add_argument("--review", "-r", action="store_true",
                       help="Review existing proposal")
    parser.add_argument("--input", "-i",
                       help="Input file for review")
    parser.add_argument("--output", "-o",
                       help="Output file path")
    parser.add_argument("--num-aims", "-n", type=int, default=3,
                       help="Number of specific aims (default: 3)")
    
    args = parser.parse_args()
    
    assistant = GrantProposalAssistant(args.agency, args.type)
    
    # Review mode
    if args.review:
        if not args.input:
            print("Error: --input required for review mode", file=sys.stderr)
            sys.exit(1)
        
        content = Path(args.input).read_text()
        result = assistant.review_proposal(content)
        
        output = f"""# PROPOSAL REVIEW REPORT

## Statistics
- Word Count: {result['word_count']}
- Estimated Pages: {result['estimated_pages']}

## Checklist Results

"""
        for section, items in result['checklist'].items():
            output += f"### {section}\n"
            for criterion, passed in items.items():
                status = "✅" if passed else ("❌" if passed is False else "⚠️")
                output += f"- {status} {criterion}\n"
            output += "\n"
        
        if result['suggestions']:
            output += "## Suggestions for Improvement\n\n"
            for suggestion in result['suggestions']:
                output += f"- {suggestion}\n"
        
        if args.output:
            Path(args.output).write_text(output)
            print(f"Review report saved to: {args.output}")
        else:
            print(output)
        
        return
    
    # Generation mode
    if not args.section:
        print("Error: --section required (or use --review)", file=sys.stderr)
        sys.exit(1)
    
    # Generate content
    content = assistant.generate_section(args.section, num_aims=args.num_aims)
    
    # Output
    if args.output:
        Path(args.output).write_text(content)
        print(f"Generated {args.section} section saved to: {args.output}")
    else:
        print(content)


if __name__ == "__main__":
    main()
