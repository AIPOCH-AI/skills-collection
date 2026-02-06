# BLAST Documentation

## Overview

BLAST (Basic Local Alignment Search Tool) is an algorithm for comparing primary biological sequence information, such as the amino-acid sequences of proteins or the nucleotides of DNA sequences.

## BLAST Programs

### blastn
- **Query**: Nucleotide
- **Database**: Nucleotide
- **Use Case**: Search nucleotide databases using a nucleotide query

### blastp
- **Query**: Protein
- **Database**: Protein
- **Use Case**: Search protein databases using a protein query

### blastx
- **Query**: Nucleotide (translated)
- **Database**: Protein
- **Use Case**: Search protein databases using a translated nucleotide query

### tblastn
- **Query**: Protein
- **Database**: Nucleotide (translated)
- **Use Case**: Search translated nucleotide databases using a protein query

### tblastx
- **Query**: Nucleotide (translated)
- **Database**: Nucleotide (translated)
- **Use Case**: Search translated nucleotide databases using a translated nucleotide query

## Key Metrics

### E-value (Expect Value)
- Statistical significance threshold
- Lower is better
- E-value < 0.01 typically considered significant
- Default: 10

### Bit Score
- Normalized score for comparison across searches
- Higher is better
- Derived from raw alignment score

### Identity
- Percentage of identical matches in alignment
- Calculated as: (identical positions / alignment length) × 100

### Positives
- For protein alignments, similar amino acids (conservative substitutions)
- Includes identical + similar residues

## Common Databases

| Database | Type | Description |
|----------|------|-------------|
| nr | Protein | Non-redundant protein sequences |
| nt | Nucleotide | Nucleotide collection |
| swissprot | Protein | Swiss-Prot protein sequences |
| pdb | Protein | Protein Data Bank sequences |
| refseq_protein | Protein | NCBI Reference Sequence proteins |
| refseq_rna | Nucleotide | NCBI Reference Sequence RNAs |
| est | Nucleotide | Expressed Sequence Tags |
| gss | Nucleotide | Genome Survey Sequences |

## Best Practices

1. **Choose appropriate program**: Match query and database types correctly
2. **Set E-value threshold**: Start with 0.001 for high-confidence hits
3. **Filter low-complexity regions**: Use appropriate filters to avoid spurious hits
4. **Check alignment length**: Short alignments may be less reliable
5. **Verify identity percentage**: Higher identity indicates closer evolutionary relationship

## References

- Altschul SF, Gish W, Miller W, Myers EW, Lipman DJ. Basic local alignment search tool. J Mol Biol. 1990;215(3):403-410.
- NCBI BLAST Help: https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs
