#!/usr/bin/env python3
"""Cover Letter Drafter - Professional cover letter generator."""

import json
from typing import Dict, List

class CoverLetterDrafter:
    """Generates cover letters for academic and medical contexts."""
    
    TEMPLATES = {
        "journal": """Dear Editor,

I am pleased to submit our manuscript titled "{title}" for consideration for publication in {journal}.

{key_points}

This work represents {significance}. We believe it aligns with the scope and readership of your journal.

Thank you for your consideration.

Sincerely,
{author}""",
        "job": """Dear Hiring Committee,

I am writing to express my strong interest in the {position} position at {institution}.

{key_points}

I am excited about the opportunity to contribute to your team.

Thank you for your consideration.

Sincerely,
{applicant}"""
    }
    
    def draft(self, purpose: str, recipient: str, key_points: List[str], **kwargs) -> Dict:
        """Generate cover letter."""
        template = self.TEMPLATES.get(purpose, self.TEMPLATES["job"])
        
        key_points_text = "\n\n".join([f"• {point}" for point in key_points])
        
        letter = template.format(
            recipient=recipient,
            key_points=key_points_text,
            **kwargs
        )
        
        return {
            "cover_letter": letter,
            "purpose": purpose,
            "word_count": len(letter.split())
        }

def main():
    import sys
    drafter = CoverLetterDrafter()
    result = drafter.draft("journal", "Nature Medicine", ["Novel findings", "Clinical relevance"], title="Study X", significance="major advance", author="Dr. Smith")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
