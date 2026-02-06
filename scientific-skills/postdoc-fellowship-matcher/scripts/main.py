#!/usr/bin/env python3
"""
Postdoc Fellowship Matcher
Match postdoc applicants to eligible fellowships.
"""

import argparse


class FellowshipMatcher:
    """Match applicants to postdoctoral fellowships."""
    
    FELLOWSHIPS = [
        {
            "name": "NIH F32",
            "eligible_nationalities": ["US", "permanent resident"],
            "max_years_post_phd": 3,
            "deadline": "April/October/December"
        },
        {
            "name": "NSF Postdoc",
            "eligible_nationalities": ["any"],
            "max_years_post_phd": 2,
            "deadline": "October"
        },
        {
            "name": "EMBO Fellowship",
            "eligible_nationalities": ["any"],
            "max_years_post_phd": 2,
            "deadline": "February/August"
        },
        {
            "name": "HFSP Fellowship",
            "eligible_nationalities": ["any"],
            "max_years_post_phd": 3,
            "deadline": "March/August"
        }
    ]
    
    def find_matches(self, nationality, years_post_phd, field):
        """Find eligible fellowships."""
        matches = []
        
        for fellowship in self.FELLOWSHIPS:
            # Check nationality
            nat_ok = ("any" in fellowship["eligible_nationalities"] or 
                     nationality in fellowship["eligible_nationalities"])
            
            # Check years
            years_ok = years_post_phd <= fellowship["max_years_post_phd"]
            
            if nat_ok and years_ok:
                matches.append(fellowship)
        
        return matches
    
    def print_matches(self, matches, applicant_info):
        """Print matching fellowships."""
        print(f"\n{'='*60}")
        print(f"FELLOWSHIP MATCHES FOR {applicant_info['name']}")
        print(f"{'='*60}\n")
        
        print(f"Nationality: {applicant_info['nationality']}")
        print(f"Years post-PhD: {applicant_info['years']}")
        print(f"Field: {applicant_info['field']}")
        print()
        
        if matches:
            print(f"Found {len(matches)} eligible fellowship(s):\n")
            for f in matches:
                print(f"  • {f['name']}")
                print(f"    Deadline: {f['deadline']}")
                print()
        else:
            print("No eligible fellowships found with current criteria.")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Postdoc Fellowship Matcher")
    parser.add_argument("--nationality", "-n", required=True, help="Your nationality")
    parser.add_argument("--years", "-y", type=int, required=True, help="Years since PhD")
    parser.add_argument("--field", "-f", required=True, help="Research field")
    parser.add_argument("--name", default="Applicant", help="Your name")
    
    args = parser.parse_args()
    
    matcher = FellowshipMatcher()
    
    applicant = {
        "name": args.name,
        "nationality": args.nationality,
        "years": args.years,
        "field": args.field
    }
    
    matches = matcher.find_matches(args.nationality, args.years, args.field)
    matcher.print_matches(matches, applicant)


if __name__ == "__main__":
    main()
