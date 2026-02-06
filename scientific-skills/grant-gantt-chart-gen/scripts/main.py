#!/usr/bin/env python3
"""
Grant Gantt Chart Generator
Create project timeline visualizations for grant proposals.
"""

import argparse
from datetime import datetime, timedelta
import json


class GanttChartGenerator:
    """Generate Gantt charts for grant proposals."""
    
    def __init__(self, start_date, duration_months):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.duration = duration_months
        self.end_date = self.start_date + timedelta(days=30 * duration_months)
    
    def create_milestone_timeline(self, milestones):
        """Create milestone timeline."""
        timeline = []
        
        for ms in milestones:
            name = ms["name"]
            month = ms["month"]
            date = self.start_date + timedelta(days=30 * month)
            
            timeline.append({
                "name": name,
                "month": month,
                "date": date.strftime("%Y-%m-%d"),
                "quarter": (month // 3) + 1
            })
        
        return timeline
    
    def generate_quarters(self):
        """Generate quarterly breakdown."""
        quarters = []
        for q in range(1, (self.duration // 3) + 2):
            start_month = (q - 1) * 3
            end_month = min(q * 3, self.duration)
            
            start_date = self.start_date + timedelta(days=30 * start_month)
            end_date = self.start_date + timedelta(days=30 * end_month)
            
            quarters.append({
                "quarter": f"Q{q}",
                "months": f"{start_month}-{end_month}",
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            })
        
        return quarters
    
    def generate_ascii_gantt(self, tasks):
        """Generate ASCII Gantt chart."""
        lines = []
        lines.append("PROJECT TIMELINE")
        lines.append("=" * 80)
        
        # Header
        month_labels = [f"M{i+1:2d}" for i in range(self.duration)]
        lines.append("Task                " + " ".join(month_labels))
        lines.append("-" * 80)
        
        # Tasks
        for task in tasks:
            name = task["name"][:18].ljust(18)
            start = task["start_month"]
            duration = task["duration_months"]
            
            row = [" "] * self.duration
            for i in range(start, min(start + duration, self.duration)):
                row[i] = "█"
            
            lines.append(name + " " + " ".join(row))
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def generate_mermaid_gantt(self, tasks):
        """Generate Mermaid syntax for Gantt chart."""
        lines = ["gantt"]
        lines.append(f"    title Project Timeline ({self.duration} months)")
        lines.append(f"    dateFormat YYYY-MM-DD")
        lines.append("")
        
        for task in tasks:
            name = task["name"]
            start = (self.start_date + timedelta(days=30 * task["start_month"])).strftime("%Y-%m-%d")
            duration = f"{task['duration_months']} months"
            
            lines.append(f"    {name} :{name.replace(' ', '_')}, {start}, {duration}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Grant Gantt Chart Generator")
    parser.add_argument("--milestones", "-m", help="Milestones JSON file")
    parser.add_argument("--duration", "-d", type=int, default=36,
                       help="Project duration in months")
    parser.add_argument("--start-date", "-s", default=datetime.now().strftime("%Y-%m-%d"),
                       help="Project start date (YYYY-MM-DD)")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--format", "-f", choices=["ascii", "mermaid", "json"],
                       default="ascii", help="Output format")
    
    args = parser.parse_args()
    
    # Load milestones or use defaults
    if args.milestones:
        with open(args.milestones) as f:
            milestones = json.load(f)
    else:
        # Default milestones for 3-year grant
        milestones = [
            {"name": "Year 1 Progress Report", "month": 12},
            {"name": "Year 2 Progress Report", "month": 24},
            {"name": "Final Report", "month": 36}
        ]
    
    # Default tasks
    tasks = [
        {"name": "Aim 1: Data Collection", "start_month": 0, "duration_months": 12},
        {"name": "Aim 2: Analysis", "start_month": 6, "duration_months": 18},
        {"name": "Aim 3: Validation", "start_month": 18, "duration_months": 12},
        {"name": "Manuscript Prep", "start_month": 24, "duration_months": 10}
    ]
    
    generator = GanttChartGenerator(args.start_date, args.duration)
    
    # Generate timeline
    timeline = generator.create_milestone_timeline(milestones)
    quarters = generator.generate_quarters()
    
    print("\n" + "=" * 70)
    print("GRANT PROJECT TIMELINE")
    print("=" * 70)
    print(f"Start: {args.start_date}")
    print(f"Duration: {args.duration} months")
    print(f"End: {generator.end_date.strftime('%Y-%m-%d')}")
    
    print("\n--- Milestones ---")
    for ms in timeline:
        print(f"  {ms['date']} (Month {ms['month']}, {ms['quarter']}): {ms['name']}")
    
    print("\n--- Quarters ---")
    for q in quarters[:4]:  # Show first 4 quarters
        print(f"  {q['quarter']}: {q['start']} to {q['end']}")
    
    # Generate chart
    if args.format == "ascii":
        chart = generator.generate_ascii_gantt(tasks)
    elif args.format == "mermaid":
        chart = generator.generate_mermaid_gantt(tasks)
    else:
        chart = json.dumps({"milestones": timeline, "quarters": quarters}, indent=2)
    
    print("\n" + chart)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(chart)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
