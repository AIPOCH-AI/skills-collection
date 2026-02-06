#!/usr/bin/env python3
"""
Methodology Extractor
Batch extraction of experimental methods from multiple papers for protocol comparison.
"""

import argparse
import json
from collections import defaultdict


class MethodologyExtractor:
    """Extract and compare methodologies from papers."""
    
    def __init__(self):
        self.methods = defaultdict(list)
    
    def extract_from_paper(self, paper_id, text):
        """Extract methods section from paper text."""
        # Simple extraction - look for Methods section
        lines = text.split('\n')
        in_methods = False
        methods_text = []
        
        for line in lines:
            line_lower = line.lower().strip()
            if 'methods' in line_lower or 'materials and methods' in line_lower:
                in_methods = True
                continue
            if in_methods and any(h in line_lower for h in ['results', 'discussion', 'references']):
                break
            if in_methods:
                methods_text.append(line)
        
        return '\n'.join(methods_text)
    
    def identify_protocol_steps(self, methods_text):
        """Identify key protocol steps."""
        steps = []
        
        # Look for numbered or bulleted steps
        lines = methods_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', 'Step', '•', '-')):
                steps.append(line)
        
        return steps
    
    def compare_protocols(self, papers_data):
        """Compare protocols across papers."""
        comparison = {
            "common_steps": [],
            "unique_steps": defaultdict(list),
            "variations": defaultdict(list)
        }
        
        all_steps = defaultdict(set)
        
        for paper_id, data in papers_data.items():
            methods = data.get("methods", "")
            steps = self.identify_protocol_steps(methods)
            
            for step in steps:
                all_steps[step].add(paper_id)
        
        # Find common and unique steps
        for step, papers in all_steps.items():
            if len(papers) > 1:
                comparison["common_steps"].append({
                    "step": step,
                    "papers": list(papers)
                })
            else:
                paper = list(papers)[0]
                comparison["unique_steps"][paper].append(step)
        
        return comparison
    
    def print_comparison(self, comparison):
        """Print protocol comparison."""
        print(f"\n{'='*70}")
        print("METHODOLOGY COMPARISON")
        print(f"{'='*70}\n")
        
        print("COMMON STEPS (across multiple papers):")
        print("-"*70)
        for item in comparison["common_steps"]:
            print(f"  • {item['step'][:60]}...")
            print(f"    Found in: {', '.join(item['papers'])}")
        print()
        
        print("UNIQUE STEPS (paper-specific):")
        print("-"*70)
        for paper, steps in comparison["unique_steps"].items():
            print(f"\n  {paper}:")
            for step in steps[:3]:  # Show first 3
                print(f"    - {step[:50]}...")
        
        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Methodology Extractor")
    parser.add_argument("--papers", "-p", help="JSON file with paper data")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    
    extractor = MethodologyExtractor()
    
    if args.demo:
        # Demo data
        papers_data = {
            "Paper1": {
                "methods": "1. Cell culture\n2. RNA extraction\n3. qPCR analysis"
            },
            "Paper2": {
                "methods": "1. Cell culture\n2. Protein extraction\n3. Western blot"
            },
            "Paper3": {
                "methods": "1. Cell culture\n2. RNA extraction\n3. RNA-seq"
            }
        }
        
        comparison = extractor.compare_protocols(papers_data)
        extractor.print_comparison(comparison)
    else:
        print("Use --demo to see example output")


if __name__ == "__main__":
    main()
