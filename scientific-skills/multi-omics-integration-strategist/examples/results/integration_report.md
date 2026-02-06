# Multi-Omics Integration Analysis Report

## Executive Summary
- **Analysis Date**: 2026-02-06 06:02
- **RNA Samples**: 3 features × samples
- **Protein Samples**: 3 features × samples
- **Metabolite Samples**: 4 features × samples
- **Significant RNA**: 7
- **Significant Proteins**: 7
- **Significant Metabolites**: 6
- **Pathways Analyzed**: 2

## Cross-Validation Results

### High Consistency Pathways (Score > 0.7)

| Carbon metabolism | 0.867 | RNA:2 Pro:2 Met:0 |

### Conflicting Pathways (Directional Score < -0.3)

_No conflicting pathways found._

## Visualization Recommendations

Based on the cross-validation results, the following visualizations are recommended:

### 1. Circos Plot (跨组学关系全景)
- **Purpose**: Show relationships between RNA, Protein, and Metabolite
- **Data**: Use `mapped_ids.json` for link data
- **Tool**: matplotlib + circlize (R) or circos (Perl)

### 2. Pathway Heatmap (通路层面变化)
- **Purpose**: Display fold changes across omics for top pathways
- **Data**: Top 20 pathways by overall score
- **Tool**: seaborn.clustermap or ComplexHeatmap (R)

### 3. Sankey Diagram (数据流向)
- **Purpose**: Show flow from genes → proteins → metabolites
- **Data**: Significant features mapped to pathways
- **Tool**: plotly.graph_objects.Sankey

### 4. Correlation Network (相关性网络)
- **Purpose**: Cross-omics correlation network
- **Data**: Features with significant correlation
- **Tool**: networkx + matplotlib or Cytoscape

### 5. Bubble Plot (富集分析整合)
- **Purpose**: Compare enrichment results across omics
- **Data**: Pathway enrichment p-values
- **Tool**: ggplot2 (R) or plotly

## Recommendations

- **Focus on**: Carbon metabolism
- **Next Steps**: Perform targeted validation experiments on high-confidence pathways