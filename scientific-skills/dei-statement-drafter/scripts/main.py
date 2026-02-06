#!/usr/bin/env python3
"""
DEI Statement Drafter
Draft Diversity, Equity, and Inclusion statements.
"""

import argparse


class DEIDrafter:
    """Draft DEI statements."""
    
    TEMPLATES = {
        "faculty": {
            "sections": [
                "Personal Background and Perspective",
                "Teaching and Mentoring",
                "Research and Scholarship",
                "Service and Community Engagement",
                "Future Commitments"
            ],
            "prompts": {
                "background": "How has your background shaped your perspective on diversity?",
                "teaching": "How do you create inclusive classroom environments?",
                "research": "How does your research address diversity and equity?",
                "service": "What DEI service activities have you participated in?",
                "future": "What are your specific plans for advancing DEI?"
            }
        },
        "postdoc": {
            "sections": [
                "Background and Values",
                "Past DEI Efforts",
                "Future Goals"
            ],
            "prompts": {
                "background": "What informs your commitment to diversity?",
                "past": "Describe your DEI-related activities",
                "future": "How will you contribute to DEI as a postdoc?"
            }
        },
        "grant": {
            "sections": [
                "Project Overview",
                "Diversity Recruitment",
                "Inclusive Research Environment",
                "Broader Impacts"
            ],
            "prompts": {
                "overview": "How does this project advance diversity in STEM?",
                "recruitment": "How will you recruit diverse participants?",
                "environment": "How will you ensure an inclusive research environment?",
                "impacts": "What are the broader impacts on diverse communities?"
            }
        }
    }
    
    def draft_statement(self, template_type, experiences=None):
        """Draft DEI statement from template."""
        template = self.TEMPLATES.get(template_type, self.TEMPLATES["faculty"])
        
        statement = []
        statement.append("DIVERSITY, EQUITY, AND INCLUSION STATEMENT\n")
        statement.append("=" * 70 + "\n")
        
        for section in template["sections"]:
            statement.append(f"\n{section.upper()}")
            statement.append("-" * len(section))
            
            # Add guidance based on section
            if "Background" in section or "Perspective" in section:
                statement.append("[Share your personal journey and values related to diversity]")
            elif "Teaching" in section:
                statement.append("[Describe inclusive teaching practices and mentoring approach]")
            elif "Research" in section:
                statement.append("[Explain how your research addresses equity and inclusion]")
            elif "Service" in section:
                statement.append("[List DEI-related service activities and their impact]")
            elif "Future" in section or "Commitments" in section:
                statement.append("[Outline specific, actionable future DEI goals]")
            else:
                statement.append("[Add relevant content for this section]")
            
            statement.append("")
        
        if experiences:
            statement.append("\nDEI EXPERIENCES TO HIGHLIGHT:")
            statement.append("-" * 40)
            statement.append(experiences)
        
        return "\n".join(statement)
    
    def print_best_practices(self):
        """Print DEI statement best practices."""
        print("\n" + "=" * 70)
        print("DEI STATEMENT BEST PRACTICES")
        print("=" * 70)
        print("""
1. BE SPECIFIC
   - Give concrete examples, not just general commitments
   - Include metrics and outcomes where possible

2. BE AUTHENTIC
   - Share genuine experiences and perspectives
   - Avoid performative language

3. BE ACTION-ORIENTED
   - Focus on what you have done and will do
   - Include timelines and measurable goals

4. ADDRESS MULTIPLE DIMENSIONS
   - Race, gender, socioeconomic status
   - Disability, LGBTQ+ inclusion
   - First-generation students, veterans

5. CONNECT TO YOUR WORK
   - Teaching: inclusive pedagogies
   - Research: diverse perspectives in scholarship
   - Service: institutional change efforts

6. SHOW GROWTH
   - Acknowledge ongoing learning
   - Demonstrate commitment to improvement
""")
        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="DEI Statement Drafter")
    parser.add_argument("--template", "-t", choices=["faculty", "postdoc", "grant"],
                       default="faculty", help="Statement template")
    parser.add_argument("--experiences", "-e", help="File with DEI experiences")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--best-practices", "-b", action="store_true",
                       help="Show best practices")
    
    args = parser.parse_args()
    
    drafter = DEIDrafter()
    
    if args.best_practices:
        drafter.print_best_practices()
        return
    
    # Load experiences if provided
    experiences = None
    if args.experiences:
        with open(args.experiences) as f:
            experiences = f.read()
    
    # Draft statement
    statement = drafter.draft_statement(args.template, experiences)
    
    print(statement)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(statement)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
