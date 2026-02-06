---
name: sequence-alignment
description: Trigger when user needs to align DNA/protein sequences, compare biological sequences, search for similar sequences in databases, or perform BLAST-based similarity analysis. Use for bioinformatics sequence comparison tasks.
---

# Sequence Alignment

A skill for performing sequence alignment using NCBI BLAST API. Supports nucleotide and protein sequence comparison against major biological databases.

## Features

- **BLAST API Integration**: Query NCBI BLAST service for sequence similarity search
- **Multiple BLAST Programs**: blastn, blastp, blastx, tblastn, tblastx
- **Alignment Visualization**: Display results in human-readable format
- **Database Support**: nr, nt, swissprot, refseq, pdb, and more

## Usage

```bash
python scripts/main.py --sequence "ATGCGTACGTAGCTAGCTAG" --program blastn --database nt --output results.txt
```

### Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--sequence` | Query sequence (DNA/Protein) | Yes |
| `--program` | BLAST program: blastn, blastp, blastx, tblastn, tblastx | Yes |
| `--database` | Target database: nr, nt, swissprot, pdb, refseq_protein | Yes |
| `--output` | Output file path | No |
| `--format` | Output format: text, json, csv | No (default: text) |
| `--max_hits` | Maximum number of hits to return | No (default: 10) |
| `--evalue` | E-value threshold | No (default: 10) |

## Technical Difficulty

**Medium** - Requires understanding of BLAST algorithm, API handling with retry logic, and biological sequence formats.

## BLAST Programs Reference

| Program | Query Type | Database Type | Use Case |
|---------|-----------|---------------|----------|
| blastn | Nucleotide | Nucleotide | DNA vs DNA |
| blastp | Protein | Protein | Protein vs Protein |
| blastx | Nucleotide (translated) | Protein | DNA vs Protein |
| tblastn | Protein | Nucleotide (translated) | Protein vs DNA |
| tblastx | Nucleotide (translated) | Nucleotide (translated) | Translated DNA vs DNA |

## Example Workflows

### DNA Sequence Similarity Search
```bash
python scripts/main.py --sequence "ATGGCCCTGTGGATGCGCTTCTTAGTCG" --program blastn --database nt --max_hits 5
```

### Protein Sequence Alignment
```bash
python scripts/main.py --sequence "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGT" --program blastp --database swissprot --evalue 0.001
```

## Output Format

Results include:
- Query sequence info
- Hit definitions and accession numbers
- Alignment scores (bit score, e-value)
- Percent identity and similarity
- Alignment visualization with match/mismatch highlighting

## References

- [BLAST Documentation](references/blast_docs.md)
- [NCBI BLAST API Guide](references/ncbi_api_guide.md)
