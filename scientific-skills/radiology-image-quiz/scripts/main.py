#!/usr/bin/env python3
"""
Radiology Image Quiz
Generate image-based diagnostic quizzes from text descriptions.
"""

import argparse
import json


class RadiologyQuiz:
    """Generate radiology quizzes."""
    
    def generate_quiz(self, cases):
        """Generate quiz from cases."""
        quiz = []
        
        for i, case in enumerate(cases, 1):
            quiz.append(f"CASE {i}")
            quiz.append("-"*60)
            quiz.append(f"History: {case['history']}")
            quiz.append(f"Findings: {case['findings']}")
            quiz.append("")
            quiz.append("What is the most likely diagnosis?")
            
            for j, option in enumerate(case['options'], 1):
                quiz.append(f"  {j}. {option}")
            
            quiz.append("")
            quiz.append(f"Answer: {case['answer']}")
            quiz.append(f"Explanation: {case['explanation']}")
            quiz.append("")
        
        return "\n".join(quiz)


def main():
    parser = argparse.ArgumentParser(description="Radiology Image Quiz")
    parser.add_argument("--cases", "-c", help="JSON file with cases")
    parser.add_argument("--demo", action="store_true", help="Generate demo quiz")
    
    args = parser.parse_args()
    
    quiz_gen = RadiologyQuiz()
    
    if args.demo:
        cases = [
            {
                "history": "65-year-old male with chest pain",
                "findings": "CT shows peripheral wedge-shaped opacity",
                "options": ["Pulmonary embolism", "Pneumonia", "Lung cancer", "Atelectasis"],
                "answer": "Pulmonary embolism",
                "explanation": "Wedge-shaped peripheral opacity is classic for pulmonary infarction"
            }
        ]
    elif args.cases:
        with open(args.cases) as f:
            cases = json.load(f)
    else:
        print("Use --demo or provide --cases file")
        return
    
    quiz = quiz_gen.generate_quiz(cases)
    print(quiz)


if __name__ == "__main__":
    main()
