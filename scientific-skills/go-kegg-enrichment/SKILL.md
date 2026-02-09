---
name: go-kegg-enrichment
description: "Performs GO (Gene Ontology) and KEGG pathway enrichment analysis on\
  \ gene lists.\nTrigger when: \n- User provides a list of genes (symbols or IDs)\
  \ and asks for enrichment analysis\n- User mentions \"GO enrichment\", \"KEGG enrichment\"\
  , \"pathway analysis\"\n- User wants to understand biological functions of gene\
  \ sets\n- User provides differentially expressed genes (DEGs) and asks for interpretation\n\
  - Input: gene list (file or inline), organism (human/mouse/rat), background gene\
  \ set (optional)\n- Output: enriched terms, statistics, visualizations (barplot,\
  \ dotplot, enrichment map)"
version: 1.0.0
category: Bioinfo
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
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

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited
## Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support
