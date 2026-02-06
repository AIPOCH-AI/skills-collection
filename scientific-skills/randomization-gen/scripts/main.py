#!/usr/bin/env python3
"""
Randomization Generator
Generate block randomization lists for RCTs.
"""

import argparse
import random
import csv


class RandomizationGenerator:
    """Generate randomization schedules."""
    
    def block_randomization(self, n_subjects, groups, block_size):
        """Generate block randomization."""
        if block_size % len(groups) != 0:
            raise ValueError("Block size must be divisible by number of groups")
        
        schedule = []
        subject_id = 1
        
        while subject_id <= n_subjects:
            block = []
            for group in groups:
                block.extend([group] * (block_size // len(groups)))
            
            random.shuffle(block)
            
            for assignment in block:
                if subject_id <= n_subjects:
                    schedule.append({
                        "subject_id": subject_id,
                        "group": assignment,
                        "block": (subject_id - 1) // block_size + 1
                    })
                    subject_id += 1
        
        return schedule
    
    def stratified_randomization(self, n_subjects, groups, strata, block_size):
        """Generate stratified randomization."""
        all_schedules = []
        
        subjects_per_stratum = n_subjects // len(strata)
        
        for stratum in strata:
            stratum_schedule = self.block_randomization(subjects_per_stratum, groups, block_size)
            for entry in stratum_schedule:
                entry["stratum"] = stratum
            all_schedules.extend(stratum_schedule)
        
        return all_schedules
    
    def export_csv(self, schedule, filename):
        """Export schedule to CSV."""
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=schedule[0].keys())
            writer.writeheader()
            writer.writerows(schedule)


def main():
    parser = argparse.ArgumentParser(description="Randomization Generator")
    parser.add_argument("--subjects", "-n", type=int, default=100, help="Number of subjects")
    parser.add_argument("--groups", "-g", default="Control,Treatment", help="Groups (comma-separated)")
    parser.add_argument("--block-size", "-b", type=int, default=4, help="Block size")
    parser.add_argument("--output", "-o", default="randomization.csv", help="Output file")
    
    args = parser.parse_args()
    
    generator = RandomizationGenerator()
    
    groups = [g.strip() for g in args.groups.split(",")]
    
    schedule = generator.block_randomization(args.subjects, groups, args.block_size)
    
    print(f"Generated randomization for {args.subjects} subjects")
    print(f"Groups: {groups}")
    print(f"Block size: {args.block_size}")
    
    # Show first 10
    print("\nFirst 10 allocations:")
    for entry in schedule[:10]:
        print(f"  Subject {entry['subject_id']}: {entry['group']}")
    
    generator.export_csv(schedule, args.output)
    print(f"\nFull schedule saved to: {args.output}")


if __name__ == "__main__":
    main()
