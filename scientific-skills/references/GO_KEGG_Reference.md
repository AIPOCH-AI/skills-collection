# GO/KEGG Enrichment Analysis References

## Table of Contents

1. [Statistical Methods](#statistical-methods)
2. [GO Ontology Structure](#go-ontology-structure)
3. [KEGG Pathway Database](#kegg-pathway-database)
4. [ID Conversion Reference](#id-conversion-reference)
5. [Visualization Types](#visualization-types)
6. [Troubleshooting](#troubleshooting)

---

## Statistical Methods

### Hypergeometric Test

The hypergeometric test is used for over-representation analysis (ORA). It calculates the probability of observing x or more genes from a gene set in the query list.

```
P(X >= k) = 1 - Σ(i=0 to k-1) [C(K,i) * C(N-K, n-i)] / C(N,n)

Where:
- N = total number of genes in background
- K = number of genes in the pathway/GO term
- n = number of genes in query list
- k = number of genes from query list in the pathway/GO term
```

### Fisher's Exact Test

Used when sample sizes are small. Similar to hypergeometric test but uses contingency table approach.

### Gene Set Enrichment Analysis (GSEA)

For ranked gene lists (e.g., by log2FoldChange). Tests if genes from a set are randomly distributed or enriched at the top/bottom of the ranked list.

---

## GO Ontology Structure

### Biological Process (BP)

Large-scale biological goals accomplished by ordered assemblies of molecular functions.

Examples:
- `GO:0006915` - apoptotic process
- `GO:0006355` - regulation of transcription, DNA-templated
- `GO:0008283` - cell population proliferation
- `GO:0006954` - inflammatory response
- `GO:0007049` - cell cycle

### Molecular Function (MF)

Activities that occur at the molecular level.

Examples:
- `GO:0005515` - protein binding
- `GO:0003677` - DNA binding
- `GO:0003824` - catalytic activity
- `GO:0004872` - receptor activity
- `GO:0016740` - transferase activity

### Cellular Component (CC)

Locations in the cell where a gene product is active.

Examples:
- `GO:0005634` - nucleus
- `GO:0005737` - cytoplasm
- `GO:0005886` - plasma membrane
- `GO:0005829` - cytosol
- `GO:0016020` - membrane

### GO Term Levels

- Level 1: Root terms (molecular_function, biological_process, cellular_component)
- Level 2-3: Broad categories
- Level 4-6: Specific functional descriptions
- Level 7+: Very specific terms

---

## KEGG Pathway Database

### Pathway Categories

1. **Metabolism**
   - Carbohydrate metabolism
   - Energy metabolism
   - Lipid metabolism
   - Nucleotide metabolism
   - Amino acid metabolism

2. **Genetic Information Processing**
   - Transcription
   - Translation
   - Folding, sorting and degradation
   - Replication and repair

3. **Environmental Information Processing**
   - Membrane transport
   - Signal transduction
   - Signaling molecules and interaction

4. **Cellular Processes**
   - Cell growth and death
   - Cell communication
   - Transport and catabolism

5. **Organismal Systems**
   - Immune system
   - Endocrine system
   - Circulatory system
   - Nervous system

6. **Human Diseases**
   - Cancers
   - Immune diseases
   - Neurodegenerative diseases
   - Cardiovascular diseases

### KEGG Organism Codes

| Code | Species | Database |
|------|---------|----------|
| hsa | Homo sapiens (human) | org.Hs.eg.db |
| mmu | Mus musculus (mouse) | org.Mm.eg.db |
| rno | Rattus norvegicus (rat) | org.Rn.eg.db |
| dre | Danio rerio (zebrafish) | org.Dr.eg.db |
| dme | Drosophila melanogaster (fruit fly) | org.Dm.eg.db |
| sce | Saccharomyces cerevisiae (yeast) | org.Sc.sgd.db |
| ath | Arabidopsis thaliana | org.At.tair.db |
| cel | Caenorhabditis elegans | org.Ce.eg.db |

---

## ID Conversion Reference

### Supported ID Types

1. **SYMBOL** - Gene symbols (e.g., TP53, BRCA1)
2. **ENTREZID** - NCBI Entrez Gene ID (e.g., 7157)
3. **ENSEMBL** - Ensembl Gene ID (e.g., ENSG00000141510)
4. **REFSEQ** - RefSeq ID (e.g., NM_000546)
5. **UNIPROT** - UniProt ID (e.g., P04637)

### Conversion Table Example

| Symbol | ENTREZID | ENSEMBL | RefSeq mRNA |
|--------|----------|---------|-------------|
| TP53 | 7157 | ENSG00000141510 | NM_000546 |
| BRCA1 | 672 | ENSG00000012048 | NM_007294 |
| EGFR | 1956 | ENSG00000146648 | NM_005228 |
| PTEN | 5728 | ENSG00000171862 | NM_000314 |
| MYC | 4609 | ENSG00000136997 | NM_002467 |

---

## Visualization Types

### Bar Plot

Shows enrichment significance (p-values) for top terms.

**Interpretation:**
- X-axis: -log10(p-value) or gene ratio
- Y-axis: Enriched terms
- Color: p-value or adjusted p-value
- Bar length indicates enrichment strength

### Dot Plot

Shows relationship between gene ratio and significance.

**Interpretation:**
- X-axis: Gene ratio (k/n)
- Y-axis: Enriched terms
- Dot size: Number of genes in the term
- Color: p-value or adjusted p-value

### Gene-Concept Network (Cnet Plot)

Shows relationships between genes and enriched terms.

**Interpretation:**
- Circles: Enriched terms
- Dots: Genes
- Lines: Gene-term associations
- Color: Fold change or p-value

### Enrichment Map

Network visualization of enriched terms where edges connect related terms.

**Interpretation:**
- Nodes: Enriched terms
- Edges: Similarity between terms (based on shared genes)
- Clustering: Groups functionally related terms

### Pathview

Displays gene expression data on KEGG pathway maps.

---

## Troubleshooting

### Common Issues

#### 1. "No significant terms found"

**Possible causes:**
- Gene list too small (< 10 genes)
- P-value cutoff too stringent
- Wrong organism selected
- Gene IDs not recognized

**Solutions:**
- Increase p-value cutoff (--pvalue-cutoff 0.1)
- Check organism is correct
- Verify gene ID format matches --id-type
- Try converting gene IDs to another format

#### 2. "KEGG API connection failed"

**Solutions:**
- Check internet connection
- KEGG API may be temporarily unavailable
- Try again later (rate limits: 3 requests/second)

#### 3. "Package not found" errors

**Solutions:**
```r
# Install BiocManager if needed
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

# Install required packages
BiocManager::install(c("clusterProfiler", "org.Hs.eg.db", 
                       "enrichplot", "pathview"))
```

#### 4. Memory errors with large gene lists

**Solutions:**
- Filter gene list (focus on significant DEGs)
- Increase max genes parameter (--max-genes 1000)
- Run on machine with more RAM

### Best Practices

1. **Background gene set**: Use all expressed genes, not genome-wide
2. **Gene list size**: 50-500 genes works best for ORA
3. **Multiple testing**: Always use adjusted p-values (q-value) for interpretation
4. **Cutoff selection**: p < 0.05, q < 0.2 are common thresholds
5. **Result interpretation**: Focus on top 10-20 terms by significance

### FAQ

**Q: Should I use GO or KEGG?**
A: Both provide complementary information. GO describes functions hierarchically; KEGG focuses on pathways and interactions.

**Q: What background should I use?**
A: Use all genes expressed in your experiment (e.g., all genes with counts > 0 in RNA-seq), not the entire genome.

**Q: How do I interpret enrichment ratio?**
A: GeneRatio/BgRatio > 1 indicates enrichment. Higher values mean stronger enrichment.

**Q: Can I use this for non-model organisms?**
A: Limited support via KEGG. For unsupported organisms, use ortholog mapping to a related model organism.

---

## References

1. Yu G, Wang LG, Han Y, He QY. clusterProfiler: an R package for comparing biological themes among gene clusters. OMICS. 2012;16(5):284-287.

2. Kanehisa M, Goto S. KEGG: kyoto encyclopedia of genes and genomes. Nucleic Acids Res. 2000;28(1):27-30.

3. Ashburner M, et al. Gene ontology: tool for the unification of biology. Nat Genet. 2000;25(1):25-29.

4. Subramanian A, et al. Gene set enrichment analysis: a knowledge-based approach for interpreting genome-wide expression profiles. Proc Natl Acad Sci USA. 2005;102(43):15545-15550.
