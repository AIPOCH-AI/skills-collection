#!/usr/bin/env python3
"""Personal Statement - Personal narrative generator."""

import json

class PersonalStatement:
    """Generates personal statements."""
    
    def generate(self, purpose: str, experiences: list, goals: str) -> dict:
        """Generate personal statement."""
        
        statement = f"""My journey in medicine began with a desire to make a difference.

Through my experiences, including {experiences[0] if experiences else 'clinical work'}, 
I have developed a passion for {purpose}.

My goal is to {goals}.
"""
        
        return {
            "personal_statement": statement,
            "themes": ["Dedication", "Growth", "Service"],
            "word_count": len(statement.split())
        }

def main():
    ps = PersonalStatement()
    result = ps.generate("patient care", ["volunteering at clinics"], "improve healthcare access")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
