#!/usr/bin/env python3
"""
WB Troubleshooter
Western Blot troubleshooting guide with step-by-step solutions.
"""

import argparse


class WBTroubleshooter:
    """Troubleshoot Western Blot problems."""
    
    PROBLEMS = {
        "no_bands": {
            "symptoms": ["No visible bands", "Blank membrane"],
            "causes": [
                "Primary antibody too dilute",
                "Protein not transferred",
                "Secondary antibody inactive",
                "ECL reagent expired"
            ],
            "solutions": [
                "Optimize antibody concentration",
                "Check transfer with Ponceau stain",
                "Use fresh secondary antibody",
                "Prepare fresh ECL"
            ]
        },
        "high_background": {
            "symptoms": ["High background", "Non-specific bands"],
            "causes": [
                "Insufficient blocking",
                "Antibody too concentrated",
                "Insufficient washing",
                "Non-specific antibody binding"
            ],
            "solutions": [
                "Increase blocking time",
                "Dilute antibody further",
                "Increase wash steps",
                "Use affinity-purified antibody"
            ]
        },
        "multiple_bands": {
            "symptoms": ["Unexpected bands", "Degradation products"],
            "causes": [
                "Protein degradation",
                "Non-specific antibody binding",
                "Post-translational modifications",
                "Isoforms present"
            ],
            "solutions": [
                "Add protease inhibitors",
                "Use blocking peptide",
                "Check for PTMs",
                "Verify isoform specificity"
            ]
        }
    }
    
    def diagnose(self, symptom):
        """Diagnose problem based on symptom."""
        matches = []
        
        for problem_id, data in self.PROBLEMS.items():
            if any(s.lower() in symptom.lower() for s in data["symptoms"]):
                matches.append({"id": problem_id, **data})
        
        return matches
    
    def print_diagnosis(self, matches):
        """Print diagnosis and solutions."""
        if not matches:
            print("No specific troubleshooting guide found for this symptom.")
            return
        
        for match in matches:
            print(f"\n{'='*60}")
            print(f"DIAGNOSIS: {match['id'].replace('_', ' ').title()}")
            print(f"{'='*60}\n")
            
            print("Likely Causes:")
            for cause in match["causes"]:
                print(f"  • {cause}")
            
            print("\nRecommended Solutions:")
            for solution in match["solutions"]:
                print(f"  • {solution}")


def main():
    parser = argparse.ArgumentParser(description="WB Troubleshooter")
    parser.add_argument("--symptom", "-s", required=True, help="Problem symptom")
    parser.add_argument("--list", action="store_true", help="List known problems")
    
    args = parser.parse_args()
    
    troubleshooter = WBTroubleshooter()
    
    if args.list:
        print("Known WB problems:")
        for pid in troubleshooter.PROBLEMS.keys():
            print(f"  - {pid.replace('_', ' ')}")
        return
    
    matches = troubleshooter.diagnose(args.symptom)
    troubleshooter.print_diagnosis(matches)


if __name__ == "__main__":
    main()
