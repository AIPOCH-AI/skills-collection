#!/usr/bin/env python3
"""Date Calculator - Medical date calculations."""

import json
from datetime import datetime, timedelta

class DateCalculator:
    """Calculates medical dates."""
    
    def calculate(self, start_date: str, calc_type: str) -> dict:
        """Calculate date."""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        
        if calc_type == "gestational":
            today = datetime.now()
            weeks = (today - start).days // 7
            result = {
                "gestational_age_weeks": weeks,
                "estimated_delivery": (start + timedelta(days=280)).strftime("%Y-%m-%d")
            }
        elif calc_type == "followup":
            window_start = start + timedelta(days=28)
            window_end = start + timedelta(days=35)
            result = {
                "followup_window": f"{window_start.strftime('%Y-%m-%d')} to {window_end.strftime('%Y-%m-%d')}",
                "weeks": 4
            }
        else:
            result = {"error": "Unknown calculation type"}
        
        return result

def main():
    calc = DateCalculator()
    result = calc.calculate("2024-01-01", "gestational")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
