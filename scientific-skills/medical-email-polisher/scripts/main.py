#!/usr/bin/env python3
"""Medical Email Polisher - Professional email refinement for medical contexts."""

import json
from typing import Dict, List

class MedicalEmailPolisher:
    """Polishes medical professional emails."""
    
    TEMPLATES = {
        "mentor": {
            "opening": "Dear Dr. {name},",
            "closing": "Thank you for your time and guidance.\n\nBest regards,",
            "tone": "respectful and professional"
        },
        "editor": {
            "opening": "Dear Editor,",
            "closing": "Thank you for considering our submission.\n\nSincerely,",
            "tone": "formal academic"
        },
        "colleague": {
            "opening": "Hi {name},",
            "closing": "Looking forward to your thoughts.\n\nBest,",
            "tone": "professional but friendly"
        },
        "patient": {
            "opening": "Dear {name},",
            "closing": "Please don't hesitate to reach out if you have any questions.\n\nBest regards,",
            "tone": "warm and clear"
        }
    }
    
    def polish(self, draft: str, recipient_type: str, name: str = "") -> Dict:
        """Polish email draft."""
        template = self.TEMPLATES.get(recipient_type, self.TEMPLATES["colleague"])
        
        changes = []
        polished = draft
        
        # Apply template structure if needed
        if not polished.startswith("Dear") and not polished.startswith("Hi"):
            opening = template["opening"].format(name=name) if name else template["opening"]
            polished = f"{opening}\n\n{polished}"
            changes.append("Added professional opening")
        
        # Add closing if missing
        if not any(word in polished.lower()[-200:] for word in ["regards", "sincerely", "best"]):
            polished = f"{polished}\n\n{template['closing']}"
            changes.append("Added professional closing")
        
        # Basic improvements
        polished = self._improve_clarity(polished)
        
        # Generate subject suggestion
        subject = self._suggest_subject(draft)
        
        return {
            "polished_email": polished,
            "subject_line": subject,
            "changes_made": changes,
            "tone_assessment": template["tone"],
            "recipient_type": recipient_type
        }
    
    def _improve_clarity(self, text: str) -> str:
        """Improve text clarity."""
        # Replace informal phrases
        replacements = {
            "hey": "Hello",
            "yeah": "yes",
            "gonna": "going to",
            "wanna": "want to",
            "kinda": "somewhat",
            "thx": "Thank you",
            "pls": "Please"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _suggest_subject(self, draft: str) -> str:
        """Generate subject line suggestion."""
        # Extract key topic
        keywords = ["manuscript", "meeting", "question", "request", "follow-up"]
        draft_lower = draft.lower()
        
        for kw in keywords:
            if kw in draft_lower:
                return f"{kw.capitalize()}: [Brief Description]"
        
        return "[Subject]: [Brief Description]"

def main():
    import sys
    polisher = MedicalEmailPolisher()
    
    draft = sys.argv[1] if len(sys.argv) > 1 else "hey, wanted to follow up on our discussion"
    recipient = sys.argv[2] if len(sys.argv) > 2 else "mentor"
    
    result = polisher.polish(draft, recipient)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
