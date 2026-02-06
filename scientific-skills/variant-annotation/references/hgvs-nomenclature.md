# HGVS Nomenclature Guide

## Overview
The Human Genome Variation Society (HGVS) nomenclature provides standardized rules for describing DNA, RNA, and protein sequence variants.

- **Website**: https://varnomen.hgvs.org/
- **Current Version**: HGVS Recommendations v20.05 (May 2020)

## Variant Types and Notation

### DNA Level (c.)

| Type | Example | Description |
|------|---------|-------------|
| Substitution | `c.5096G>A` | G changed to A at position 5096 |
| Deletion | `c.76del` | Deletion of nucleotide 76 |
| Deletion | `c.76_80del` | Deletion of nucleotides 76-80 |
| Insertion | `c.76_77insG` | Insertion of G between 76 and 77 |
| Duplication | `c.76dup` | Duplication of nucleotide 76 |
| Inversion | `c.76_80inv` | Inversion of nucleotides 76-80 |
| Deletion-Insertion | `c.76_80delinsTAG` | Deletion of 76-80, insertion of TAG |

### Genomic Level (g.)

```
g.123456G>A          # Substitution
g.123_125del         # Deletion
g.123_124insATC      # Insertion
g.123dup             # Duplication
```

### Coding DNA Reference Sequence
- Use coding DNA reference sequence (NM_ accession)
- Position 1 is A of ATG initiation codon
- 5' UTR: negative positions (c.-1, c.-2...)
- 3' UTR: asterisk notation (c.*1, c.*2...)
- Introns: base after exon + intron position (c.77+1, c.77+2)

### Protein Level (p.)

| Type | Example | Description |
|------|---------|-------------|
| Missense | `p.Arg1699Gln` or `p.R1699Q` | Arginine to Glutamine at position 1699 |
| Nonsense | `p.Arg1699*` or `p.R1699X` | Arginine to Stop codon |
| Deletion | `p.Gly76del` or `p.G76del` | Deletion of Glycine at position 76 |
| Frameshift | `p.Glu5ValfsTer15` | Frameshift starting at Glu5, stops at codon 15 |
| Duplication | `p.Gly76dup` | Duplication of Glycine 76 |
| Extension | `p.*110Glnext*17` | Stop codon extension |

## Reference Sequence Prefixes

| Prefix | Type | Example |
|--------|------|---------|
| **NC_** | Genomic chromosome | NC_000017.11 |
| **NG_** | Genomic gene | NG_005905.2 |
| **NM_** | Coding transcript | NM_007294.3 |
| **NR_** | Non-coding transcript | NR_027676.2 |
| **NP_** | Protein | NP_009225.1 |
| **LRG_** | Locus Reference Genomic | LRG_292 |

## Position Numbering

### Genomic (g.)
- Continuous numbering from 5' to 3'
- No negative positions
- Chromosome-specific

### Coding DNA (c.)
- **+1** = A of ATG initiation codon
- **5' UTR**: c.-1, c.-2, ... (up to c.-1000 or more)
- **3' UTR**: c.*1, c.*2, ... (up to c.*1000 or more)
- **Introns**: 
  - c.77+1, c.77+2 (donor site, after exon 77)
  - c.78-1, c.78-2 (acceptor site, before exon 78)

### Protein (p.)
- **+1** = Methionine (initiator)
- **Ter** or ***** = Stop codon
- **fs** = Frameshift

## Special Cases

### Splice Site Variants
```
c.77+1G>A      # Canonical splice donor
c.78-2A>G      # Canonical splice acceptor
c.77+5G>C      # Splice donor +5 position
```

### Large Deletions/Duplications
```
c.(-50_+100)_(+200_+300)del   # Large deletion affecting UTR
c.123_678dup                   # Large duplication
```

### Complex Variants
```
c.76_80delinsTAG    # Delins (deletion-insertion)
c.76_80conATA       # Conversion
```

## Common Mistakes to Avoid

1. ❌ `c.76delC` → ✅ `c.76del` (deleted base not repeated)
2. ❌ `p.R1699Q` without transcript → ✅ Include transcript: `NM_007294.3:c.5096G>A (p.Arg1699Gln)`
3. ❌ `c.76-10_77+10del` → Use genomic for large intronic: `NC_000017.11:g.41234567_41234600del`
4. ❌ `p.C22S` for cysteine loss → ✅ Use `p.C22S` for change, `p.C22*` for stop

## Validation Tools

| Tool | URL | Description |
|------|-----|-------------|
| Mutalyzer | https://mutalyzer.nl/ | HGVS syntax checker and converter |
| Variant Validator | https://variantvalidator.org/ | Comprehensive validation |
| ClinGen Allele Registry | https://reg.clinicalgenome.org/ | Normalization and aliases |

## Reference

- Den Dunnen JT, et al. HGVS recommendations for the description of sequence variants: 2016 update. Hum Mutat. 2016;37(6):564-569.
- https://varnomen.hgvs.org/
