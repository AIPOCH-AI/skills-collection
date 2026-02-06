#!/usr/bin/env python3
"""
Equipment Maintenance Log
Track lab equipment calibration and maintenance.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class EquipmentLog:
    """Manage equipment maintenance records."""
    
    def __init__(self, data_file="~/.openclaw/equipment_log.json"):
        self.data_file = Path(data_file).expanduser()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.equipment = self._load()
    
    def _load(self):
        if self.data_file.exists():
            with open(self.data_file) as f:
                return json.load(f)
        return {}
    
    def _save(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.equipment, f, indent=2)
    
    def add(self, name, calibration_date, interval_months, location=""):
        """Add equipment to log."""
        self.equipment[name] = {
            "calibration_date": calibration_date,
            "interval_months": interval_months,
            "location": location,
            "added": datetime.now().isoformat()
        }
        self._save()
        print(f"Added: {name}")
    
    def check(self):
        """Check for upcoming maintenance."""
        today = datetime.now()
        alerts = {"overdue": [], "30days": [], "60days": [], "90days": []}
        
        for name, data in self.equipment.items():
            last_cal = datetime.fromisoformat(data["calibration_date"])
            next_cal = last_cal + timedelta(days=data["interval_months"] * 30)
            days_until = (next_cal - today).days
            
            if days_until < 0:
                alerts["overdue"].append((name, abs(days_until)))
            elif days_until <= 30:
                alerts["30days"].append((name, days_until))
            elif days_until <= 60:
                alerts["60days"].append((name, days_until))
            elif days_until <= 90:
                alerts["90days"].append((name, days_until))
        
        self._print_alerts(alerts)
        return alerts
    
    def _print_alerts(self, alerts):
        print("\n=== Equipment Maintenance Alerts ===")
        if alerts["overdue"]:
            print("\n🔴 OVERDUE:")
            for name, days in alerts["overdue"]:
                print(f"  {name}: {days} days overdue")
        if alerts["30days"]:
            print("\n🟡 Due within 30 days:")
            for name, days in alerts["30days"]:
                print(f"  {name}: {days} days")
        if alerts["60days"]:
            print("\n🟢 Due within 60 days:")
            for name, days in alerts["60days"]:
                print(f"  {name}: {days} days")
    
    def list_all(self):
        """List all equipment."""
        print("\n=== Equipment List ===")
        for name, data in self.equipment.items():
            print(f"\n{name}")
            print(f"  Last calibration: {data['calibration_date']}")
            print(f"  Interval: {data['interval_months']} months")


def main():
    parser = argparse.ArgumentParser(description="Equipment Maintenance Log")
    parser.add_argument("--add", help="Equipment name")
    parser.add_argument("--calibration-date", help="Last calibration date (YYYY-MM-DD)")
    parser.add_argument("--interval", type=int, help="Calibration interval (months)")
    parser.add_argument("--location", help="Equipment location")
    parser.add_argument("--check", action="store_true", help="Check for upcoming maintenance")
    parser.add_argument("--list", action="store_true", help="List all equipment")
    
    args = parser.parse_args()
    
    log = EquipmentLog()
    
    if args.add:
        log.add(args.add, args.calibration_date, args.interval, args.location)
    elif args.check:
        log.check()
    elif args.list:
        log.list_all()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
