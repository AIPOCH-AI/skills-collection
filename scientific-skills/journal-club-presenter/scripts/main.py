#!/usr/bin/env python3
"""
Journal Club Presenter
Generate journal club slides with background, critique, and discussion.
"""

import argparse
from datetime import datetime


class JournalClubPresenter:
    """Generate journal club presentation content."""
    
    def generate_structure(self, paper_info):
        """Generate journal club presentation structure."""
        slides = []
        
        # Title slide
        slides.append("="*70)
        slides.append("SLIDE 1: TITLE")
        slides.append("-"*70)
        slides.append(f"Paper: {paper_info.get('title', '[Paper Title]')}")
        slides.append(f"Authors: {paper_info.get('authors', '[Authors]')}")
        slides.append(f"Journal: {paper_info.get('journal', '[Journal]')} ({paper_info.get('year', '[Year]')})")
        slides.append(f"Presenter: {paper_info.get('presenter', '[Your Name]')}")
        slides.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        slides.append("")
        
        # Background
        slides.append("="*70)
        slides.append("SLIDE 2: BACKGROUND")
        slides.append("-"*70)
        slides.append("Key Points:")
        slides.append("  • What is the scientific problem?")
        slides.append("  • Why is it important?")
        slides.append("  • What is the current state of knowledge?")
        slides.append("  • What gap does this study address?")
        slides.append("")
        slides.append(f"[Add: {paper_info.get('background', 'Background context')}]")
        slides.append("")
        
        # Research Question
        slides.append("="*70)
        slides.append("SLIDE 3: RESEARCH QUESTION & HYPOTHESIS")
        slides.append("-"*70)
        slides.append("Main Question:")
        slides.append(f"  {paper_info.get('research_question', '[Research question]')}")
        slides.append("")
        slides.append("Hypothesis:")
        slides.append(f"  {paper_info.get('hypothesis', '[Hypothesis]')}")
        slides.append("")
        
        # Methods
        slides.append("="*70)
        slides.append("SLIDE 4: METHODS OVERVIEW")
        slides.append("-"*70)
        slides.append("Study Design:")
        slides.append(f"  {paper_info.get('design', '[Study design]')}")
        slides.append("")
        slides.append("Key Methods:")
        slides.append("  • [Method 1]")
        slides.append("  • [Method 2]")
        slides.append("  • [Method 3]")
        slides.append("")
        
        # Results
        slides.append("="*70)
        slides.append("SLIDE 5: KEY RESULTS")
        slides.append("-"*70)
        slides.append("Main Findings:")
        slides.append("  1. [First key result]")
        slides.append("  2. [Second key result]")
        slides.append("  3. [Third key result]")
        slides.append("")
        slides.append("[Include representative figures/tables]")
        slides.append("")
        
        # Critique
        slides.append("="*70)
        slides.append("SLIDE 6: CRITIQUE - STRENGTHS")
        slides.append("-"*70)
        slides.append("Strengths:")
        slides.append("  ✓ [Strength 1]")
        slides.append("  ✓ [Strength 2]")
        slides.append("  ✓ [Strength 3]")
        slides.append("")
        
        slides.append("="*70)
        slides.append("SLIDE 7: CRITIQUE - WEAKNESSES")
        slides.append("-"*70)
        slides.append("Limitations:")
        slides.append("  ⚠ [Limitation 1]")
        slides.append("  ⚠ [Limitation 2]")
        slides.append("  ⚠ [Limitation 3]")
        slides.append("")
        
        # Discussion Questions
        slides.append("="*70)
        slides.append("SLIDE 8: DISCUSSION QUESTIONS")
        slides.append("-"*70)
        slides.append("Questions for Discussion:")
        slides.append("  1. What are the implications of these findings?")
        slides.append("  2. How does this compare to previous work?")
        slides.append("  3. What would you do differently?")
        slides.append("  4. What are the next steps?")
        slides.append("  5. How does this relate to your own research?")
        slides.append("")
        
        # Take-home
        slides.append("="*70)
        slides.append("SLIDE 9: TAKE-HOME MESSAGE")
        slides.append("-"*70)
        slides.append("Key Points:")
        slides.append("  1. [Main takeaway]")
        slides.append("  2. [Clinical/scientific significance]")
        slides.append("  3. [Future directions]")
        slides.append("")
        slides.append("="*70)
        
        return "\n".join(slides)


def main():
    parser = argparse.ArgumentParser(description="Journal Club Presenter")
    parser.add_argument("--title", "-t", required=True, help="Paper title")
    parser.add_argument("--authors", "-a", help="Authors")
    parser.add_argument("--journal", "-j", help="Journal name")
    parser.add_argument("--year", "-y", help="Publication year")
    parser.add_argument("--presenter", "-p", help="Presenter name")
    parser.add_argument("--output", "-o", default="journal_club_outline.txt", help="Output file")
    
    args = parser.parse_args()
    
    presenter = JournalClubPresenter()
    
    paper_info = {
        "title": args.title,
        "authors": args.authors or "[Authors]",
        "journal": args.journal or "[Journal]",
        "year": args.year or "[Year]",
        "presenter": args.presenter or "[Your Name]"
    }
    
    outline = presenter.generate_structure(paper_info)
    print(outline)
    
    with open(args.output, 'w') as f:
        f.write(outline)
    print(f"\nOutline saved to: {args.output}")


if __name__ == "__main__":
    main()
