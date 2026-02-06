#!/usr/bin/env python3
"""Residency Interview Preparation - Mock interview trainer for Match."""

import random
import json
from typing import Dict, List

class ResidencyInterviewPrep:
    """Generates residency interview questions and feedback."""
    
    QUESTION_BANK = {
        "behavioral": [
            {
                "question": "Tell me about a time you made a medical error.",
                "structure": "STAR: Situation, Task, Action, Result + reflection",
                "key_points": ["Accountability", "Patient safety priority", "Learning from mistake", "System improvement"],
                "pitfalls": ["Blaming others", "Minimizing the error", "No reflection"]
            },
            {
                "question": "Describe a conflict with a team member and how you resolved it.",
                "structure": "STAR format focusing on communication",
                "key_points": ["Professionalism", "Active listening", "Finding common ground", "Patient-centered outcome"],
                "pitfalls": ["Badmouthing colleague", "Avoiding the conflict", "Not addressing root cause"]
            },
            {
                "question": "Tell me about a time you went above and beyond for a patient.",
                "structure": "Situation + your extra effort + patient outcome",
                "key_points": ["Empathy", "Advocacy", "Going beyond job duties", "Meaningful impact"],
                "pitfalls": ["Generic answer", "No specific outcome", "Seems exaggerated"]
            }
        ],
        "clinical": [
            {
                "question": "A patient refuses your recommended treatment. How do you proceed?",
                "structure": "Assess capacity → Educate → Explore concerns → Shared decision",
                "key_points": ["Respect autonomy", "Ensure understanding", "Address barriers", "Document discussion"],
                "pitfalls": ["Coercion", "Dismissing concerns", "Not offering alternatives"]
            },
            {
                "question": "You suspect a colleague is impaired. What do you do?",
                "structure": "Patient safety first → Gather facts → Report appropriately",
                "key_points": ["Patient safety priority", "Objectivity", "Chain of command", "Support for colleague"],
                "pitfalls": ["Ignoring it", "Confronting directly without facts", "Gossiping"]
            }
        ],
        "program": [
            {
                "question": "Why do you want to train at our program?",
                "structure": "Specific program strengths + your fit + career alignment",
                "key_points": ["Research specific features", "Mission alignment", "Unique opportunities", "Geographic ties"],
                "pitfalls": ["Generic answer", "Only location", "Haven't researched program"]
            }
        ],
        "ethical": [
            {
                "question": "A 17-year-old wants an abortion but doesn't want parents to know. How do you handle this?",
                "structure": "Legal requirements → Ethics → Patient-centered approach",
                "key_points": ["Know state laws", "Minor confidentiality", "Counseling without judgment", "Safety assessment"],
                "pitfalls": ["Personal bias", "Not knowing legal requirements", "Breaking confidentiality improperly"]
            }
        ]
    }
    
    def get_question(self, question_type: str = "behavioral", specialty: str = None) -> Dict:
        """Generate interview question with guidance."""
        questions = self.QUESTION_BANK.get(question_type, self.QUESTION_BANK["behavioral"])
        q = random.choice(questions)
        
        result = {
            "question": q["question"],
            "category": question_type,
            "suggested_structure": q["structure"],
            "key_points": q["key_points"],
            "common_pitfalls": q["pitfalls"]
        }
        
        if specialty:
            result["specialty_consideration"] = f"Consider {specialty}-specific aspects in your answer"
        
        return result
    
    def get_practice_session(self, num_questions: int = 5) -> List[Dict]:
        """Generate a full practice session."""
        types = ["behavioral", "clinical", "program", "ethical", "behavioral"]
        session = []
        
        for i in range(min(num_questions, len(types))):
            session.append(self.get_question(types[i]))
        
        return session

def main():
    import sys
    prep = ResidencyInterviewPrep()
    
    q_type = sys.argv[1] if len(sys.argv) > 1 else "behavioral"
    result = prep.get_question(q_type)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
