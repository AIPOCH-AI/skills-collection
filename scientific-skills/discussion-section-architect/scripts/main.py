#!/usr/bin/env python3
"""
Discussion Section Architect
Guided framework for structuring academic Discussion sections.
"""

import argparse


class DiscussionArchitect:
    """Guide writing of academic Discussion sections."""
    
    STRUCTURE_TEMPLATE = {
        "opening": {
            "title": "Summary of Key Findings",
            "prompts": [
                "Restate your main findings in 2-3 sentences",
                "Connect findings to your original research question",
                "Highlight the most significant result"
            ]
        },
        "literature": {
            "title": "Comparison with Existing Literature",
            "prompts": [
                "How do your findings compare to previous studies?",
                "Do your results confirm or contradict prior work?",
                "What new insights do you provide?"
            ]
        },
        "mechanism": {
            "title": "Mechanistic Interpretation",
            "prompts": [
                "What biological/physical mechanisms explain your findings?",
                "Provide rationale for observed effects",
                "Connect to underlying theory"
            ]
        },
        "limitations": {
            "title": "Study Limitations",
            "prompts": [
                "What are the main limitations of your study?",
                "How might these limitations affect interpretation?",
                "Be honest but don't undermine your work"
            ]
        },
        "implications": {
            "title": "Clinical/Research Implications",
            "prompts": [
                "What are the practical applications of your findings?",
                "How might this change clinical practice?",
                "What is the significance for the field?"
            ]
        },
        "future": {
            "title": "Future Directions",
            "prompts": [
                "What questions remain unanswered?",
                "What are the logical next steps?",
                "Suggest specific follow-up studies"
            ]
        }
    }
    
    def generate_outline(self, findings, include_sections=None):
        """Generate Discussion section outline."""
        if include_sections is None:
            include_sections = list(self.STRUCTURE_TEMPLATE.keys())
        
        outline = []
        outline.append("DISCUSSION SECTION OUTLINE")
        outline.append("="*70)
        outline.append("")
        
        for section_key in include_sections:
            if section_key in self.STRUCTURE_TEMPLATE:
                section = self.STRUCTURE_TEMPLATE[section_key]
                outline.append(f"\n{section['title'].upper()}")
                outline.append("-"*50)
                
                for prompt in section['prompts']:
                    outline.append(f"  • {prompt}")
                
                outline.append("")
                outline.append("  [Write your content here]")
                outline.append("")
        
        return "\n".join(outline)
    
    def generate_transitions(self):
        """Provide transition phrase suggestions."""
        transitions = {
            "summary_to_literature": [
                "These findings are consistent with...",
                "Our results align with previous studies showing...",
                "In contrast to earlier work..."
            ],
            "literature_to_mechanism": [
                "The mechanism underlying this observation may be...",
                "These effects can be explained by...",
                "One possible explanation is..."
            ],
            "mechanism_to_limitations": [
                "Despite these insights, several limitations should be noted...",
                "However, this interpretation is subject to certain constraints...",
                "It is important to acknowledge..."
            ],
            "limitations_to_implications": [
                "Nevertheless, our findings have important implications...",
                "Despite these limitations, this work demonstrates...",
                "These results suggest that..."
            ]
        }
        return transitions


def main():
    parser = argparse.ArgumentParser(description="Discussion Section Architect")
    parser.add_argument("--findings", "-f", help="Key findings to discuss")
    parser.add_argument("--sections", "-s", help="Sections to include (comma-separated)")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--transitions", "-t", action="store_true",
                       help="Show transition phrases")
    
    args = parser.parse_args()
    
    architect = DiscussionArchitect()
    
    if args.transitions:
        print("\n" + "="*70)
        print("SUGGESTED TRANSITION PHRASES")
        print("="*70)
        transitions = architect.generate_transitions()
        for section, phrases in transitions.items():
            print(f"\n{section.replace('_', ' ').title()}:")
            for phrase in phrases:
                print(f"  • {phrase}")
        print("="*70 + "\n")
        return
    
    sections = None
    if args.sections:
        sections = [s.strip() for s in args.sections.split(",")]
    
    outline = architect.generate_outline(args.findings, sections)
    
    print("\n" + outline)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(outline)
        print(f"\nOutline saved to: {args.output}")


if __name__ == "__main__":
    main()
