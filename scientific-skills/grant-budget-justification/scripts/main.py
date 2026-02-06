#!/usr/bin/env python3
"""
Grant Budget Justification
Generate narrative budget justifications for NIH/NSF applications.
"""

import argparse
from datetime import datetime


class BudgetJustification:
    """Generate budget justification narratives."""
    
    PERSONNEL_LEVELS = {
        "PI": {"effort": "3 months", "role": "Project oversight and direction"},
        "Co-I": {"effort": "1.5 months", "role": "Methodology and analysis"},
        "Postdoc": {"effort": "12 months", "role": "Laboratory experiments"},
        "Graduate Student": {"effort": "12 months", "role": "Data collection and analysis"},
        "Technician": {"effort": "12 months", "role": "Technical support"}
    }
    
    def generate_personnel_justification(self, personnel_list):
        """Generate personnel justification."""
        sections = []
        sections.append("A. Personnel")
        sections.append("")
        
        total_cost = 0
        for person in personnel_list:
            name = person.get("name", "TBD")
            role = person.get("role", "Postdoc")
            percent = person.get("percent", 50)
            salary = person.get("salary", 50000)
            cost = salary * (percent / 100)
            total_cost += cost
            
            level_info = self.PERSONNEL_LEVELS.get(role, {})
            
            sections.append(f"{name} ({role})")
            sections.append(f"  Effort: {percent}% ({level_info.get('effort', '12 months')})")
            sections.append(f"  Role: {level_info.get('role', 'Research support')}")
            sections.append(f"  Justification: {person.get('justification', 'Essential for project success')}")
            sections.append(f"  Cost: ${cost:,.2f}")
            sections.append("")
        
        sections.append(f"Total Personnel Costs: ${total_cost:,.2f}")
        return "\n".join(sections)
    
    def generate_equipment_justification(self, equipment_list):
        """Generate equipment justification."""
        sections = []
        sections.append("B. Equipment")
        sections.append("")
        
        total_cost = 0
        for item in equipment_list:
            name = item.get("name", "Equipment")
            cost = item.get("cost", 0)
            total_cost += cost
            
            sections.append(f"{name}: ${cost:,.2f}")
            sections.append(f"  Justification: {item.get('justification', 'Required for specific aims')}")
            sections.append(f"  Usage: {item.get('usage', 'Dedicated to this project')}")
            sections.append("")
        
        sections.append(f"Total Equipment Costs: ${total_cost:,.2f}")
        return "\n".join(sections)
    
    def generate_supplies_justification(self, supplies_list):
        """Generate supplies justification."""
        sections = []
        sections.append("C. Supplies")
        sections.append("")
        
        total_cost = 0
        for category, items in supplies_list.items():
            cat_cost = sum(item.get("cost", 0) for item in items)
            total_cost += cat_cost
            
            sections.append(f"{category}: ${cat_cost:,.2f}")
            for item in items:
                sections.append(f"  - {item['name']}: ${item['cost']:,.2f}")
            sections.append("")
        
        sections.append(f"Total Supplies Costs: ${total_cost:,.2f}")
        return "\n".join(sections)
    
    def generate_travel_justification(self, trips):
        """Generate travel justification."""
        sections = []
        sections.append("D. Travel")
        sections.append("")
        
        total_cost = sum(trip.get("cost", 0) for trip in trips)
        
        for trip in trips:
            sections.append(f"{trip.get('destination', 'Conference')}: ${trip.get('cost', 0):,.2f}")
            sections.append(f"  Purpose: {trip.get('purpose', 'Present research findings')}")
            sections.append(f"  Justification: {trip.get('justification', 'Essential for dissemination')}")
            sections.append("")
        
        sections.append(f"Total Travel Costs: ${total_cost:,.2f}")
        return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Grant Budget Justification")
    parser.add_argument("--personnel", "-p", help="Personnel JSON file")
    parser.add_argument("--equipment", "-e", help="Equipment JSON file")
    parser.add_argument("--output", "-o", default="budget_justification.txt", help="Output file")
    parser.add_argument("--demo", action="store_true", help="Generate demo justification")
    
    args = parser.parse_args()
    
    justifier = BudgetJustification()
    
    if args.demo:
        # Demo data
        personnel = [
            {"name": "Dr. Smith", "role": "PI", "percent": 25, "salary": 120000},
            {"name": "Dr. Jones", "role": "Postdoc", "percent": 100, "salary": 52000}
        ]
        
        equipment = [
            {"name": "High-performance computer", "cost": 5000, "justification": "Data analysis"}
        ]
        
        supplies = {
            "Laboratory": [
                {"name": "Reagents", "cost": 15000},
                {"name": "Consumables", "cost": 5000}
            ]
        }
        
        trips = [
            {"destination": "Annual Scientific Meeting", "cost": 2500, "purpose": "Present results"}
        ]
        
        justification = []
        justification.append("=" * 70)
        justification.append("BUDGET JUSTIFICATION")
        justification.append("=" * 70)
        justification.append("")
        justification.append(justifier.generate_personnel_justification(personnel))
        justification.append("")
        justification.append(justifier.generate_equipment_justification(equipment))
        justification.append("")
        justification.append(justifier.generate_supplies_justification(supplies))
        justification.append("")
        justification.append(justifier.generate_travel_justification(trips))
        justification.append("")
        justification.append("=" * 70)
        
        text = "\n".join(justification)
        print(text)
        
        with open(args.output, 'w') as f:
            f.write(text)
        print(f"\nSaved to: {args.output}")
    else:
        print("Use --demo to see example output")
        print("Or provide --personnel and --equipment JSON files")


if __name__ == "__main__":
    main()
