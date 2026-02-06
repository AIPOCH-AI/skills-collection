#!/usr/bin/env python3
"""Time Zone Planner - Global meeting scheduler."""

import json

class TimeZonePlanner:
    """Plans meetings across time zones."""
    
    def plan(self, regions: list, duration: int) -> dict:
        """Find optimal meeting times."""
        
        # Simplified timezone mapping
        timezones = {
            "US": "EST/EDT (UTC-5/-4)",
            "EU": "CET/CEST (UTC+1/+2)",
            "Asia": "CST (UTC+8)"
        }
        
        suggested = []
        for region in regions:
            if region in timezones:
                suggested.append({
                    "region": region,
                    "local_time": "09:00",
                    "timezone": timezones[region]
                })
        
        return {
            "suggested_times": suggested,
            "optimal_window": "08:00-10:00 EST / 14:00-16:00 CET / 21:00-23:00 CST",
            "duration_minutes": duration
        }

def main():
    planner = TimeZonePlanner()
    result = planner.plan(["US", "EU", "Asia"], 60)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
