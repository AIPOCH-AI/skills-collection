#!/usr/bin/env python3
"""Meeting Minutes - Structures medical meeting transcripts."""

import json
import re

class MeetingMinutes:
    """Converts transcripts to structured meeting minutes."""
    
    def process(self, transcript: str, meeting_type: str = "clinical") -> dict:
        """Process transcript into structured minutes."""
        
        # Extract action items
        action_patterns = [
            r'(?:action item|todo|task|follow.up)[\s:]*(.*?)(?:\n|$)',
            r'(?:will|should|need to|must)\s+(\w+\s+.*?(?:by|before|next).*?)\.',
        ]
        
        action_items = []
        for pattern in action_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            action_items.extend(matches)
        
        # Extract decisions
        decision_patterns = [
            r'(?:decided|agreed|resolved|concluded)[\s:]*(.*?)(?:\n|$)',
            r'(?:decision|resolution)[\s:]*(.*?)(?:\n|$)',
        ]
        
        decisions = []
        for pattern in decision_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            decisions.extend(matches)
        
        # Format minutes
        minutes = f"""MEETING MINUTES

Date: [Extract from context]
Type: {meeting_type}

SUMMARY:
{transcript[:500]}...

DECISIONS:
"""
        for i, d in enumerate(decisions[:10], 1):
            minutes += f"{i}. {d}\n"
        
        minutes += "\nACTION ITEMS:\n"
        for i, a in enumerate(action_items[:10], 1):
            minutes += f"{i}. {a}\n"
        
        return {
            "minutes": minutes,
            "action_items": action_items[:10],
            "decisions": decisions[:10],
            "meeting_type": meeting_type
        }

def main():
    processor = MeetingMinutes()
    transcript = "We agreed to proceed with the study. Action item: Dr. Smith will prepare the protocol by Friday."
    result = processor.process(transcript)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
