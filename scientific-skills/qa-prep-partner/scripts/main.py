#!/usr/bin/env python3
"""
Q&A Prep Partner
Predict presentation questions and prepare responses.
"""

import argparse
import random


class QAPrepPartner:
    """Prepare for presentation Q&A."""
    
    QUESTION_TEMPLATES = {
        "methodology": [
            "Can you elaborate on your {method} approach?",
            "Why did you choose {method} over alternatives?",
            "How did you validate your {method}?",
            "What are the limitations of using {method}?"
        ],
        "statistics": [
            "Was your sample size adequately powered?",
            "Did you correct for multiple comparisons?",
            "Can you explain the statistical significance of your findings?",
            "What was your effect size?"
        ],
        "interpretation": [
            "How do you interpret these findings in context of {field}?",
            "Are your results generalizable to {population}?",
            "What is the clinical significance of these results?",
            "How do you explain the {observation}?"
        ],
        "limitations": [
            "What are the main limitations of this study?",
            "How might {limitation} affect your conclusions?",
            "What biases might be present in your data?",
            "What couldn't you measure or control?"
        ],
        "future": [
            "What are the next steps for this research?",
            "How do you plan to follow up on these findings?",
            "What would you do differently if you started over?",
            "What unanswered questions remain?"
        ],
        "comparison": [
            "How do your results compare to {previous_work}?",
            "Why do your findings differ from {other_study}?",
            "How does this advance beyond {prior_art}?"
        ]
    }
    
    RESPONSE_FRAMEWORKS = {
        "methodology": "1. Acknowledge the question\n2. Explain rationale\n3. Describe validation\n4. Note limitations",
        "statistics": "1. Confirm the analysis\n2. State the numbers\n3. Explain significance\n4. Note assumptions",
        "interpretation": "1. Restate key finding\n2. Provide context\n3. Address nuance\n4. Acknowledge uncertainty",
        "limitations": "1. Acknowledge limitation\n2. Explain impact\n3. Describe mitigation\n4. Suggest future improvement",
        "future": "1. Summarize current work\n2. Propose next steps\n3. Describe timeline\n4. State expected impact",
        "comparison": "1. Acknowledge prior work\n2. Highlight key differences\n3. Explain your contribution\n4. Discuss implications"
    }
    
    def generate_questions(self, topic, field, audience, n=10):
        """Generate predicted questions."""
        questions = []
        
        # Select categories based on audience
        if audience == "experts":
            categories = ["methodology", "statistics", "comparison", "limitations"]
        elif audience == "peers":
            categories = ["methodology", "interpretation", "future", "limitations"]
        else:  # general
            categories = ["interpretation", "future", "limitations"]
        
        for i in range(n):
            category = random.choice(categories)
            template = random.choice(self.QUESTION_TEMPLATES[category])
            
            question = template.format(
                method="proposed method",
                field=field,
                population="broader populations",
                observation="unexpected finding",
                limitation="sample size",
                previous_work="Smith et al. 2023",
                other_study="previous research"
            )
            
            questions.append({
                "number": i + 1,
                "category": category,
                "question": question,
                "framework": self.RESPONSE_FRAMEWORKS[category]
            })
        
        return questions
    
    def print_prep_guide(self, questions):
        """Print preparation guide."""
        print("\n" + "="*70)
        print("Q&A PREPARATION GUIDE")
        print("="*70)
        
        for q in questions:
            print(f"\n{q['number']}. [{q['category'].upper()}]")
            print(f"Q: {q['question']}")
            print(f"\nResponse Framework:")
            for line in q['framework'].split('\n'):
                print(f"  {line}")
            print("-"*70)


def main():
    parser = argparse.ArgumentParser(description="Q&A Prep Partner")
    parser.add_argument("--abstract", "-a", help="Abstract text or file")
    parser.add_argument("--topic", "-t", help="Research topic")
    parser.add_argument("--field", "-f", default="general",
                       help="Research field")
    parser.add_argument("--audience", choices=["general", "peers", "experts"],
                       default="peers", help="Audience type")
    parser.add_argument("--n-questions", "-n", type=int, default=10,
                       help="Number of questions")
    
    args = parser.parse_args()
    
    partner = QAPrepPartner()
    
    topic = args.topic or "your research"
    if args.abstract:
        try:
            with open(args.abstract) as f:
                topic = f.read()[:100] + "..."
        except:
            topic = args.abstract[:100]
    
    questions = partner.generate_questions(
        topic, args.field, args.audience, args.n_questions
    )
    
    partner.print_prep_guide(questions)
    
    print(f"\n✓ Generated {len(questions)} potential questions")
    print(f"✓ Audience: {args.audience}")
    print(f"✓ Field: {args.field}")
    print("\nTip: Practice your responses out loud!")


if __name__ == "__main__":
    main()
