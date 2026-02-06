#!/usr/bin/env python3
"""Recommendation Letter Assistant - Helps draft LORs for medical trainees."""

import json
from typing import Dict, List

class RecommendationLetterAssistant:
    """Generates recommendation letter drafts."""
    
    OPENINGS = {
        "mentor": "It is with great enthusiasm that I write to recommend {name} for {context}.",
        "course_director": "I am pleased to provide this letter of recommendation for {name}, whom I taught in {course}.",
        "research_PI": "I am writing to strongly endorse {name} for {context} based on their research work in my laboratory."
    }
    
    CLOSINGS = {
        "strong": "I give {name} my highest recommendation without reservation.",
        "standard": "I recommend {name} for your program and believe they will be an excellent addition.",
        "enthusiastic": "I enthusiastically recommend {name} and would welcome them as a colleague."
    }
    
    COMPETENCY_PHRASES = {
        "clinical skills": "demonstrated excellent clinical acumen and patient care skills",
        "work ethic": "consistently showed exceptional dedication and reliability",
        "teamwork": "worked effectively as part of the healthcare team",
        "communication": "communicated clearly with patients, families, and colleagues",
        "research": "produced high-quality research with strong analytical skills",
        "leadership": "demonstrated leadership potential and initiative",
        "professionalism": "conducted themselves with the highest level of professionalism"
    }
    
    def generate(self, name: str, relationship: str, duration: str, 
                 strengths: List[str], context: str = "residency") -> Dict:
        """Generate recommendation letter draft."""
        
        # Opening
        opening_template = self.OPENINGS.get(relationship, self.OPENINGS["mentor"])
        opening = opening_template.format(name=name, context=context)
        
        # Body paragraphs
        body = []
        
        # Introduction paragraph
        intro = f"I have known {name} for {duration} in my capacity as their {relationship.replace('_', ' ')}."
        body.append(intro)
        
        # Strengths paragraph
        strength_sentences = []
        for strength in strengths[:4]:
            phrase = self.COMPETENCY_PHRASES.get(strength.lower(), f"excelled in {strength}")
            strength_sentences.append(f"{name} {phrase}")
        
        if strength_sentences:
            body.append(" ".join(strength_sentences) + ".")
        
        # Comparison/standout paragraph
        standout = f"{name} ranks among the top students/residents I have worked with during my career."
        body.append(standout)
        
        # Closing
        closing = self.CLOSINGS["enthusiastic"].format(name=name)
        
        # Full letter
        letter = f"{opening}\n\n" + "\n\n".join(body) + f"\n\n{closing}"
        
        return {
            "letter_draft": letter,
            "opening": opening,
            "body_paragraphs": body,
            "closing": closing,
            "competencies_addressed": strengths,
            "relationship": relationship,
            "context": context
        }

def main():
    import sys
    assistant = RecommendationLetterAssistant()
    
    name = sys.argv[1] if len(sys.argv) > 1 else "Jane Smith"
    result = assistant.generate(
        name=name,
        relationship="mentor",
        duration="2 years",
        strengths=["clinical skills", "work ethic", "teamwork"],
        context="residency"
    )
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
