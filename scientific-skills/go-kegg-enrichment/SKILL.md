---
name: go-kegg-enrichment
description: |
  Performs GO (Gene Ontology) and KEGG pathway enrichment analysis on gene lists.
  Trigger when: 
  - User provides a list of genes (symbols or IDs) and asks for enrichment analysis
  - User mentions "GO enrichment", "KEGG enrichment", "pathway analysis"
  - User wants to understand biological functions of gene sets
  - User provides differentially expressed genes (DEGs) and asks for interpretation
  - Input: gene list (file or inline), organism (human/mouse/rat), background gene set (optional)
  - Output: enriched terms, statistics, visualizations (barplot, dotplot, enrichment map)
---

# GO/KEGG Enrichment Analysis

Automated pipeline for Gene Ontology and KEGG pathway enrichment analysis with result interpretation and visualization.

## Features

- **GO Enrichment**: Biological Process (BP), Molecular Function (MF), Cellular Component (CC)
- **KEGG Pathway**: Pathway enrichment with organism-specific mapping
- **Multiple ID Support**: Gene symbols, Entrez IDs, Ensembl IDs, RefSeq
- **Statistical Methods**: Hypergeometric test, Fisher's exact test, GSEA support
- **Visualizations**: Bar plots, dot plots, enrichment maps, cnet plots
- **Result Interpretation**: Automatic biological significance summary

## Supported Organisms

| Common Name | Scientific Name | KEGG Code | OrgDB Package |
|-------------|-----------------|-----------|---------------|
| Human | Homo sapiens | hsa | org.Hs.eg.db |
| Mouse | Mus musculus | mmu | org.Mm.eg.db |
| Rat | Rattus norvegicus | rno | org.Rn.eg.db |
| Zebrafish | Danio rerio | dre | org.Dr.eg.db |
| Fly | Drosophila melanogaster | dme | org.Dm.eg.db |
| Yeast | Saccharomyces cerevisiae | sce | org.Sc.sgd.db |

## Usage

### Basic Usage

```python
# Run enrichment analysis with gene list
python scripts/main.py --genes gene_list.txt --organism human --output results/
```

### Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `--genes` | Path to gene list file (one gene per line) | - | Yes |
| `--organism` | Organism code (human/mouse/rat/zebrafish/fly/yeast) | human | No |
| `--id-type` | Gene ID type (symbol/entrez/ensembl/refseq) | symbol | No |
| `--background` | Background gene list file | all genes | No |
| `--pvalue-cutoff` | P-value cutoff for significance | 0.05 | No |
| `--qvalue-cutoff` | Adjusted p-value (q-value) cutoff | 0.2 | No |
| `--analysis` | Analysis type (go/kegg/all) | all | No |
| `--output` | Output directory | ./enrichment_results | No |
| `--format` | Output format (csv/tsv/excel/all) | all | No |

### Advanced Usage

```python
# GO enrichment only with specific ontology
python scripts/main.py \
    --genes deg_upregulated.txt \
    --organism mouse \
    --analysis go \
    --go-ontologies BP,MF \
    --pvalue-cutoff 0.01 \
    --output go_results/

# KEGG enrichment with custom background
python scripts/main.py \
    --genes treatment_genes.txt \
    --background all_expressed_genes.txt \
    --organism human \
    --analysis kegg \
    --qvalue-cutoff 0.05 \
    --output kegg_results/
```

## Input Format

### Gene List File
```
TP53
BRCA1
EGFR
MYC
KRAS
PTEN
```

### With Expression Values (for GSEA)
```
gene,log2FoldChange
TP53,2.5
BRCA1,-1.8
EGFR,3.2
```

## Output Files

```
output/
├── go_enrichment/
│   ├── GO_BP_results.csv       # Biological Process results
│   ├── GO_MF_results.csv       # Molecular Function results
│   ├── GO_CC_results.csv       # Cellular Component results
│   ├── GO_BP_barplot.pdf       # Visualization
│   ├── GO_MF_dotplot.pdf
│   └── GO_summary.txt          # Interpretation summary
├── kegg_enrichment/
│   ├── KEGG_results.csv        # Pathway results
│   ├── KEGG_barplot.pdf
│   ├── KEGG_dotplot.pdf
│   └── KEGG_pathview/          # Pathway diagrams
└── combined_report.html        # Interactive report
```

## Result Interpretation

The tool automatically generates biological interpretation including:

1. **Top Enriched Terms**: Significant GO terms/pathways ranked by enrichment ratio
2. **Functional Themes**: Clustered biological themes from enriched terms
3. **Key Genes**: Core genes driving enrichment in significant terms
4. **Network Relationships**: Gene-term relationship visualization
5. **Clinical Relevance**: Disease associations (for human genes)

## Technical Difficulty: **HIGH**

⚠️ **AI自主验收状态**: 需人工检查

This skill requires:
- R/Bioconductor environment with clusterProfiler
- Multiple annotation databases (org.*.eg.db)
- KEGG REST API access
- Complex visualization dependencies

## Dependencies

### Required R Packages
```r
install.packages(c("BiocManager", "ggplot2", "dplyr", "readr"))
BiocManager::install(c(
    "clusterProfiler", 
    "org.Hs.eg.db", "org.Mm.eg.db", "org.Rn.eg.db",
    "enrichplot", "pathview", "DOSE"
))
```

### Python Dependencies
```bash
pip install pandas numpy matplotlib seaborn rpy2
```

## Example Workflow

1. **Prepare Input**: Create gene list from DEG analysis
2. **Run Analysis**: Execute main.py with appropriate parameters
3. **Review Results**: Check generated CSV files and visualizations
4. **Interpret**: Read auto-generated summary for biological insights

## References

See `references/` for:
- clusterProfiler documentation
- KEGG API guide
- Statistical methods explanation
- Visualization examples

## Limitations

- Requires internet connection for KEGG database queries
- Large gene lists (>5000) may require increased memory
- Some pathways may not be available for all organisms
- KEGG API has rate limits (max 3 requests/second)
