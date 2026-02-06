#!/usr/bin/env python3
"""
MoA Explainer
Generate 3D animation scripts and lay explanations for drug mechanisms.
"""

import argparse


class MoAExplainer:
    """Explain drug mechanisms of action."""
    
    def generate_script(self, drug_name, mechanism, target):
        """Generate animation script for mechanism."""
        script = []
        
        script.append("="*70)
        script.append(f"3D ANIMATION SCRIPT: {drug_name.upper()}")
        script.append("="*70)
        script.append("")
        
        script.append("SCENE 1: INTRODUCTION")
        script.append("-"*70)
        script.append(f"Show normal cellular environment without {drug_name}")
        script.append(f"Highlight the {target} in its natural state")
        script.append("Duration: 5 seconds")
        script.append("")
        
        script.append("SCENE 2: DISEASE STATE (Optional)")
        script.append("-"*70)
        script.append("Show what happens when target is dysregulated")
        script.append("Visual cues: Color change, erratic movement")
        script.append("Duration: 5 seconds")
        script.append("")
        
        script.append("SCENE 3: DRUG ENTRY")
        script.append("-"*70)
        script.append(f"{drug_name} molecule enters the scene")
        script.append("Show drug approaching target")
        script.append("Visual: Drug highlighted with glow effect")
        script.append("Duration: 3 seconds")
        script.append("")
        
        script.append("SCENE 4: MECHANISM OF ACTION")
        script.append("-"*70)
        script.append(f"{mechanism}")
        script.append("Show binding/interaction in detail")
        script.append("Visual: Conformational changes, bond formation")
        script.append("Duration: 10 seconds")
        script.append("")
        
        script.append("SCENE 5: THERAPEUTIC EFFECT")
        script.append("-"*70)
        script.append("Show downstream effects")
        script.append("Return to normal cellular state")
        script.append("Duration: 5 seconds")
        script.append("")
        
        script.append("SCENE 6: SUMMARY")
        script.append("-"*70)
        script.append("Recap of mechanism")
        script.append("Duration: 3 seconds")
        script.append("")
        
        script.append("="*70)
        
        return "\n".join(script)
    
    def generate_lay_explanation(self, drug_name, mechanism):
        """Generate lay explanation."""
        explanation = f"""
HOW {drug_name.upper()} WORKS (Simplified)

Imagine your body as a busy city with many workers (proteins) doing different jobs.

THE PROBLEM:
Sometimes one of these workers (the {mechanism.split()[0]} target) 
starts working too hard or not hard enough, causing problems.

THE SOLUTION:
{drug_name} acts like a smart key that fits into a specific lock on this worker.
When {drug_name} attaches to the worker, it changes how the worker behaves.

WHAT HAPPENS:
{mechanism}

THE RESULT:
This brings the worker back to normal activity, helping your body function properly.

Think of it like adjusting the volume on a radio - {drug_name} turns it up or down 
to just the right level.
"""
        return explanation


def main():
    parser = argparse.ArgumentParser(description="MoA Explainer")
    parser.add_argument("--drug", "-d", required=True, help="Drug name")
    parser.add_argument("--mechanism", "-m", required=True, help="Mechanism of action")
    parser.add_argument("--target", "-t", required=True, help="Molecular target")
    parser.add_argument("--type", choices=["script", "explanation"], default="script",
                       help="Output type")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    explainer = MoAExplainer()
    
    if args.type == "script":
        text = explainer.generate_script(args.drug, args.mechanism, args.target)
    else:
        text = explainer.generate_lay_explanation(args.drug, args.mechanism)
    
    print(text)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(text)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
