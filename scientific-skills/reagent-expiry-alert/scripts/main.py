#!/usr/bin/env python3
"""
Reagent Expiry Alert
Track reagent expiration dates and send alerts.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class ReagentTracker:
    """Track reagent expiry dates."""
    
    def __init__(self, data_file="~/.openclaw/reagent_inventory.json"):
        self.data_file = Path(data_file).expanduser()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.inventory = self._load()
    
    def _load(self):
        if self.data_file.exists():
            with open(self.data_file) as f:
                return json.load(f)
        return {}
    
    def _save(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.inventory, f, indent=2)
    
    def scan_reagent(self, barcode, name, expiry_date, location="", quantity=1):
        """Add or update reagent."""
        self.inventory[barcode] = {
            "name": name,
            "expiry_date": expiry_date,
            "location": location,
            "quantity": quantity,
            "added": datetime.now().isoformat(),
            "scanned": True
        }
        self._save()
        print(f"✓ Scanned: {name} (expires: {expiry_date})")
    
    def check_alerts(self, alert_days=30):
        """Check for upcoming expirations."""
        today = datetime.now()
        alerts = {"expired": [], "soon": [], "warning": []}
        
        for barcode, data in self.inventory.items():
            expiry = datetime.fromisoformat(data["expiry_date"])
            days_until = (expiry - today).days
            
            if days_until < 0:
                alerts["expired"].append((data["name"], barcode, abs(days_until)))
            elif days_until <= 7:
                alerts["expired"].append((data["name"], barcode, days_until))
            elif days_until <= alert_days:
                alerts["soon"].append((data["name"], barcode, days_until))
        
        self._print_alerts(alerts)
        return alerts
    
    def _print_alerts(self, alerts):
        print("\n=== Reagent Expiry Alerts ===")
        
        if alerts["expired"]:
            print("\n🔴 EXPIRED / EXPIRING SOON:")
            for name, barcode, days in alerts["expired"]:
                if days < 0:
                    print(f"  {name}: {days} days OVERDUE ({barcode})")
                else:
                    print(f"  {name}: {days} days left ({barcode})")
        
        if alerts["soon"]:
            print("\n🟡 Expiring within alert period:")
            for name, barcode, days in alerts["soon"]:
                print(f"  {name}: {days} days left ({barcode})")
        
        if not alerts["expired"] and not alerts["soon"]:
            print("\n✅ No expiring reagents in alert period")
    
    def list_inventory(self):
        """List all reagents."""
        print("\n=== Reagent Inventory ===")
        for barcode, data in sorted(self.inventory.items(), 
                                     key=lambda x: x[1]["expiry_date"]):
            print(f"\n{data['name']}")
            print(f"  Barcode: {barcode}")
            print(f"  Expires: {data['expiry_date']}")
            print(f"  Location: {data.get('location', 'N/A')}")
            print(f"  Quantity: {data.get('quantity', 1)}")


def main():
    parser = argparse.ArgumentParser(description="Reagent Expiry Alert")
    parser.add_argument("--scan", "-s", help="Reagent barcode")
    parser.add_argument("--name", "-n", help="Reagent name")
    parser.add_argument("--expiry", "-e", help="Expiry date (YYYY-MM-DD)")
    parser.add_argument("--location", "-l", help="Storage location")
    parser.add_argument("--quantity", type=int, default=1, help="Quantity")
    parser.add_argument("--check-alerts", "-c", action="store_true", help="Check alerts")
    parser.add_argument("--alert-days", type=int, default=30, help="Alert threshold")
    parser.add_argument("--list", action="store_true", help="List inventory")
    
    args = parser.parse_args()
    
    tracker = ReagentTracker()
    
    if args.scan and args.expiry:
        tracker.scan_reagent(args.scan, args.name or args.scan, 
                            args.expiry, args.location, args.quantity)
    elif args.check_alerts:
        tracker.check_alerts(args.alert_days)
    elif args.list:
        tracker.list_inventory()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
