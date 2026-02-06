#!/usr/bin/env python3
"""
Motif Logo Generator
Generate DNA or protein sequence motif logos showing conserved positions.
"""

import argparse
import numpy as np


class MotifLogoGenerator:
    """Generate sequence motif logos."""
    
    def calculate_information_content(self, sequences):
        """Calculate information content at each position."""
        if not sequences:
            return []
        
        length = len(sequences[0])
        num_sequences = len(sequences)
        
        info_content = []
        
        for pos in range(length):
            # Get residues at this position
            residues = [seq[pos] for seq in sequences if pos < len(seq)]
            
            # Calculate frequencies
            unique_residues = set(residues)
            frequencies = {r: residues.count(r) / len(residues) for r in unique_residues}
            
            # Calculate information content (simplified)
            # IC = log2(num_possible) + sum(p * log2(p))
            ic = 0
            for freq in frequencies.values():
                if freq > 0:
                    ic += freq * np.log2(freq)
            
            ic = -ic  # Make positive
            info_content.append(ic)
        
        return info_content
    
    def generate_ascii_logo(self, sequences):
        """Generate ASCII representation of motif logo."""
        if not sequences:
            return "No sequences provided"
        
        length = len(sequences[0])
        
        # Calculate frequencies at each position
        logo_lines = []
        header = "Position: " + " ".join([f"{i+1:2d}" for i in range(length)])
        logo_lines.append(header)
        logo_lines.append("-" * len(header))
        
        # Get all unique residues
        all_residues = set()
        for seq in sequences:
            all_residues.update(seq)
        
        # For each residue, show conservation
        for residue in sorted(all_residues):
            line = f"{residue:9s} "
            for pos in range(length):
                residues_at_pos = [seq[pos] for seq in sequences if pos < len(seq)]
                count = residues_at_pos.count(residue)
                freq = count / len(residues_at_pos)
                
                # Use characters to represent frequency
                if freq > 0.8:
                    symbol = "█"
                elif freq > 0.5:
                    symbol = "▓"
                elif freq > 0.2:
                    symbol = "▒"
                elif freq > 0:
                    symbol = "░"
                else:
                    symbol = " "
                
                line += f"{symbol:2s} "
            
            logo_lines.append(line)
        
        return "\n".join(logo_lines)
    
    def generate_weblogo_commands(self, sequences, output_file="motif_logo.png"):
        """Generate WebLogo command line instructions."""
        # Save sequences to FASTA format
        fasta_content = []
        for i, seq in enumerate(sequences):
            fasta_content.append(f">seq{i+1}")
            fasta_content.append(seq)
        
        newline = '\n'
        commands = f"""# Motif Logo Generation Commands
# Using WebLogo (https://weblogo.berkeley.edu/)

# Step 1: Save sequences to FASTA file
cat > sequences.fa << 'EOF'
{newline.join(fasta_content)}
EOF

# Step 2: Convert to alignment format (if needed)
# Step 3: Generate logo using WebLogo
weblogo -f sequences.fa -o {output_file} -F png \
    --title "Sequence Motif" \
    --color-scheme chemistry \
    --resolution 300

# Alternative: Use seq2logo
# seq2logo -f sequences.fa -o {output_file}
"""
        return commands


def main():
    parser = argparse.ArgumentParser(description="Motif Logo Generator")
    parser.add_argument("--sequences", "-s", help="File with sequences (one per line)")
    parser.add_argument("--format", "-f", choices=["ascii", "weblogo"], default="ascii",
                       help="Output format")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--demo", action="store_true", help="Generate demo logo")
    
    args = parser.parse_args()
    
    generator = MotifLogoGenerator()
    
    if args.demo:
        # Demo sequences
        sequences = [
            "ACGTACGT",
            "ACGTACGT",
            "ACGTACGT",
            "ACGTTCGT",
            "ACGAACGT"
        ]
    elif args.sequences:
        with open(args.sequences) as f:
            sequences = [line.strip() for line in f if line.strip()]
    else:
        print("Use --demo or provide --sequences file")
        return
    
    if args.format == "ascii":
        logo = generator.generate_ascii_logo(sequences)
        print(logo)
    else:
        commands = generator.generate_weblogo_commands(sequences)
        print(commands)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(logo if args.format == "ascii" else commands)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
