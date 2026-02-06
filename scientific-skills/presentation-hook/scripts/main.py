#!/usr/bin/env python3
"""Presentation Hook - Opening and closing generators."""

import json

class PresentationHook:
    """Creates presentation hooks."""
    
    def generate(self, topic: str, audience: str, hook_type: str) -> dict:
        """Generate hook."""
        
        if hook_type == "opening":
            hook = f"What if I told you that {topic.lower()} could change everything we know about patient care?"
            alternatives = [
                f"Every year, thousands of patients face challenges with {topic.lower()}.",
                f"Imagine a world where {topic.lower()} is no longer a barrier."
            ]
        else:  # closing
            hook = f"Together, we can transform {topic.lower()} and improve patient outcomes."
            alternatives = [
                f"The future of {topic.lower()} starts with the actions we take today.",
                f"Thank you. Let's make a difference in {topic.lower()}."
            ]
        
        return {
            "hook": hook,
            "alternative_hooks": alternatives,
            "type": hook_type
        }

def main():
    gen = PresentationHook()
    result = gen.generate("diabetes management", "clinicians", "opening")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
