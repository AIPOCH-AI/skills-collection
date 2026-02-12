---
name: multi-omics-integration-strategist
description: Design multi-omics integration strategies for transcriptomics, proteomics,
  and metabolomics data analysis
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

# Skill: Multi-Omics Integration Strategist (ID: 204)

## Overview

Designs multi-omics (transcriptomics RNA, proteomics Pro, metabolomics Met) joint analysis schemes, performs cross-validation at the pathway level, and provides systems biology-level integrated analysis strategies.

## Use Cases

- Systems biology mechanism research for complex diseases
- Biomarker discovery and validation
- Drug target identification and pathway validation
- Multi-omics data quality assessment and consistency analysis

## Directory Structure

```
.
├── SKILL.md                 # This file - Skill documentation
├── config/
│   └── pathways.json        # Pathway database configuration
├── scripts/
│   └── main.py             # Main analysis script
├── templates/
│   └── report_template.md   # Analysis report template
└── examples/
    └── sample_data/         # Sample datasets
```

## Input

### Required Files

| File | Format | Description |
|------|------|------|
| `rna_data.csv` | CSV | Transcriptomics data: Gene ID, expression value, differential analysis results |
| `pro_data.csv` | CSV | Proteomics data: Protein ID, abundance value, differential analysis results |
| `met_data.csv` | CSV | Metabolomics data: Metabolite ID, concentration value, differential analysis results |

### Input Format Specifications

#### RNA Data (rna_data.csv)
```csv
gene_id,gene_name,log2fc,pvalue,padj,sample_A,sample_B,...
ENSG00000139618,BRCA1,1.23,0.001,0.005,12.5,13.2,...
```

#### Protein Data (pro_data.csv)
```csv
protein_id,gene_name,log2fc,pvalue,padj,sample_A,sample_B,...
P38398,BRCA1,0.85,0.002,0.008,2450,2890,...
```

#### Metabolite Data (met_data.csv)
```csv
metabolite_id,metabolite_name,kegg_id,log2fc,pvalue,padj,...
C00187,Cholesterol,C00187,-1.45,0.003,0.012,...
```

## Integration Strategy

### 1. ID Mapping Layer

- **RNA → Protein**: Mapping through Gene Symbol / UniProt ID
- **Protein → Metabolite**: Association through KEGG/Reactome enzyme-reaction-metabolite
- **RNA → Metabolite**: Indirect association through KEGG pathway

### 2. Pathway Mapping

Supported databases:
- **KEGG** (Kyoto Encyclopedia of Genes and Genomes)
- **Reactome**
- **WikiPathways**
- **GO (Gene Ontology)** - Biological Process

### 3. Cross-Validation Methods

#### 3.1 Directional Consistency Validation
- Whether the change direction of genes/proteins/metabolites in the same pathway is consistent
- Score: +1 (consistent), -1 (opposite), 0 (no data)

#### 3.2 Correlation Validation
- Pearson/Spearman correlation analysis
- Cross-omics expression profile clustering

#### 3.3 Pathway Enrichment Concordance
- Independent enrichment analysis for each omics
- Common enriched pathway identification

#### 3.4 Network Topology Validation
- Construct cross-omics regulatory network
- Identify key nodes (Hub genes/proteins/metabolites)

## Output

### 1. Integration Report (`integration_report.md`)

```markdown
# Multi-Omics Integration Analysis Report

## Executive Summary
- Sample count: RNA=30, Pro=28, Met=25
- Mapping success rate: RNA-Pro=85%, Pro-Met=62%
- Pathway coverage: 342 KEGG pathways

## Cross-Validation Results
### Highly Consistent Pathways (Score > 0.8)
1. Glycolysis/Gluconeogenesis (Score=0.92)
2. Citrate cycle (TCA cycle) (Score=0.88)

### Conflicting Pathways (Score < -0.3)
1. Fatty acid biosynthesis (Score=-0.45)

## Recommendations
- Focus on: Energy metabolism-related pathways
- Needs verification: Lipid metabolism pathway data quality
```

### 2. External Visualization Tools (Not Included)

This tool generates analysis results that can be visualized using external tools. Users may export results to:

| Chart Type | Purpose | External Tool Required |
|---------|------|---------|
|  Circos Plot | Cross-omics relationship panorama | matplotlib/circlize (user-installed) |
|  Pathway Heatmap | Pathway-level changes | seaborn/complexheatmap (user-installed) |
|  Sankey Diagram | Data flow mapping | plotly (user-installed) |
|  Network Graph | Molecular interaction network | networkx/cytoscape (networkx is included) |
|  Correlation Matrix | Cross-omics correlation | seaborn (user-installed) |
|  Bubble Plot | Integrated enrichment analysis | ggplot2/plotly (user-installed) |

**Note:** This skill focuses on data integration and analysis. Visualization requires separate installation of plotting libraries by the user.

### 3. Output Files

| File | Description |
|------|------|
| `mapped_ids.json` | ID mapping results |
| `pathway_scores.csv` | Pathway cross-validation scores |
| `consistency_matrix.csv` | Cross-omics consistency matrix |
| `network_edges.csv` | Network edge list |
| `report.html` | Interactive HTML report |

## Usage

### Basic Usage

```bash
python scripts/main.py \
  --rna rna_data.csv \
  --pro pro_data.csv \
  --met met_data.csv \
  --output ./results
```

### Advanced Options

```bash
python scripts/main.py \
  --rna rna_data.csv \
  --pro pro_data.csv \
  --met met_data.csv \
  --pathway-db KEGG,Reactome \
  --id-mapping config/mapping.json \
  --method correlation+enrichment+network \
  --output ./results \
  --format html,csv,json
```

## Configuration

### config/pathways.json

```json
{
  "databases": {
    "KEGG": {
      "enabled": true,
      "organism": "hsa",
      "min_genes": 3
    },
    "Reactome": {
      "enabled": true,
      "min_genes": 5
    }
  },
  "mapping": {
    "rna_to_protein": "gene_symbol",
    "protein_to_metabolite": "enzyme_commission"
  }
}
```

## Dependencies

- Python >= 3.8
- pandas >= 1.3.0
- numpy >= 1.21.0
- scipy >= 1.7.0
- scikit-learn >= 1.0.0
- networkx >= 2.6.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0
- gseapy >= 1.0.0 (Pathway enrichment analysis)

## References

1. Subramanian et al. (2005) PNAS - GSEA method
2. Kamburov et al. (2011) NAR - ConsensusPathDB
3. Chin et al. (2018) Nature Communications - Multi-omics integration methods review

## Version

- **Version**: 1.0.0
- **Last Updated**: 2026-02-06
- **Author**: OpenClaw Bioinformatics Team

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

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--rna` | str | Required |  |
| `--pro` | str | Required |  |
| `--met` | str | Required |  |
| `--output` | str | './results' |  |
| `--databases` | str | 'KEGG' |  |
| `--create-sample` | str | Required | Create sample data for testing |
| `--format` | str | 'md |  |
