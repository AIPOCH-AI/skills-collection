#!/usr/bin/env python3
"""
CRISPR gRNA Designer - Design optimal guide RNAs for gene editing.

This script designs gRNA sequences targeting specific gene exons,
scores their predicted efficiency, and predicts off-target effects.

Usage:
    python main.py --gene TP53 --exon 4 --output results.json
    python main.py --gene BRCA1 --max-mismatches 2 --gc-min 35
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import math

# Try to import optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from Bio import SeqIO
    from Bio.Seq import Seq
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False


@dataclass
class GuideRNA:
    """Represents a candidate gRNA with scores and metadata."""
    id: str
    gene: str
    exon: int
    sequence: str
    pam: str
    position: str
    strand: str
    gc_content: float
    efficiency_score: float
    off_target_count: int = 0
    off_targets: List[Dict] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.off_targets is None:
            self.off_targets = []
        if self.warnings is None:
            self.warnings = []


class GRNADesigner:
    """Main class for gRNA design and scoring."""
    
    # Doench et al. 2014 position-specific scoring matrix (simplified)
    POSITION_WEIGHTS = {
        1: -0.097377, 2: -0.097377, 3: -0.027388, 4: -0.168522,
        5: -0.100259, 6: 0.019786, 7: 0.033438, 8: 0.102702,
        9: 0.142613, 10: 0.025298, 11: 0.111993, 12: 0.130075,
        13: 0.116803, 14: 0.141113, 15: 0.147290, 16: 0.105579,
        17: 0.093110, 18: 0.174167, 19: 0.195515, 20: 0.140337
    }
    
    # Nucleotide preferences at specific positions
    NUC_PREFERENCES = {
        20: {'G': 0.3, 'A': -0.1, 'C': 0.0, 'T': -0.1},  # PAM-proximal
        19: {'C': 0.2, 'G': 0.1, 'A': -0.1, 'T': 0.0},
        18: {'G': 0.15, 'C': 0.1, 'A': -0.05, 'T': 0.0},
    }
    
    def __init__(self, genome_build: str = "hg38", pam: str = "NGG"):
        self.genome_build = genome_build
        self.pam = pam.upper()
        self.pam_regex = self._pam_to_regex(pam)
        
    def _pam_to_regex(self, pam: str) -> str:
        """Convert PAM sequence to regex pattern."""
        pam_map = {
            'N': '[ATCG]', 'R': '[AG]', 'Y': '[CT]', 
            'M': '[AC]', 'K': '[GT]', 'S': '[GC]',
            'W': '[AT]', 'H': '[ATC]', 'B': '[GTC]',
            'V': '[GCA]', 'D': '[GAT]', 'A': 'A',
            'T': 'T', 'C': 'C', 'G': 'G'
        }
        pattern = ''.join(pam_map.get(b, b) for b in pam.upper())
        return re.compile(f'(?=({pattern}))')
    
    def fetch_gene_sequence(self, gene_symbol: str, exon: Optional[int] = None) -> Dict:
        """
        Fetch gene sequence from Ensembl REST API.
        
        In production, this would query Ensembl. For demo, returns mock data.
        """
        if not HAS_REQUESTS:
            # Return mock sequence for testing
            return self._get_mock_sequence(gene_symbol, exon)
        
        # Real Ensembl API query would go here
        # url = f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene_symbol}"
        # ...
        return self._get_mock_sequence(gene_symbol, exon)
    
    def _get_mock_sequence(self, gene: str, exon: Optional[int]) -> Dict:
        """Generate mock sequence for testing/demo purposes."""
        # Mock TP53 exon 4 sequence with multiple PAM sites
        mock_sequences = {
            'TP53': {
                4: {
                    'sequence': (
                        'ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTA'
                        'TGGCCTCCTGTGCTGCTGCTGTGCTGACAGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTG'
                        'CTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTG'
                    ),
                    'chromosome': '17',
                    'start': 7669600,
                    'gene': 'TP53'
                }
            },
            'BRCA1': {
                2: {
                    'sequence': (
                        'ATGGTGTCCAGGGAGCTGCTGGTGGAAGATGGCGAGTCTTACACCTGCTGCTGCTGCTGCTGCTG'
                        'CTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTG'
                        'AGCGCTGCTCAGATAGCGATGGTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTG'
                    ),
                    'chromosome': '17',
                    'start': 43044295,
                    'gene': 'BRCA1'
                }
            }
        }
        
        gene_data = mock_sequences.get(gene, mock_sequences['TP53'])
        if exon and exon in gene_data:
            return gene_data[exon]
        return gene_data.get(4, gene_data.get(list(gene_data.keys())[0]))
    
    def find_pam_sites(self, sequence: str, guide_length: int = 20) -> List[Dict]:
        """
        Find all PAM-adjacent target sites in a sequence.
        
        Returns list of dicts with position, strand, and target sequence.
        """
        sites = []
        seq = sequence.upper()
        
        # Find PAM on forward strand (NGG pattern)
        for match in self.pam_regex.finditer(seq):
            pam_start = match.start()
            guide_start = pam_start - guide_length
            
            if guide_start >= 0:
                guide_seq = seq[guide_start:pam_start]
                pam_seq = match.group(1)
                
                sites.append({
                    'position': pam_start,
                    'strand': '+',
                    'guide': guide_seq,
                    'pam': pam_seq,
                    'full_target': guide_seq + pam_seq
                })
        
        # Find PAM on reverse strand (reverse complement)
        rev_comp = self._reverse_complement(seq)
        seq_len = len(seq)
        
        for match in self.pam_regex.finditer(rev_comp):
            pam_start = match.start()
            guide_start = pam_start - guide_length
            
            if guide_start >= 0:
                guide_seq = rev_comp[guide_start:pam_start]
                pam_seq = match.group(1)
                
                # Convert positions back to forward strand coordinates
                actual_guide_end = seq_len - pam_start
                actual_guide_start = actual_guide_end - guide_length
                
                sites.append({
                    'position': actual_guide_start,
                    'strand': '-',
                    'guide': self._reverse_complement(guide_seq),
                    'pam': self._reverse_complement(pam_seq),
                    'full_target': self._reverse_complement(guide_seq + pam_seq)
                })
        
        return sites
    
    def _reverse_complement(self, seq: str) -> str:
        """Return reverse complement of DNA sequence."""
        complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
        return ''.join(complement.get(b, b) for b in reversed(seq.upper()))
    
    def calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content percentage."""
        seq = sequence.upper()
        gc_count = seq.count('G') + seq.count('C')
        return (gc_count / len(seq)) * 100 if seq else 0.0
    
    def score_efficiency(self, guide_seq: str) -> float:
        """
        Calculate on-target efficiency score (0-1) using position-specific rules.
        
        Based on Doench et al. 2014 scoring algorithm.
        """
        seq = guide_seq.upper()
        if len(seq) != 20:
            # Pad or truncate to 20bp
            seq = seq[:20].ljust(20, 'N')
        
        score = 0.5  # Base score
        
        # Apply position-specific weights
        for i, base in enumerate(seq, 1):
            if i in self.POSITION_WEIGHTS:
                score += self.POSITION_WEIGHTS[i]
            
            # Apply nucleotide preferences
            if i in self.NUC_PREFERENCES and base in self.NUC_PREFERENCES[i]:
                score += self.NUC_PREFERENCES[i][base]
        
        # GC content penalty
        gc = self.calculate_gc_content(seq)
        if gc < 40:
            score -= (40 - gc) * 0.01
        elif gc > 60:
            score -= (gc - 60) * 0.01
        
        # Poly-T penalty (RNA Pol III terminator)
        if 'TTTT' in seq or 'UUUU' in seq.replace('T', 'U'):
            score -= 0.2
        
        # Clamp to 0-1 range
        return max(0.0, min(1.0, score))
    
    def check_off_targets(self, guide_seq: str, max_mismatches: int = 3) -> List[Dict]:
        """
        Predict potential off-target sites.
        
        In production, this would align against the genome using Bowtie2/BWA.
        For demo, returns simulated off-target data.
        """
        off_targets = []
        
        # Simulate off-target detection
        # In real implementation: bowtie2 -N 1 -L 20 -i S,0,2.50
        
        # Mock off-target for specific sequences
        if 'GAGCGCTGCT' in guide_seq.upper():
            off_targets.append({
                'chrom': 'chr17',
                'position': 43100000,
                'sequence': 'GAGCGCTGCTCAGATAGCGATGGT',
                'mismatches': 1,
                'cfd_score': 0.15,
                'context': 'intergenic'
            })
        
        return off_targets
    
    def filter_guides(self, guides: List[GuideRNA], 
                      gc_min: float = 30.0,
                      gc_max: float = 70.0,
                      min_efficiency: float = 0.3,
                      max_off_targets: int = 10) -> List[GuideRNA]:
        """Filter guides based on quality criteria."""
        filtered = []
        
        for guide in guides:
            # GC content filter
            if not (gc_min <= guide.gc_content <= gc_max):
                guide.warnings.append(f"GC content {guide.gc_content:.1f}% outside range")
            
            # Efficiency filter
            if guide.efficiency_score < min_efficiency:
                guide.warnings.append(f"Low efficiency score: {guide.efficiency_score:.2f}")
            
            # Off-target filter
            if guide.off_target_count > max_off_targets:
                guide.warnings.append(f"High off-target count: {guide.off_target_count}")
            
            # Poly-T check
            if 'TTTT' in guide.sequence.upper():
                guide.warnings.append("Contains Poly-T tract")
            
            filtered.append(guide)
        
        # Sort by efficiency score descending
        filtered.sort(key=lambda x: x.efficiency_score, reverse=True)
        return filtered
    
    def design_grnas(self, gene_symbol: str, 
                     target_exon: Optional[int] = None,
                     guide_length: int = 20,
                     gc_min: float = 30.0,
                     gc_max: float = 70.0,
                     max_mismatches: int = 3,
                     off_target_check: bool = True) -> Dict:
        """
        Main method to design gRNAs for a target gene.
        
        Args:
            gene_symbol: HGNC gene symbol
            target_exon: Specific exon number (None = all coding exons)
            guide_length: gRNA length in bp
            gc_min: Minimum GC content percentage
            gc_max: Maximum GC content percentage
            max_mismatches: Max mismatches for off-target prediction
            off_target_check: Enable off-target prediction
        
        Returns:
            Dictionary with gene info and list of GuideRNA objects
        """
        # Fetch gene sequence
        gene_data = self.fetch_gene_sequence(gene_symbol, target_exon)
        sequence = gene_data['sequence']
        
        # Find all PAM sites
        pam_sites = self.find_pam_sites(sequence, guide_length)
        
        # Score each potential guide
        guides = []
        for i, site in enumerate(pam_sites):
            guide_seq = site['guide']
            
            # Calculate metrics
            gc_content = self.calculate_gc_content(guide_seq)
            efficiency = self.score_efficiency(guide_seq)
            
            # Predict off-targets
            off_targets = []
            off_target_count = 0
            if off_target_check:
                off_targets = self.check_off_targets(guide_seq, max_mismatches)
                off_target_count = len(off_targets)
            
            # Create guide object
            guide = GuideRNA(
                id=f"{gene_symbol}_E{target_exon or 'X'}_G{i+1}",
                gene=gene_symbol,
                exon=target_exon or 0,
                sequence=guide_seq,
                pam=site['pam'],
                position=f"chr{gene_data['chromosome']}:{gene_data['start'] + site['position']}-{gene_data['start'] + site['position'] + guide_length}",
                strand=site['strand'],
                gc_content=round(gc_content, 1),
                efficiency_score=round(efficiency, 3),
                off_target_count=off_target_count,
                off_targets=off_targets
            )
            
            guides.append(guide)
        
        # Apply filters and sort
        guides = self.filter_guides(guides, gc_min, gc_max)
        
        return {
            'gene': gene_symbol,
            'genome': self.genome_build,
            'exon': target_exon,
            'total_candidates': len(pam_sites),
            'guides': [asdict(g) for g in guides]
        }


def main():
    """Command-line interface for gRNA designer."""
    parser = argparse.ArgumentParser(
        description='Design CRISPR gRNA sequences for gene editing'
    )
    parser.add_argument('--gene', '-g', required=True,
                        help='Gene symbol (e.g., TP53)')
    parser.add_argument('--exon', '-e', type=int,
                        help='Target exon number')
    parser.add_argument('--genome', default='hg38',
                        choices=['hg38', 'hg19', 'mm10'],
                        help='Reference genome (default: hg38)')
    parser.add_argument('--pam', default='NGG',
                        help='PAM sequence (default: NGG)')
    parser.add_argument('--guide-length', type=int, default=20,
                        help='gRNA length in bp (default: 20)')
    parser.add_argument('--gc-min', type=float, default=30.0,
                        help='Minimum GC content %% (default: 30)')
    parser.add_argument('--gc-max', type=float, default=70.0,
                        help='Maximum GC content %% (default: 70)')
    parser.add_argument('--max-mismatches', type=int, default=3,
                        help='Max mismatches for off-target (default: 3)')
    parser.add_argument('--no-offtarget', action='store_true',
                        help='Disable off-target prediction')
    parser.add_argument('--output', '-o',
                        help='Output JSON file (default: stdout)')
    parser.add_argument('--top', type=int, default=10,
                        help='Show top N guides (default: 10)')
    
    args = parser.parse_args()
    
    # Initialize designer
    designer = GRNADesigner(
        genome_build=args.genome,
        pam=args.pam
    )
    
    # Design gRNAs
    print(f"Designing gRNAs for {args.gene} (exon {args.exon or 'all'})...", 
          file=sys.stderr)
    
    results = designer.design_grnas(
        gene_symbol=args.gene,
        target_exon=args.exon,
        guide_length=args.guide_length,
        gc_min=args.gc_min,
        gc_max=args.gc_max,
        max_mismatches=args.max_mismatches,
        off_target_check=not args.no_offtarget
    )
    
    # Limit output
    results['guides'] = results['guides'][:args.top]
    
    # Output results
    output = json.dumps(results, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results saved to {args.output}", file=sys.stderr)
    else:
        print(output)
    
    # Print summary
    print(f"\nSummary: {len(results['guides'])} guides designed", 
          file=sys.stderr)
    if results['guides']:
        top = results['guides'][0]
        print(f"Top guide: {top['sequence']} (score: {top['efficiency_score']})",
              file=sys.stderr)


if __name__ == '__main__':
    main()
