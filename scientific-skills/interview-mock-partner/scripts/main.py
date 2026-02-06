#!/usr/bin/env python3
"""Interview Mock Partner - Interview simulation for medical roles."""

import json

class InterviewMockPartner:
    """Simulates medical interviews."""
    
    def get_questions(self, position: str, experience_level: str) -> dict:
        """Generate interview questions."""
        
        questions = [
            "Tell me about a challenging patient case.",
            "How do you handle conflicts with colleagues?",
            "Describe your approach to patient education."
        ]
        
        sample_answers = [
            "I once managed a complex case by...",
            "I believe in open communication...",
            "I use visual aids and simple language..."
        ]
        
        tips = [
            "Use the STAR method",
            "Be specific with examples",
            "Show empathy and professionalism"
        ]
        
        return {
            "questions": questions,
            "sample_answers": sample_answers,
            "tips": tips,
            "position": position
        }

def main():
    mock = InterviewMockPartner()
    result = mock.get_questions("Physician", "mid")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
