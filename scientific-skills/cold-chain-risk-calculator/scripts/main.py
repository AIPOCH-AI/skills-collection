#!/usr/bin/env python3
"""
Cold Chain Risk Calculator
Calculate transport risks for temperature-sensitive samples.
"""

import argparse


def calculate_risk(route, duration_hours, packaging):
    """Calculate cold chain risk."""
    # Simplified risk calculation
    base_risk = duration_hours * 0.5
    packaging_factor = {"dry-ice": 0.8, "liquid-nitrogen": 0.3, "gel-packs": 1.2}
    risk = base_risk * packaging_factor.get(packaging, 1.0)
    
    print(f"Route: {route}")
    print(f"Duration: {duration_hours} hours")
    print(f"Packaging: {packaging}")
    print(f"Risk score: {risk:.2f}")
    
    if risk < 10:
        return "Low risk"
    elif risk < 20:
        return "Medium risk"
    else:
        return "High risk"


def main():
    parser = argparse.ArgumentParser(description="Cold Chain Risk Calculator")
    parser.add_argument("--route", "-r", required=True, help="Transport route")
    parser.add_argument("--duration", "-d", type=int, required=True, help="Duration in hours")
    parser.add_argument("--packaging", "-p", default="dry-ice", choices=["dry-ice", "liquid-nitrogen", "gel-packs"])
    args = parser.parse_args()
    
    risk_level = calculate_risk(args.route, args.duration, args.packaging)
    print(f"Risk level: {risk_level}")


if __name__ == "__main__":
    main()
