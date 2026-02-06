#!/usr/bin/env python3
"""
Study Limitations Drafter
Transform study design flaws into professional limitation statements.
"""

import argparse


class LimitationsDrafter:
    """Draft study limitations sections."""
    
    LIMITATION_TEMPLATES = {
        "sample_size": {
            "issue": "Small sample size",
            "statement": "The sample size in this study was limited, which may have reduced statistical power to detect smaller effects."
        },
        "retrospective": {
            "issue": "Retrospective design",
            "statement": "The retrospective nature of this study introduces potential selection bias and limits causal inference."
        },
        "single_center": {
            "issue": "Single-center study",
            "statement": "Findings from this single-center study may not generalize to other populations or healthcare settings."
        },
        "short_followup": {
            "issue": "Short follow-up",
            "statement": "The relatively short follow-up period limits assessment of long-term outcomes and delayed effects."
        },
        "missing_data": {
            "issue": "Missing data",
            "statement": "Missing data for some variables may have introduced bias, though we employed appropriate imputation methods."
        }
    }
    
    def generate_limitations(self, issues):
        """Generate limitations section."""
        sections = []
        
        sections.append("STUDY LIMITATIONS")
        sections.append("-"*60)
        sections.append("")
        
        for issue in issues:
            if issue in self.LIMITATION_TEMPLATES:
                template = self.LIMITATION_TEMPLATES[issue]
                sections.append(f"• {template['statement']}")
                sections.append("")
        
        sections.append("Despite these limitations, this study provides valuable insights...")
        
        return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Study Limitations Drafter")
    parser.add_argument("--issues", "-i", required=True, 
                       help="Comma-separated limitation types")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    drafter = LimitationsDrafter()
    
    issues = [i.strip() for i in args.issues.split(",")]
    
    text = drafter.generate_limitations(issues)
    print(text)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(text)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
