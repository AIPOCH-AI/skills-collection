#!/usr/bin/env python3
"""Anatomy Quiz Master - Interactive anatomy quiz generator."""

import random
import json
from typing import Dict, List

class AnatomyQuizMaster:
    """Generates anatomy questions for medical education."""
    
    QUESTION_BANK = {
        "upper_limb": [
            {
                "question": "Which nerve is compressed in carpal tunnel syndrome?",
                "options": ["Median nerve", "Ulnar nerve", "Radial nerve", "Musculocutaneous nerve"],
                "correct": "Median nerve",
                "explanation": "The median nerve passes through the carpal tunnel and is compressed by transverse ligament.",
                "clinical": "Patients present with numbness in thumb, index, middle fingers (median nerve distribution)."
            },
            {
                "question": "The rotator cuff consists of all EXCEPT:",
                "options": ["Supraspinatus", "Infraspinatus", "Teres major", "Subscapularis"],
                "correct": "Teres major",
                "explanation": "Rotator cuff = SITS: Supraspinatus, Infraspinatus, Teres minor, Subscapularis.",
                "clinical": "Rotator cuff tears are common in overhead athletes and elderly."
            }
        ],
        "lower_limb": [
            {
                "question": "Which muscle is the primary hip flexor?",
                "options": ["Iliopsoas", "Rectus femoris", "Sartorius", "Tensor fasciae latae"],
                "correct": "Iliopsoas",
                "explanation": "Iliopsoas (iliacus + psoas major) is the strongest hip flexor.",
                "clinical": "Iliopsoas abscess can present with flexed hip posture to reduce pain."
            }
        ],
        "neuroanatomy": [
            {
                "question": "A lesion of the left optic tract results in:",
                "options": ["Right homonymous hemianopia", "Left homonymous hemianopia", "Bitemporal hemianopia", "Total blindness left eye"],
                "correct": "Right homonymous hemianopia",
                "explanation": "Optic tract carries fibers from both eyes for contralateral visual field.",
                "clinical": "Homonymous hemianopia suggests lesion posterior to optic chiasm."
            }
        ],
        "thorax": [
            {
                "question": "The thoracic duct drains lymph into the:",
                "options": ["Left subclavian vein", "Right subclavian vein", "Superior vena cava", "Azygos vein"],
                "correct": "Left subclavian vein",
                "explanation": "Thoracic duct drains most of body, empties at junction of left subclavian and internal jugular.",
                "clinical": "Thoracic duct injury during surgery causes chylothorax."
            }
        ]
    }
    
    def get_question(self, region: str = "upper_limb", difficulty: str = "intermediate") -> Dict:
        """Generate anatomy question."""
        questions = self.QUESTION_BANK.get(region, self.QUESTION_BANK["upper_limb"])
        q = random.choice(questions)
        
        return {
            "question": q["question"],
            "options": q["options"],
            "correct_answer": q["correct"],
            "explanation": q["explanation"],
            "clinical_note": q.get("clinical", ""),
            "difficulty": difficulty,
            "region": region
        }
    
    def list_regions(self) -> List[str]:
        """List available body regions."""
        return list(self.QUESTION_BANK.keys())

def main():
    import sys
    quiz = AnatomyQuizMaster()
    
    region = sys.argv[1] if len(sys.argv) > 1 else "upper_limb"
    result = quiz.get_question(region)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
