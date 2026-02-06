#!/usr/bin/env python3
"""
Resubmission Deadline Tracker

Monitors academic manuscript resubmission deadlines and automatically
generates task breakdowns based on remaining time.

Usage:
    python main.py --add --title "Paper Title" --deadline "2024-03-15"
    python main.py --list
    python main.py --tasks "Paper Title"
    python main.py --interactive
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any


# Configuration
DEFAULT_TIMEZONE = "Asia/Shanghai"
DATA_DIR = Path(__file__).parent.parent / "data"
DEADLINES_FILE = DATA_DIR / "deadlines.json"
COMPLETED_FILE = DATA_DIR / "completed.json"


class UrgencyLevel(Enum):
    """Urgency classification based on remaining time."""
    RELAXED = "relaxed"      # >30 days
    STANDARD = "standard"    # 14-30 days
    ACTIVE = "active"        # 7-14 days
    URGENT = "urgent"        # 3-7 days
    EMERGENCY = "emergency"  # <3 days
    OVERDUE = "overdue"      # Past deadline


@dataclass
class Resubmission:
    """Represents a manuscript resubmission deadline."""
    id: str
    title: str
    journal: str
    deadline: str  # ISO format: YYYY-MM-DD
    deadline_time: str  # HH:MM format
    timezone: str
    major_issues: int
    minor_issues: int
    status: str  # not_started, in_progress, final_review, submitted
    progress: int  # 0-100
    notes: str
    created_at: str
    updated_at: str


class DeadlineTracker:
    """Main class for tracking resubmission deadlines."""

    # Task templates based on urgency level
    TASK_TEMPLATES = {
        UrgencyLevel.RELAXED: {
            "phases": [
                {
                    "name": "Phase 1: Planning & Analysis",
                    "duration_days": 3,
                    "tasks": [
                        "Re-read reviewer comments thoroughly",
                        "Categorize all comments by reviewer and priority",
                        "Create detailed response strategy document",
                        "Schedule co-author meetings",
                        "Identify required new data/analyses"
                    ]
                },
                {
                    "name": "Phase 2: Core Revisions",
                    "duration_days": 15,
                    "tasks": [
                        "Address all major reviewer concerns",
                        "Perform additional analyses if required",
                        "Revise methodology section",
                        "Update all figures and tables",
                        "Add new supplementary materials"
                    ]
                },
                {
                    "name": "Phase 3: Writing & Response",
                    "duration_days": 7,
                    "tasks": [
                        "Draft comprehensive response letter",
                        "Revise manuscript introduction",
                        "Update results and discussion sections",
                        "Polish abstract and title",
                        "Format according to journal guidelines"
                    ]
                },
                {
                    "name": "Phase 4: Review & Buffer",
                    "duration_days": 5,
                    "tasks": [
                        "Co-author review and approval",
                        "Professional editing check",
                        "Final proofreading",
                        "Prepare submission materials",
                        "Buffer time for unexpected issues"
                    ]
                }
            ]
        },
        UrgencyLevel.STANDARD: {
            "phases": [
                {
                    "name": "Phase 1: Analysis",
                    "duration_days": 2,
                    "tasks": [
                        "Re-read reviewer comments carefully",
                        "Categorize comments by type (major/minor)",
                        "Create response strategy document",
                        "Identify required new analyses"
                    ]
                },
                {
                    "name": "Phase 2: Core Revisions",
                    "duration_days": 8,
                    "tasks": [
                        "Address major concerns first",
                        "Revise methodology if needed",
                        "Update figures and tables",
                        "Add new data/analyses",
                        "Handle minor comments"
                    ]
                },
                {
                    "name": "Phase 3: Writing",
                    "duration_days": 3,
                    "tasks": [
                        "Draft response letter",
                        "Revise manuscript text",
                        "Update supplementary materials",
                        "Proofread all changes"
                    ]
                },
                {
                    "name": "Phase 4: Final Review",
                    "duration_days": 1,
                    "tasks": [
                        "Co-author sign-off",
                        "Final formatting checks",
                        "Journal submission prep",
                        "Submit before deadline"
                    ]
                }
            ]
        },
        UrgencyLevel.ACTIVE: {
            "phases": [
                {
                    "name": "Days 1-2: Triage & Priority",
                    "duration_days": 2,
                    "tasks": [
                        "Prioritize critical reviewer concerns",
                        "Identify 'must-fix' vs 'nice-to-have'",
                        "Draft quick response outline",
                        "Alert co-authors to timeline"
                    ]
                },
                {
                    "name": "Days 3-6: Execute",
                    "duration_days": 4,
                    "tasks": [
                        "Address P0 (critical) items only",
                        "Make essential figure updates",
                        "Draft concise response letter",
                        "Update core manuscript sections"
                    ]
                },
                {
                    "name": "Days 7-8: Finalize",
                    "duration_days": 2,
                    "tasks": [
                        "Co-author rapid review",
                        "Final proofread",
                        "Format and prep submission",
                        "SUBMIT"
                    ]
                }
            ]
        },
        UrgencyLevel.URGENT: {
            "phases": [
                {
                    "name": "IMMEDIATE (Day 1)",
                    "duration_days": 1,
                    "tasks": [
                        "🚨 List MINIMUM changes needed for acceptance",
                        "🚨 Contact co-authors - emergency review needed",
                        "🚨 Identify deal-breaker issues only",
                        "🚀 Skip non-critical comments"
                    ]
                },
                {
                    "name": "Days 2-4: Execute",
                    "duration_days": 3,
                    "tasks": [
                        "Fix only critical issues",
                        "Update essential figures",
                        "Draft minimal response letter",
                        "Get async co-author approval"
                    ]
                },
                {
                    "name": "Days 5-7: Submit",
                    "duration_days": 3,
                    "tasks": [
                        "Final proofread (self)",
                        "Quick format check",
                        "SUBMIT - even if imperfect",
                        "Consider extension request if needed"
                    ]
                }
            ]
        },
        UrgencyLevel.EMERGENCY: {
            "phases": [
                {
                    "name": "🚨 EMERGENCY PROTOCOL",
                    "duration_days": 1,
                    "tasks": [
                        "List ONLY deal-breaker issues",
                        "Request deadline extension NOW if possible",
                        "Emergency contact to co-authors",
                        "Decide: minimal viable submission vs extension"
                    ]
                },
                {
                    "name": "Final Hours",
                    "duration_days": 2,
                    "tasks": [
                        "Fix critical issues only",
                        "Minimal response letter",
                        "Submit what you have",
                        "Follow up with editor if needed"
                    ]
                }
            ]
        },
        UrgencyLevel.OVERDUE: {
            "phases": [
                {
                    "name": "⚠️ OVERDUE",
                    "duration_days": 0,
                    "tasks": [
                        "Contact editor IMMEDIATELY",
                        "Explain situation honestly",
                        "Request extension with timeline",
                        "Prepare for possible resubmission as new submission"
                    ]
                }
            ]
        }
    }

    def __init__(self):
        self._ensure_data_dir()
        self.deadlines = self._load_deadlines()

    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_deadlines(self) -> List[Resubmission]:
        """Load deadlines from JSON file."""
        if not DEADLINES_FILE.exists():
            return []
        try:
            with open(DEADLINES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Resubmission(**item) for item in data]
        except (json.JSONDecodeError, TypeError):
            return []

    def _save_deadlines(self):
        """Save deadlines to JSON file."""
        data = [asdict(d) for d in self.deadlines]
        with open(DEADLINES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _generate_id(self) -> str:
        """Generate unique ID for new deadline."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"rs_{timestamp}"

    def add_deadline(
        self,
        title: str,
        journal: str,
        deadline: str,
        deadline_time: str = "23:59",
        timezone: str = DEFAULT_TIMEZONE,
        major_issues: int = 0,
        minor_issues: int = 0,
        notes: str = ""
    ) -> Resubmission:
        """Add a new resubmission deadline."""
        now = datetime.now().isoformat()
        
        resubmission = Resubmission(
            id=self._generate_id(),
            title=title,
            journal=journal,
            deadline=deadline,
            deadline_time=deadline_time,
            timezone=timezone,
            major_issues=major_issues,
            minor_issues=minor_issues,
            status="not_started",
            progress=0,
            notes=notes,
            created_at=now,
            updated_at=now
        )
        
        self.deadlines.append(resubmission)
        self._save_deadlines()
        return resubmission

    def get_deadline(self, title_or_id: str) -> Optional[Resubmission]:
        """Get a specific deadline by title or ID."""
        for d in self.deadlines:
            if d.id == title_or_id or d.title.lower() == title_or_id.lower():
                return d
        # Try partial match
        for d in self.deadlines:
            if title_or_id.lower() in d.title.lower():
                return d
        return None

    def list_deadlines(self) -> List[Resubmission]:
        """List all active deadlines, sorted by urgency."""
        return sorted(self.deadlines, key=lambda d: d.deadline)

    def update_progress(self, title_or_id: str, progress: int) -> Optional[Resubmission]:
        """Update progress for a deadline."""
        deadline = self.get_deadline(title_or_id)
        if not deadline:
            return None
        
        deadline.progress = max(0, min(100, progress))
        deadline.updated_at = datetime.now().isoformat()
        
        # Auto-update status based on progress
        if deadline.progress >= 100:
            deadline.status = "submitted"
        elif deadline.progress >= 80:
            deadline.status = "final_review"
        elif deadline.progress >= 20:
            deadline.status = "in_progress"
        
        self._save_deadlines()
        return deadline

    def delete_deadline(self, title_or_id: str) -> bool:
        """Delete a deadline."""
        deadline = self.get_deadline(title_or_id)
        if not deadline:
            return False
        
        self.deadlines.remove(deadline)
        self._save_deadlines()
        return True

    def calculate_remaining_time(self, deadline: Resubmission) -> timedelta:
        """Calculate remaining time until deadline."""
        deadline_str = f"{deadline.deadline} {deadline.deadline_time}"
        deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        now = datetime.now()
        return deadline_dt - now

    def get_urgency_level(self, remaining: timedelta) -> UrgencyLevel:
        """Determine urgency level based on remaining time."""
        days = remaining.total_seconds() / (24 * 3600)
        
        if days < 0:
            return UrgencyLevel.OVERDUE
        elif days < 3:
            return UrgencyLevel.EMERGENCY
        elif days < 7:
            return UrgencyLevel.URGENT
        elif days < 14:
            return UrgencyLevel.ACTIVE
        elif days < 30:
            return UrgencyLevel.STANDARD
        else:
            return UrgencyLevel.RELAXED

    def format_time_remaining(self, remaining: timedelta) -> str:
        """Format remaining time in human-readable format."""
        if remaining.total_seconds() < 0:
            overdue = abs(remaining)
            days = int(overdue.days)
            hours = int(overdue.seconds // 3600)
            return f"OVERDUE by {days} days, {hours} hours"
        
        days = int(remaining.days)
        hours = int(remaining.seconds // 3600)
        minutes = int((remaining.seconds % 3600) // 60)
        
        if days > 0:
            return f"{days} days, {hours} hours"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes"

    def get_urgency_emoji(self, level: UrgencyLevel) -> str:
        """Get emoji for urgency level."""
        return {
            UrgencyLevel.RELAXED: "🟢",
            UrgencyLevel.STANDARD: "🟡",
            UrgencyLevel.ACTIVE: "🔵",
            UrgencyLevel.URGENT: "🟠",
            UrgencyLevel.EMERGENCY: "🔴",
            UrgencyLevel.OVERDUE: "⛔"
        }.get(level, "⚪")

    def generate_task_breakdown(self, deadline: Resubmission) -> Dict[str, Any]:
        """Generate task breakdown based on remaining time."""
        remaining = self.calculate_remaining_time(deadline)
        urgency = self.get_urgency_level(remaining)
        template = self.TASK_TEMPLATES.get(urgency, self.TASK_TEMPLATES[UrgencyLevel.STANDARD])
        
        return {
            "urgency_level": urgency.value,
            "urgency_emoji": self.get_urgency_emoji(urgency),
            "remaining_time": self.format_time_remaining(remaining),
            "remaining_days": remaining.days,
            "phases": template["phases"],
            "recommendations": self._get_recommendations(urgency)
        }

    def _get_recommendations(self, urgency: UrgencyLevel) -> List[str]:
        """Get recommendations based on urgency level."""
        recommendations = {
            UrgencyLevel.RELAXED: [
                "You have plenty of time. Focus on thorough revisions.",
                "Consider doing additional analyses to strengthen the paper.",
                "Schedule regular co-author meetings.",
                "Use buffer time for unexpected issues."
            ],
            UrgencyLevel.STANDARD: [
                "Standard timeline. Stay on track with the schedule.",
                "Prioritize major reviewer concerns.",
                "Don't let minor issues derail core revisions."
            ],
            UrgencyLevel.ACTIVE: [
                "Pick up the pace. Focus on essentials only.",
                "Consider delegating tasks to co-authors.",
                "Skip non-critical improvements."
            ],
            UrgencyLevel.URGENT: [
                "⚠️ Urgent: Focus ONLY on critical issues.",
                "Request async co-author feedback, not meetings.",
                "Submit even if not perfect - done is better than perfect."
            ],
            UrgencyLevel.EMERGENCY: [
                "🚨 EMERGENCY: Consider requesting deadline extension.",
                "Only fix deal-breaker issues.",
                "Get emergency help from co-authors.",
                "Submit minimal viable revision."
            ],
            UrgencyLevel.OVERDUE: [
                "⛔ OVERDUE: Contact editor immediately!",
                "Be honest about the situation.",
                "Request extension with specific timeline.",
                "Prepare for possible resubmission as new submission."
            ]
        }
        return recommendations.get(urgency, [])

    def print_status(self, deadline: Resubmission):
        """Print formatted status for a deadline."""
        remaining = self.calculate_remaining_time(deadline)
        urgency = self.get_urgency_level(remaining)
        emoji = self.get_urgency_emoji(urgency)
        
        print(f"\n{'='*60}")
        print(f"📄 {deadline.title}")
        print(f"{'='*60}")
        print(f"  Journal:     {deadline.journal}")
        print(f"  Deadline:    {deadline.deadline} {deadline.deadline_time}")
        print(f"  Remaining:   {emoji} {self.format_time_remaining(remaining)}")
        print(f"  Status:      {deadline.status.replace('_', ' ').title()}")
        print(f"  Progress:    {deadline.progress}%")
        print(f"  Issues:      {deadline.major_issues} major, {deadline.minor_issues} minor")
        if deadline.notes:
            print(f"  Notes:       {deadline.notes}")

    def print_task_breakdown(self, deadline: Resubmission):
        """Print formatted task breakdown."""
        breakdown = self.generate_task_breakdown(deadline)
        
        print(f"\n{'='*60}")
        print(f"📋 TASK BREAKDOWN: {deadline.title}")
        print(f"{'='*60}")
        print(f"Status: {breakdown['urgency_emoji']} {breakdown['urgency_level'].upper()}")
        print(f"Time Remaining: {breakdown['remaining_time']}")
        print()
        
        # Recommendations
        if breakdown['recommendations']:
            print("💡 RECOMMENDATIONS:")
            for rec in breakdown['recommendations']:
                print(f"   • {rec}")
            print()
        
        # Task phases
        for phase in breakdown['phases']:
            print(f"\n{phase['name']}")
            print("-" * len(phase['name']))
            for i, task in enumerate(phase['tasks'], 1):
                print(f"  {i}. {task}")

    def print_all_status(self):
        """Print status for all deadlines."""
        if not self.deadlines:
            print("\n📭 No active resubmissions tracked.")
            print("   Use --add to create a new deadline.")
            return
        
        print("\n📊 ACTIVE RESUBMISSIONS")
        print("="*80)
        print(f"{'Paper':<30} {'Journal':<20} {'Deadline':<12} {'Remaining':<15} {'Status'}")
        print("-"*80)
        
        for d in self.deadlines:
            remaining = self.calculate_remaining_time(d)
            urgency = self.get_urgency_level(remaining)
            emoji = self.get_urgency_emoji(urgency)
            time_str = self.format_time_remaining(remaining)
            
            title = d.title[:28] + ".." if len(d.title) > 30 else d.title
            journal = d.journal[:18] + ".." if len(d.journal) > 20 else d.journal
            
            print(f"{title:<30} {journal:<20} {d.deadline:<12} {emoji} {time_str:<12} {d.progress}%")
        
        print("="*80)


def interactive_mode():
    """Run in interactive mode."""
    tracker = DeadlineTracker()
    
    print("="*60)
    print("📅 Resubmission Deadline Tracker - Interactive Mode")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. Add new deadline")
        print("  2. View all deadlines")
        print("  3. View task breakdown")
        print("  4. Update progress")
        print("  5. Delete deadline")
        print("  6. Exit")
        
        choice = input("\nSelect (1-6): ").strip()
        
        if choice == "1":
            print("\n--- Add New Deadline ---")
            title = input("Paper title: ").strip()
            journal = input("Journal name: ").strip()
            deadline = input("Deadline date (YYYY-MM-DD): ").strip()
            deadline_time = input("Deadline time (HH:MM, default 23:59): ").strip() or "23:59"
            
            try:
                major = int(input("Number of major issues (default 0): ").strip() or "0")
                minor = int(input("Number of minor issues (default 0): ").strip() or "0")
            except ValueError:
                major, minor = 0, 0
            
            notes = input("Additional notes: ").strip()
            
            try:
                result = tracker.add_deadline(
                    title=title,
                    journal=journal,
                    deadline=deadline,
                    deadline_time=deadline_time,
                    major_issues=major,
                    minor_issues=minor,
                    notes=notes
                )
                print(f"\n✅ Added: {result.title}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        elif choice == "2":
            tracker.print_all_status()
        
        elif choice == "3":
            if not tracker.deadlines:
                print("\nNo deadlines to show.")
                continue
            
            print("\nAvailable papers:")
            for i, d in enumerate(tracker.deadlines, 1):
                print(f"  {i}. {d.title}")
            
            selection = input("\nSelect paper (number or title): ").strip()
            
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(tracker.deadlines):
                    tracker.print_task_breakdown(tracker.deadlines[idx])
                else:
                    print("Invalid selection.")
            except ValueError:
                deadline = tracker.get_deadline(selection)
                if deadline:
                    tracker.print_task_breakdown(deadline)
                else:
                    print("Paper not found.")
        
        elif choice == "4":
            title = input("Paper title: ").strip()
            deadline = tracker.get_deadline(title)
            if not deadline:
                print("Paper not found.")
                continue
            
            try:
                progress = int(input("Progress percentage (0-100): ").strip())
                tracker.update_progress(title, progress)
                print(f"✅ Updated progress to {progress}%")
            except ValueError:
                print("Invalid progress value.")
        
        elif choice == "5":
            title = input("Paper title to delete: ").strip()
            if tracker.delete_deadline(title):
                print("✅ Deleted successfully.")
            else:
                print("Paper not found.")
        
        elif choice == "6":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice.")


def main():
    parser = argparse.ArgumentParser(
        description="Track manuscript resubmission deadlines and generate task schedules"
    )
    parser.add_argument("--add", action="store_true", help="Add new deadline")
    parser.add_argument("--list", "-l", action="store_true", help="List all deadlines")
    parser.add_argument("--show", "-s", help="Show details for specific paper")
    parser.add_argument("--tasks", "-t", help="Generate task breakdown for paper")
    parser.add_argument("--update", "-u", help="Update progress for paper")
    parser.add_argument("--delete", "-d", help="Delete a deadline")
    parser.add_argument("--title", help="Paper title")
    parser.add_argument("--journal", "-j", help="Journal name")
    parser.add_argument("--deadline", help="Deadline date (YYYY-MM-DD)")
    parser.add_argument("--time", default="23:59", help="Deadline time (HH:MM)")
    parser.add_argument("--major-issues", type=int, default=0, help="Number of major issues")
    parser.add_argument("--minor-issues", type=int, default=0, help="Number of minor issues")
    parser.add_argument("--notes", default="", help="Additional notes")
    parser.add_argument("--progress", type=int, help="Progress percentage (0-100)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    tracker = DeadlineTracker()
    
    # Interactive mode if no arguments
    if args.interactive or len(sys.argv) == 1:
        interactive_mode()
        return
    
    if args.add:
        if not all([args.title, args.journal, args.deadline]):
            print("Error: --title, --journal, and --deadline are required for --add")
            sys.exit(1)
        
        result = tracker.add_deadline(
            title=args.title,
            journal=args.journal,
            deadline=args.deadline,
            deadline_time=args.time,
            major_issues=args.major_issues,
            minor_issues=args.minor_issues,
            notes=args.notes
        )
        print(f"✅ Added deadline: {result.title}")
        tracker.print_status(result)
    
    elif args.list:
        tracker.print_all_status()
    
    elif args.show:
        deadline = tracker.get_deadline(args.show)
        if deadline:
            tracker.print_status(deadline)
        else:
            print(f"❌ Paper not found: {args.show}")
            sys.exit(1)
    
    elif args.tasks:
        deadline = tracker.get_deadline(args.tasks)
        if deadline:
            tracker.print_task_breakdown(deadline)
        else:
            print(f"❌ Paper not found: {args.tasks}")
            sys.exit(1)
    
    elif args.update:
        if args.progress is None:
            print("Error: --progress is required for --update")
            sys.exit(1)
        
        result = tracker.update_progress(args.update, args.progress)
        if result:
            print(f"✅ Updated progress: {result.title} is now {result.progress}%")
        else:
            print(f"❌ Paper not found: {args.update}")
            sys.exit(1)
    
    elif args.delete:
        if tracker.delete_deadline(args.delete):
            print(f"✅ Deleted: {args.delete}")
        else:
            print(f"❌ Paper not found: {args.delete}")
            sys.exit(1)


if __name__ == "__main__":
    main()
