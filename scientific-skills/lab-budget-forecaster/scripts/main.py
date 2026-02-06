#!/usr/bin/env python3
"""
Lab Budget Forecaster
Predict grant fund depletion based on burn rate.
"""

import argparse
from datetime import datetime, timedelta


class LabBudgetForecaster:
    """Forecast lab budget and predict fund depletion."""
    
    def __init__(self, total_budget, start_date, end_date):
        self.total_budget = total_budget
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.expenses = []
    
    def add_expense(self, category, amount, date, description=""):
        """Add an expense."""
        self.expenses.append({
            "category": category,
            "amount": amount,
            "date": datetime.strptime(date, "%Y-%m-%d"),
            "description": description
        })
    
    def calculate_burn_rate(self):
        """Calculate monthly burn rate."""
        if not self.expenses:
            return 0
        
        total_spent = sum(e["amount"] for e in self.expenses)
        days_elapsed = (max(e["date"] for e in self.expenses) - self.start_date).days
        
        if days_elapsed == 0:
            return 0
        
        monthly_rate = (total_spent / days_elapsed) * 30
        return monthly_rate
    
    def predict_depletion(self):
        """Predict when funds will be depleted."""
        total_spent = sum(e["amount"] for e in self.expenses)
        remaining = self.total_budget - total_spent
        monthly_rate = self.calculate_burn_rate()
        
        if monthly_rate == 0:
            return None
        
        months_remaining = remaining / monthly_rate
        depletion_date = datetime.now() + timedelta(days=months_remaining * 30)
        
        return {
            "remaining_budget": remaining,
            "monthly_burn_rate": monthly_rate,
            "months_remaining": months_remaining,
            "predicted_depletion": depletion_date.strftime("%Y-%m-%d")
        }
    
    def generate_report(self):
        """Generate budget forecast report."""
        total_spent = sum(e["amount"] for e in self.expenses)
        remaining = self.total_budget - total_spent
        burn_rate = self.calculate_burn_rate()
        depletion = self.predict_depletion()
        
        report = {
            "total_budget": self.total_budget,
            "total_spent": total_spent,
            "remaining": remaining,
            "percent_used": (total_spent / self.total_budget) * 100,
            "monthly_burn_rate": burn_rate,
            "depletion_forecast": depletion
        }
        
        return report
    
    def print_report(self, report):
        """Print formatted report."""
        print(f"\n{'='*60}")
        print("LAB BUDGET FORECAST")
        print(f"{'='*60}\n")
        
        print(f"Total Budget:     ${report['total_budget']:,.2f}")
        print(f"Total Spent:      ${report['total_spent']:,.2f}")
        print(f"Remaining:        ${report['remaining']:,.2f}")
        print(f"Percent Used:     {report['percent_used']:.1f}%")
        print()
        
        if report['depletion_forecast']:
            print("FORECAST:")
            print(f"  Monthly Burn Rate: ${report['depletion_forecast']['monthly_burn_rate']:,.2f}")
            print(f"  Months Remaining:  {report['depletion_forecast']['months_remaining']:.1f}")
            print(f"  Predicted Depletion: {report['depletion_forecast']['predicted_depletion']}")
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Lab Budget Forecaster")
    parser.add_argument("--budget", "-b", type=float, required=True, help="Total budget")
    parser.add_argument("--start", "-s", required=True, help="Grant start date (YYYY-MM-DD)")
    parser.add_argument("--end", "-e", required=True, help="Grant end date (YYYY-MM-DD)
    parser.add_argument("--expenses", help="Expenses CSV file")
    
    args = parser.parse_args()
    
    forecaster = LabBudgetForecaster(args.budget, args.start, args.end)
    
    if args.expenses:
        # Parse expenses file
        import csv
        with open(args.expenses) as f:
            reader = csv.DictReader(f)
            for row in reader:
                forecaster.add_expense(
                    row.get("category", ""),
                    float(row.get("amount", 0)),
                    row.get("date", ""),
                    row.get("description", "")
                )
    else:
        # Demo data
        forecaster.add_expense("Personnel", 15000, "2024-01-15", "Month 1 salaries")
        forecaster.add_expense("Supplies", 3000, "2024-01-20", "Lab supplies")
        forecaster.add_expense("Equipment", 5000, "2024-02-01", "New centrifuge")
        forecaster.add_expense("Personnel", 15000, "2024-02-15", "Month 2 salaries")
    
    report = forecaster.generate_report()
    forecaster.print_report(report)


if __name__ == "__main__":
    main()
