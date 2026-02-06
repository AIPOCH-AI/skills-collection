#!/usr/bin/env python3
"""
Rebuttal Letter Strategist
Strategic response drafting for sharp reviewer criticisms.
"""

import argparse


class RebuttalStrategist:
    """Draft strategic rebuttal responses."""
    
    RESPONSE_TEMPLATES = {
        "minor": {
            "tone": "appreciative",
            "strategy": "Accept and thank",
            "template": "We thank the reviewer for this insightful comment. We have revised the manuscript accordingly."
        },
        "moderate": {
            "tone": "constructive",
            "strategy": "Acknowledge and clarify",
            "template": "We appreciate this important point. We have now clarified this in the revised manuscript."
        },
        "major": {
            "tone": "diplomatic",
            "strategy": "Address with evidence",
            "template": "We respectfully address this concern by [specific action/explanation]."
        },
        "harsh": {
            "tone": "professional",
            "strategy": "De-escalate and redirect",
            "template": "We appreciate the reviewer's critical assessment. We have carefully considered this and [response]."
        }
    }
    
    def analyze_criticism(self, criticism):
        """Analyze severity of criticism."""
        harsh_words = ["fundamentally", "seriously", "severely", "major", "critical", "flawed"]
        
        criticism_lower = criticism.lower()
        harsh_count = sum(1 for word in harsh_words if word in criticism_lower)
        
        if harsh_count >= 2:
            return "harsh"
        elif harsh_count == 1 or "significant" in criticism_lower:
            return "major"
        elif "unclear" in criticism_lower or "should" in criticism_lower:
            return "moderate"
        else:
            return "minor"
    
    def draft_response(self, criticism, revision_made):
        """Draft response to criticism."""
        severity = self.analyze_criticism(criticism)
        template = self.RESPONSE_TEMPLATES[severity]
        
        response = template["template"].replace("[specific action/explanation]", revision_made)
        response = response.replace("[response]", revision_made)
        
        return {
            "severity": severity,
            "tone": template["tone"],
            "strategy": template["strategy"],
            "response": response
        }


def main():
    parser = argparse.ArgumentParser(description="Rebuttal Letter Strategist")
    parser.add_argument("--criticism", "-c", required=True, help="Reviewer criticism")
    parser.add_argument("--revision", "-r", required=True, help="How you addressed it")
    
    args = parser.parse_args()
    
    strategist = RebuttalStrategist()
    
    result = strategist.draft_response(args.criticism, args.revision)
    
    print(f"\n{'='*60}")
    print("REBUTTAL STRATEGY")
    print(f"{'='*60}\n")
    
    print(f"Criticism severity: {result['severity'].upper()}")
    print(f"Recommended tone: {result['tone']}")
    print(f"Strategy: {result['strategy']}")
    print()
    print("Suggested response:")
    print(f"  {result['response']}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
