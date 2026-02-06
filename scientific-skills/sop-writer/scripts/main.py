#!/usr/bin/env python3
"""
SOP Writer
Write GCP-compliant Standard Operating Procedures.
"""

import argparse
from datetime import datetime


class SOPWriter:
    """Generate Standard Operating Procedures."""
    
    def generate_sop(self, procedure_name, scope, responsibility, steps):
        """Generate SOP document."""
        
        sop = f"""
STANDARD OPERATING PROCEDURE

Title: {procedure_name}
Document Number: SOP-{datetime.now().strftime('%Y')}-XXX
Version: 1.0
Effective Date: {datetime.now().strftime('%Y-%m-%d')}

1. PURPOSE
This SOP describes the procedure for {procedure_name}.

2. SCOPE
{scope}

3. RESPONSIBILITY
{responsibility}

4. MATERIALS AND EQUIPMENT
[List required materials]

5. PROCEDURE
"""
        
        for i, step in enumerate(steps, 1):
            sop += f"\n5.{i} {step}\n"
        
        sop += f"""
6. QUALITY CONTROL
[Describe QC checks]

7. DOCUMENTATION
[Record keeping requirements]

8. REFERENCES
[List applicable regulations and guidelines]

Approved by: _________________ Date: ___________
"""
        
        return sop


def main():
    parser = argparse.ArgumentParser(description="SOP Writer")
    parser.add_argument("--name", "-n", required=True, help="Procedure name")
    parser.add_argument("--scope", "-s", required=True, help="Scope")
    parser.add_argument("--responsibility", "-r", required=True, help="Who performs")
    parser.add_argument("--output", "-o", default="sop.txt", help="Output file")
    
    args = parser.parse_args()
    
    writer = SOPWriter()
    
    # Demo steps
    steps = [
        "Prepare workspace and materials",
        "Follow detailed procedure steps",
        "Document all actions",
        "Perform quality checks",
        "Archive records"
    ]
    
    sop = writer.generate_sop(args.name, args.scope, args.responsibility, steps)
    
    print(sop)
    
    with open(args.output, 'w') as f:
        f.write(sop)
    print(f"SOP saved to: {args.output}")


if __name__ == "__main__":
    main()
