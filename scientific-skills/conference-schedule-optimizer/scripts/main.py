#!/usr/bin/env python3
"""
Conference Schedule Optimizer
Optimize conference attendance schedule.
"""

import argparse
import json
from datetime import datetime


class ScheduleOptimizer:
    """Optimize conference schedule."""
    
    def __init__(self):
        self.schedule = []
        self.interests = []
    
    def load_schedule(self, schedule_file):
        """Load conference schedule."""
        with open(schedule_file) as f:
            data = json.load(f)
        return data.get("sessions", [])
    
    def score_session(self, session, interests):
        """Score session relevance to interests."""
        score = 0
        session_topics = session.get("topics", [])
        session_title = session.get("title", "").lower()
        
        for interest in interests:
            interest = interest.lower().strip()
            if interest in session_title:
                score += 10
            for topic in session_topics:
                if interest in topic.lower():
                    score += 5
        
        return score
    
    def find_conflicts(self, sessions):
        """Find time conflicts."""
        conflicts = []
        for i, s1 in enumerate(sessions):
            for s2 in sessions[i+1:]:
                if s1["start"] == s2["start"]:
                    conflicts.append((s1, s2))
        return conflicts
    
    def optimize(self, sessions, interests, must_attend=None):
        """Generate optimized schedule."""
        must_attend = must_attend or []
        
        # Score all sessions
        scored = []
        for session in sessions:
            score = self.score_session(session, interests)
            is_must = session.get("id") in must_attend
            scored.append({
                **session,
                "score": score,
                "is_must": is_must
            })
        
        # Sort by time, then by score (must-attend first)
        scored.sort(key=lambda x: (x["start"], not x["is_must"], -x["score"]))
        
        # Select non-conflicting sessions
        selected = []
        used_times = set()
        
        for session in scored:
            if session["is_must"] or session["start"] not in used_times:
                selected.append(session)
                used_times.add(session["start"])
        
        return selected
    
    def print_schedule(self, schedule):
        """Print optimized schedule."""
        print("\n" + "="*70)
        print("OPTIMIZED CONFERENCE SCHEDULE")
        print("="*70)
        
        current_day = None
        for session in schedule:
            day = session["start"][:10]
            if day != current_day:
                current_day = day
                print(f"\n📅 {day}")
                print("-"*70)
            
            must = "⭐ " if session["is_must"] else "   "
            print(f"{must}{session['start'][11:16]} - {session['title'][:50]}")
            print(f"    Room: {session.get('room', 'TBA')} | Score: {session['score']}")
        
        print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Conference Schedule Optimizer")
    parser.add_argument("--interests", "-i", required=True,
                       help="Comma-separated topic interests")
    parser.add_argument("--schedule", "-s", required=True,
                       help="Conference schedule JSON file")
    parser.add_argument("--must-attend", "-m",
                       help="Comma-separated must-attend session IDs")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    optimizer = ScheduleOptimizer()
    
    # Load and process
    sessions = optimizer.load_schedule(args.schedule)
    interests = [i.strip() for i in args.interests.split(",")]
    must_attend = [m.strip() for m in args.must_attend.split(",")] if args.must_attend else []
    
    # Optimize
    optimized = optimizer.optimize(sessions, interests, must_attend)
    
    # Display
    optimizer.print_schedule(optimized)
    
    # Save if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(optimized, f, indent=2)
        print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()
