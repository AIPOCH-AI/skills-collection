#!/usr/bin/env python3
"""
Mentorship Meeting Agenda
Generate structured agendas for mentor-student one-on-one meetings.
"""

import argparse
from datetime import datetime


class MentorshipAgenda:
    """Generate mentorship meeting agendas."""
    
    PHASES = {
        "early": "Early Stage (Year 1-2)",
        "mid": "Mid Stage (Year 3-4)",
        "late": "Late Stage (Year 5+)"
    }
    
    def generate_agenda(self, student, phase, topics=None):
        """Generate meeting agenda."""
        agenda = []
        
        agenda.append(f"MENTORSHIP MEETING AGENDA")
        agenda.append(f"Student: {student}")
        agenda.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        agenda.append(f"Phase: {self.PHASES.get(phase, phase)}")
        agenda.append("="*70)
        agenda.append("")
        
        sections = [
            ("Opening (5 min)", "Check-in on overall wellbeing"),
            ("Progress Update (10 min)", "What have you accomplished since last meeting?"),
            ("Current Challenges (10 min)", "What obstacles are you facing?"),
            ("Goal Setting (10 min)", "What are your short-term goals?"),
            ("Resource Needs (5 min)", "What support do you need?"),
            ("Action Items (5 min)", "What are the next steps?")
        ]
        
        for title, prompt in sections:
            agenda.append(f"{title}")
            agenda.append(f"  Prompt: {prompt}")
            agenda.append("  [Notes]")
            agenda.append("")
        
        if topics:
            agenda.append("SPECIFIC TOPICS:")
            for topic in topics:
                agenda.append(f"  • {topic}")
            agenda.append("")
        
        agenda.append("="*70)
        
        return "\n".join(agenda)


def main():
    parser = argparse.ArgumentParser(description="Mentorship Meeting Agenda")
    parser.add_argument("--student", "-s", required=True, help="Student name")
    parser.add_argument("--phase", "-p", choices=["early", "mid", "late"],
                       default="mid", help="Career phase")
    parser.add_argument("--topics", "-t", help="Comma-separated topics")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    generator = MentorshipAgenda()
    
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    agenda = generator.generate_agenda(args.student, args.phase, topics)
    print(agenda)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(agenda)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
