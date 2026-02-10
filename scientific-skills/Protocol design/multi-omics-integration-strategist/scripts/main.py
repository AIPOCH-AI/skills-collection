#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Omics Integration Strategist
===================================
Multi-omics (RNA/Pro/Met) integration analysis and pathway cross-validation

Author: OpenClaw Bioinformatics Team
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import networkx as nx


# ==================== Data Structures ====================

@dataclass
class OmicsData:
    """Omics data structure"""
    data_type: str  # 'rna', 'pro', 'met'
    df: pd.DataFrame
    id_column: str
    fc_column: str
    pvalue_column: str
    
    @property
    def significant_features(self) -> pd.DataFrame:
        """Get significantly differential features"""
        if 'padj' in self.df.columns:
            return self.df[self.df['padj'] < 0.05]
        return self.df[self.df[self.pvalue_column] < 0.05]


@dataclass
class PathwayScore:
    """Pathway cross-validation scoring structure"""
    pathway_id: str
    pathway_name: str
    database: str
    rna_genes: List[str]
    pro_genes: List[str]
    met_ids: List[str]
    directional_score: float  # Directional consistency score
    correlation_score: float  # Correlation score
    enrichment_score: float   # Enrichment consistency score
    overall_score: float      # Overall composite score
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ==================== ID Mapping Module ====================

class IDMapper:
    """Cross-omics ID mapper"""
    
    def __init__(self):
        self.rna_to_pro_map = {}
        self.pro_to_met_map = {}
        self.kegg_map = {}
    
    def load_mapping_databases(self, config_path: Optional[str] = None):
        """Load ID mapping databases"""
        # Built-in simplified mapping table (actual use requires connection to real databases)
        self.rna_to_pro_map = self._build_rna_pro_mapping()
        self.pro_to_met_map = self._build_pro_met_mapping()
        
    def _build_rna_pro_mapping(self) -> Dict[str, str]:
        """Build RNA to Protein mapping (based on Gene Symbol)"""
        # Simplified example mapping
        return {}
    
    def _build_pro_met_mapping(self) -> Dict[str, List[str]]:
        """Build Protein to Metabolite mapping (based on KEGG enzyme-metabolite relationships)"""
        # Simplified example mapping
        return {}
    
    def map_rna_to_protein(self, gene_symbols: List[str]) -> Dict[str, str]:
        """Map Gene Symbol to Protein ID"""
        # Simplified implementation: assume Gene Symbol is the same
        return {g: g for g in gene_symbols}
    
    def map_to_kegg(self, gene_symbols: List[str], organism: str = 'hsa') -> Dict[str, str]:
        """Map to KEGG ID"""
        # Simplified implementation
        return {g: f"{organism}:{g}" for g in gene_symbols}


# ==================== Pathway Analysis Module ====================

class PathwayAnalyzer:
    """Pathway analyzer"""
    
    def __init__(self, databases: List[str] = ['KEGG']):
        self.databases = databases
        self.pathway_db = self._load_pathway_database()
    
    def _load_pathway_database(self) -> Dict[str, Dict]:
        """Load pathway database"""
        # Simplified KEGG pathway examples
        pathways = {
            'hsa00010': {
                'name': 'Glycolysis / Gluconeogenesis',
                'genes': ['HK1', 'HK2', 'GPI', 'PFKM', 'PFKL', 'ALDOA', 'GAPDH', 
                         'PGK1', 'PGAM1', 'ENO1', 'PKM', 'LDHA'],
                'metabolites': ['C00267', 'C00668', 'C05378', 'C00111', 'C00118', 
                               'C00236', 'C01159', 'C00631', 'C00074']
            },
            'hsa00020': {
                'name': 'Citrate cycle (TCA cycle)',
                'genes': ['CS', 'ACO2', 'IDH1', 'IDH2', 'IDH3A', 'IDH3B', 'IDH3G',
                         'OGDH', 'SUCLG1', 'SUCLG2', 'SUCLA2', 'SDHA', 'SDHB',
                         'SDHC', 'SDHD', 'FH', 'MDH1', 'MDH2'],
                'metabolites': ['C00024', 'C00311', 'C00417', 'C00026', 'C05379',
                               'C00042', 'C00149', 'C00036', 'C00022']
            },
            'hsa00620': {
                'name': 'Pyruvate metabolism',
                'genes': ['PDHA1', 'PDHA2', 'PDHB', 'PC', 'LDHA', 'LDHB', 'ME1', 'ME2'],
                'metabolites': ['C00022', 'C00024', 'C00074', 'C00033']
            },
            'hsa01200': {
                'name': 'Carbon metabolism',
                'genes': ['HK1', 'HK2', 'GPI', 'PFKM', 'ALDOA', 'GAPDH', 'CS', 'ACO2',
                         'IDH1', 'IDH2', 'OGDH', 'SDHA', 'FH', 'MDH1'],
                'metabolites': ['C00267', 'C00074', 'C00024', 'C00036']
            }
        }
        return pathways
    
    def enrich_pathways(self, gene_list: List[str], threshold: float = 0.05) -> pd.DataFrame:
        """Pathway enrichment analysis (simplified hypergeometric test)"""
        results = []
        total_genes = 20000  # Assumed background gene count
        
        for pathway_id, pathway_info in self.pathway_db.items():
            pathway_genes = set(pathway_info['genes'])
            gene_set = set(gene_list)
            
            overlap = pathway_genes & gene_set
            if len(overlap) < 2:
                continue
            
            # Hypergeometric test
            k = len(overlap)  # Number of differential genes in pathway
            M = len(pathway_genes)  # Number of genes in pathway
            n = len(gene_set)  # Total number of differential genes
            N = total_genes  # Background gene count
            
            pvalue = stats.hypergeom.sf(k-1, N, M, n)
            
            results.append({
                'pathway_id': pathway_id,
                'pathway_name': pathway_info['name'],
                'overlap_genes': list(overlap),
                'overlap_count': len(overlap),
                'pathway_genes': M,
                'pvalue': pvalue,
                'gene_ratio': len(overlap) / len(pathway_genes)
            })
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        # BH correction (Benjamini-Hochberg)
        pvalues = df['pvalue'].values
        n = len(pvalues)
        if n > 0:
            sorted_indices = np.argsort(pvalues)
            sorted_pvalues = pvalues[sorted_indices]
            padj = np.zeros(n)
            padj[sorted_indices] = np.minimum.accumulate(sorted_pvalues * n / np.arange(1, n + 1))
            padj = np.minimum(padj, 1.0)  # Ensure value does not exceed 1
            df['padj'] = padj
        else:
            df['padj'] = df['pvalue']
        df = df.sort_values('pvalue')
        
        return df


# ==================== Cross-Validation Module ====================

class CrossValidator:
    """Cross-omics cross-validation validator"""
    
    def __init__(self, id_mapper: IDMapper, pathway_analyzer: PathwayAnalyzer):
        self.id_mapper = id_mapper
        self.pathway_analyzer = pathway_analyzer
    
    def validate_directional_consistency(
        self,
        rna_data: OmicsData,
        pro_data: OmicsData,
        met_data: OmicsData,
        pathway_id: str
    ) -> float:
        """
        Validate directional consistency of changes across omics in the same pathway
        
        Returns:
            Consistency score (-1 to 1, 1 means completely consistent)
        """
        pathway_info = self.pathway_analyzer.pathway_db.get(pathway_id, {})
        if not pathway_info:
            return 0.0
        
        pathway_genes = set(pathway_info.get('genes', []))
        pathway_mets = set(pathway_info.get('metabolites', []))
        
        # Get changes for each omics in this pathway
        rna_changes = []
        pro_changes = []
        met_changes = []
        
        # RNA changes
        rna_sig = rna_data.significant_features
        for gene in pathway_genes:
            matches = rna_sig[rna_sig['gene_name'] == gene] if 'gene_name' in rna_sig.columns else pd.DataFrame()
            if len(matches) > 0:
                rna_changes.append(np.sign(matches[rna_data.fc_column].iloc[0]))
        
        # Protein changes
        pro_sig = pro_data.significant_features
        for gene in pathway_genes:
            matches = pro_sig[pro_sig['gene_name'] == gene] if 'gene_name' in pro_sig.columns else pd.DataFrame()
            if len(matches) > 0:
                pro_changes.append(np.sign(matches[pro_data.fc_column].iloc[0]))
        
        # Metabolite changes
        met_sig = met_data.significant_features
        for met in pathway_mets:
            matches = met_sig[met_sig['kegg_id'] == met] if 'kegg_id' in met_sig.columns else pd.DataFrame()
            if len(matches) == 0:
                # Try matching by name
                matches = met_sig[met_sig['metabolite_id'] == met] if 'metabolite_id' in met_sig.columns else pd.DataFrame()
            if len(matches) > 0:
                # Metabolite change direction is usually opposite to genes (substrate consumption vs product generation)
                met_changes.append(-np.sign(matches[met_data.fc_column].iloc[0]))
        
        # Calculate consistency
        all_changes = rna_changes + pro_changes + met_changes
        if len(all_changes) < 2:
            return 0.0
        
        # Majority direction
        positive_ratio = sum(1 for c in all_changes if c > 0) / len(all_changes)
        consistency = 2 * abs(positive_ratio - 0.5)
        
        # Determine sign based on majority direction
        if positive_ratio < 0.5:
            consistency = -consistency
            
        return consistency
    
    def validate_correlation(
        self,
        rna_data: OmicsData,
        pro_data: OmicsData,
        matched_samples: Optional[List[str]] = None
    ) -> Tuple[float, pd.DataFrame]:
        """
        Validate correlation between RNA and Protein expression
        
        Returns:
            (Average correlation coefficient, detailed correlation matrix)
        """
        # Simplified implementation: correlation based on Fold Change
        rna_sig = rna_data.significant_features
        pro_sig = pro_data.significant_features
        
        # Match genes
        if 'gene_name' not in rna_sig.columns or 'gene_name' not in pro_sig.columns:
            return 0.0, pd.DataFrame()
        
        merged = pd.merge(
            rna_sig[['gene_name', rna_data.fc_column]],
            pro_sig[['gene_name', pro_data.fc_column]],
            on='gene_name',
            suffixes=('_rna', '_pro')
        )
        
        if len(merged) < 3:
            return 0.0, merged
        
        correlation, pvalue = stats.spearmanr(
            merged[rna_data.fc_column + '_rna'],
            merged[rna_data.fc_column + '_pro']
        )
        
        return correlation, merged
    
    def validate_enrichment_concordance(
        self,
        rna_enrichment: pd.DataFrame,
        pro_enrichment: pd.DataFrame,
        met_enrichment: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        Validate consistency of pathway enrichment results across omics
        
        Returns:
            Dictionary of consistency scores for each pathway
        """
        concordance = {}
        
        # Merge RNA and Protein enrichment results
        if len(rna_enrichment) > 0 and len(pro_enrichment) > 0:
            merged = pd.merge(
                rna_enrichment[['pathway_id', 'pvalue']].rename(columns={'pvalue': 'pvalue_rna'}),
                pro_enrichment[['pathway_id', 'pvalue']].rename(columns={'pvalue': 'pvalue_pro'}),
                on='pathway_id',
                how='outer'
            )
            
            for _, row in merged.iterrows():
                pid = row['pathway_id']
                p_rna = row.get('pvalue_rna', 1.0)
                p_pro = row.get('pvalue_pro', 1.0)
                
                # High consistency if both are significant
                if p_rna < 0.05 and p_pro < 0.05:
                    concordance[pid] = 1.0
                elif (p_rna < 0.05) != (p_pro < 0.05):
                    concordance[pid] = 0.0  # Inconsistent
                else:
                    concordance[pid] = 0.5  # Neither significant, neutral
        
        return concordance


# ==================== Report Generator ====================

class ReportGenerator:
    """Analysis report generator"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        pathway_scores: List[PathwayScore],
        rna_data: OmicsData,
        pro_data: OmicsData,
        met_data: OmicsData,
        consistency_matrix: pd.DataFrame
    ) -> str:
        """Generate integration analysis report"""
        
        report_lines = [
            "# Multi-Omics Integration Analysis Report",
            "",
            "## Executive Summary",
            f"- **Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
            f"- **RNA Samples**: {len(rna_data.df.columns) - 4} features × samples",
            f"- **Protein Samples**: {len(pro_data.df.columns) - 4} features × samples",
            f"- **Metabolite Samples**: {len(met_data.df.columns) - 4} features × samples",
            f"- **Significant RNA**: {len(rna_data.significant_features)}",
            f"- **Significant Proteins**: {len(pro_data.significant_features)}",
            f"- **Significant Metabolites**: {len(met_data.significant_features)}",
            f"- **Pathways Analyzed**: {len(pathway_scores)}",
            "",
            "## Cross-Validation Results",
            "",
        ]
        
        # High scoring pathways
        high_score = [p for p in pathway_scores if p.overall_score > 0.7]
        report_lines.append("### High Consistency Pathways (Score > 0.7)")
        report_lines.append("")
        if high_score:
            for ps in sorted(high_score, key=lambda x: x.overall_score, reverse=True)[:10]:
                report_lines.append(
                    f"| {ps.pathway_name} | {ps.overall_score:.3f} | "
                    f"RNA:{len(ps.rna_genes)} Pro:{len(ps.pro_genes)} Met:{len(ps.met_ids)} |"
                )
        else:
            report_lines.append("_No pathways with high consistency found._")
        report_lines.append("")
        
        # Conflicting pathways
        conflict = [p for p in pathway_scores if p.directional_score < -0.3]
        report_lines.append("### Conflicting Pathways (Directional Score < -0.3)")
        report_lines.append("")
        if conflict:
            for ps in sorted(conflict, key=lambda x: x.directional_score):
                report_lines.append(f"- **{ps.pathway_name}**: {ps.directional_score:.3f}")
        else:
            report_lines.append("_No conflicting pathways found._")
        report_lines.append("")
        
        # Visualization recommendations
        report_lines.extend([
            "## Visualization Recommendations",
            "",
            "Based on the cross-validation results, the following visualizations are recommended:",
            "",
            "### 1. Circos Plot (Cross-omics Relationship Overview)",
            "- **Purpose**: Show relationships between RNA, Protein, and Metabolite",
            "- **Data**: Use `mapped_ids.json` for link data",
            "- **Tool**: matplotlib + circlize (R) or circos (Perl)",
            "",
            "### 2. Pathway Heatmap (Pathway-level Changes)",
            "- **Purpose**: Display fold changes across omics for top pathways",
            "- **Data**: Top 20 pathways by overall score",
            "- **Tool**: seaborn.clustermap or ComplexHeatmap (R)",
            "",
            "### 3. Sankey Diagram (Data Flow)",
            "- **Purpose**: Show flow from genes → proteins → metabolites",
            "- **Data**: Significant features mapped to pathways",
            "- **Tool**: plotly.graph_objects.Sankey",
            "",
            "### 4. Correlation Network (Correlation Network)",
            "- **Purpose**: Cross-omics correlation network",
            "- **Data**: Features with significant correlation",
            "- **Tool**: networkx + matplotlib or Cytoscape",
            "",
            "### 5. Bubble Plot (Enrichment Analysis Integration)",
            "- **Purpose**: Compare enrichment results across omics",
            "- **Data**: Pathway enrichment p-values",
            "- **Tool**: ggplot2 (R) or plotly",
            "",
            "## Recommendations",
            "",
        ])
        
        if high_score:
            top_pathways = ", ".join([p.pathway_name for p in high_score[:3]])
            report_lines.append(f"- **Focus on**: {top_pathways}")
        
        if conflict:
            conflict_paths = ", ".join([p.pathway_name for p in conflict[:3]])
            report_lines.append(f"- **Requires Validation**: {conflict_paths} (data quality check recommended)")
        
        report_lines.append("- **Next Steps**: Perform targeted validation experiments on high-confidence pathways")
        
        report_text = "\n".join(report_lines)
        
        # Save report
        report_path = self.output_dir / "integration_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return str(report_path)
    
    def save_results(
        self,
        pathway_scores: List[PathwayScore],
        mapped_ids: Dict,
        consistency_matrix: pd.DataFrame
    ) -> Dict[str, str]:
        """Save analysis result files"""
        
        # Save pathway scores
        scores_df = pd.DataFrame([p.to_dict() for p in pathway_scores])
        scores_path = self.output_dir / "pathway_scores.csv"
        scores_df.to_csv(scores_path, index=False)
        
        # Save ID mappings
        mapped_path = self.output_dir / "mapped_ids.json"
        with open(mapped_path, 'w') as f:
            json.dump(mapped_ids, f, indent=2)
        
        # Save consistency matrix
        matrix_path = self.output_dir / "consistency_matrix.csv"
        consistency_matrix.to_csv(matrix_path)
        
        return {
            'pathway_scores': str(scores_path),
            'mapped_ids': str(mapped_path),
            'consistency_matrix': str(matrix_path)
        }


# ==================== Main Analysis Pipeline ====================

class MultiOmicsIntegrator:
    """Main class for multi-omics integration analysis"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.id_mapper = IDMapper()
        self.pathway_analyzer = PathwayAnalyzer(
            databases=self.config.get('databases', ['KEGG'])
        )
        self.cross_validator = CrossValidator(self.id_mapper, self.pathway_analyzer)
        self.id_mapper.load_mapping_databases()
    
    def load_data(
        self,
        rna_path: str,
        pro_path: str,
        met_path: str
    ) -> Tuple[OmicsData, OmicsData, OmicsData]:
        """Load multi-omics data"""
        
        # Load RNA data
        rna_df = pd.read_csv(rna_path)
        rna_data = OmicsData(
            data_type='rna',
            df=rna_df,
            id_column='gene_id',
            fc_column='log2fc',
            pvalue_column='pvalue'
        )
        
        # Load Protein data
        pro_df = pd.read_csv(pro_path)
        pro_data = OmicsData(
            data_type='pro',
            df=pro_df,
            id_column='protein_id',
            fc_column='log2fc',
            pvalue_column='pvalue'
        )
        
        # Load Metabolite data
        met_df = pd.read_csv(met_path)
        met_data = OmicsData(
            data_type='met',
            df=met_df,
            id_column='metabolite_id',
            fc_column='log2fc',
            pvalue_column='pvalue'
        )
        
        return rna_data, pro_data, met_data
    
    def run_integration(
        self,
        rna_data: OmicsData,
        pro_data: OmicsData,
        met_data: OmicsData
    ) -> Tuple[List[PathwayScore], Dict, pd.DataFrame]:
        """Execute integration analysis"""
        
        print("=" * 60)
        print("Multi-Omics Integration Analysis")
        print("=" * 60)
        
        # Step 1: ID mapping
        print("\n[Step 1] ID Mapping...")
        rna_genes = rna_data.df['gene_name'].tolist() if 'gene_name' in rna_data.df.columns else []
        pro_genes = pro_data.df['gene_name'].tolist() if 'gene_name' in pro_data.df.columns else []
        
        mapped_ids = {
            'rna_to_pro': self.id_mapper.map_rna_to_protein(rna_genes),
            'rna_kegg': self.id_mapper.map_to_kegg(rna_genes),
            'pro_kegg': self.id_mapper.map_to_kegg(pro_genes)
        }
        print(f"  - RNA genes: {len(rna_genes)}")
        print(f"  - Protein genes: {len(pro_genes)}")
        
        # Step 2: Pathway enrichment analysis
        print("\n[Step 2] Pathway Enrichment Analysis...")
        rna_sig_genes = rna_data.significant_features['gene_name'].tolist() if 'gene_name' in rna_data.significant_features.columns else []
        pro_sig_genes = pro_data.significant_features['gene_name'].tolist() if 'gene_name' in pro_data.significant_features.columns else []
        
        rna_enrich = self.pathway_analyzer.enrich_pathways(rna_sig_genes)
        pro_enrich = self.pathway_analyzer.enrich_pathways(pro_sig_genes)
        
        print(f"  - RNA enriched pathways: {len(rna_enrich)}")
        print(f"  - Protein enriched pathways: {len(pro_enrich)}")
        
        # Step 3: Cross-omics cross-validation
        print("\n[Step 3] Cross-Validation...")
        
        # Enrichment consistency
        enrichment_concordance = self.cross_validator.validate_enrichment_concordance(
            rna_enrich, pro_enrich
        )
        
        # Score each pathway
        pathway_scores = []
        all_pathways = set(rna_enrich['pathway_id'].tolist() if len(rna_enrich) > 0 else []) | \
                      set(pro_enrich['pathway_id'].tolist() if len(pro_enrich) > 0 else [])
        
        for pathway_id in all_pathways:
            pathway_info = self.pathway_analyzer.pathway_db.get(pathway_id, {})
            if not pathway_info:
                continue
            
            # Directional consistency
            dir_score = self.cross_validator.validate_directional_consistency(
                rna_data, pro_data, met_data, pathway_id
            )
            
            # Correlation score (simplified: based on enrichment consistency)
            corr_score = enrichment_concordance.get(pathway_id, 0.5)
            
            # Enrichment score
            enrich_score = 1.0 if pathway_id in enrichment_concordance and enrichment_concordance[pathway_id] > 0.5 else 0.0
            
            # Overall composite score
            overall = (abs(dir_score) + corr_score + enrich_score) / 3
            if dir_score < 0:
                overall = -overall
            
            pathway_scores.append(PathwayScore(
                pathway_id=pathway_id,
                pathway_name=pathway_info.get('name', pathway_id),
                database='KEGG',
                rna_genes=[g for g in rna_sig_genes if g in pathway_info.get('genes', [])],
                pro_genes=[g for g in pro_sig_genes if g in pathway_info.get('genes', [])],
                met_ids=[],
                directional_score=dir_score,
                correlation_score=corr_score,
                enrichment_score=enrich_score,
                overall_score=overall
            ))
        
        print(f"  - Pathways scored: {len(pathway_scores)}")
        
        # Build consistency matrix
        consistency_matrix = self._build_consistency_matrix(
            pathway_scores, rna_enrich, pro_enrich
        )
        
        return pathway_scores, mapped_ids, consistency_matrix
    
    def _build_consistency_matrix(
        self,
        pathway_scores: List[PathwayScore],
        rna_enrich: pd.DataFrame,
        pro_enrich: pd.DataFrame
    ) -> pd.DataFrame:
        """Build cross-omics consistency matrix"""
        
        data = {
            'pathway_id': [p.pathway_id for p in pathway_scores],
            'pathway_name': [p.pathway_name for p in pathway_scores],
            'directional_score': [p.directional_score for p in pathway_scores],
            'correlation_score': [p.correlation_score for p in pathway_scores],
            'enrichment_score': [p.enrichment_score for p in pathway_scores],
            'overall_score': [p.overall_score for p in pathway_scores],
        }
        
        return pd.DataFrame(data)


def create_sample_data(output_dir: str):
    """Create sample data for testing"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # RNA data
    rna_data = pd.DataFrame({
        'gene_id': ['ENSG00000139618', 'ENSG00000141510', 'ENSG00000171862', 'ENSG00000111640', 
                   'ENSG00000111641', 'ENSG00000149925', 'ENSG00000167996'],
        'gene_name': ['BRCA1', 'TP53', 'HK1', 'GAPDH', 'GAPDHS', 'PKM', 'LDHA'],
        'log2fc': [1.23, 0.85, 2.1, 1.5, 0.9, 1.8, -1.2],
        'pvalue': [0.001, 0.002, 0.0001, 0.0005, 0.01, 0.0002, 0.003],
        'padj': [0.005, 0.008, 0.0005, 0.002, 0.03, 0.001, 0.01],
        'control': [12.5, 10.2, 8.5, 15.3, 9.1, 11.2, 14.5],
        'treatment': [13.8, 11.1, 12.1, 18.2, 11.5, 15.8, 12.8]
    })
    rna_data.to_csv(output_path / 'rna_data.csv', index=False)
    
    # Protein data
    pro_data = pd.DataFrame({
        'protein_id': ['P38398', 'P04637', 'P19367', 'P04406', 'P61812', 'P14618', 'P00338'],
        'gene_name': ['BRCA1', 'TP53', 'HK1', 'GAPDH', 'GAPDHS', 'PKM', 'LDHA'],
        'log2fc': [0.85, 0.65, 1.45, 1.2, 0.75, 1.35, -0.95],
        'pvalue': [0.002, 0.005, 0.001, 0.001, 0.02, 0.003, 0.008],
        'padj': [0.008, 0.015, 0.005, 0.004, 0.04, 0.01, 0.02],
        'control': [2450, 1890, 3200, 5600, 2100, 4300, 3800],
        'treatment': [3890, 2670, 5200, 8900, 3100, 7200, 2100]
    })
    pro_data.to_csv(output_path / 'pro_data.csv', index=False)
    
    # Metabolite data
    met_data = pd.DataFrame({
        'metabolite_id': ['C00267', 'C00668', 'C05378', 'C00236', 'C01159', 'C00631', 'C00074'],
        'metabolite_name': ['D-Glucose', 'alpha-D-Glucose', 'beta-D-Fructose', 'Glyceraldehyde 3-phosphate',
                           '3-Phospho-D-glycerate', 'Pyruvate', 'Phosphoenolpyruvate'],
        'kegg_id': ['C00267', 'C00668', 'C05378', 'C00236', 'C01159', 'C00631', 'C00074'],
        'log2fc': [1.2, 1.15, 0.95, 0.85, 0.75, -0.65, 0.55],
        'pvalue': [0.003, 0.004, 0.008, 0.01, 0.015, 0.02, 0.025],
        'padj': [0.012, 0.015, 0.025, 0.03, 0.04, 0.045, 0.05],
        'control': [45.2, 42.1, 38.5, 12.3, 8.5, 35.2, 15.8],
        'treatment': [78.5, 72.3, 65.1, 18.9, 12.8, 22.5, 24.2]
    })
    met_data.to_csv(output_path / 'met_data.csv', index=False)
    
    print(f"Sample data created in: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Multi-Omics Integration Strategist - Multi-omics Integration Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python main.py --rna rna_data.csv --pro pro_data.csv --met met_data.csv --output ./results
  
  # Create sample data
  python main.py --create-sample --output ./sample_data
  
  # Specify database
  python main.py --rna rna.csv --pro pro.csv --met met.csv --databases KEGG,Reactome --output ./results
        """
    )
    
    parser.add_argument('--rna', type=str, help='Transcriptomics data file path (CSV)')
    parser.add_argument('--pro', type=str, help='Proteomics data file path (CSV)')
    parser.add_argument('--met', type=str, help='Metabolomics data file path (CSV)')
    parser.add_argument('--output', '-o', type=str, default='./results', 
                       help='Output directory (default: ./results)')
    parser.add_argument('--databases', type=str, default='KEGG',
                       help='Pathway databases, comma-separated (default: KEGG)')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create sample data for testing')
    parser.add_argument('--format', type=str, default='md,csv,json',
                       help='Output formats, comma-separated (default: md,csv,json)')
    
    args = parser.parse_args()
    
    # Create sample data
    if args.create_sample:
        create_sample_data(args.output)
        return
    
    # Validate required arguments
    if not all([args.rna, args.pro, args.met]):
        parser.print_help()
        print("\nError: --rna, --pro, and --met are required for analysis.")
        sys.exit(1)
    
    # Check file existence
    for f in [args.rna, args.pro, args.met]:
        if not Path(f).exists():
            print(f"Error: File not found: {f}")
            sys.exit(1)
    
    # Configuration
    config = {
        'databases': args.databases.split(','),
        'output_formats': args.format.split(',')
    }
    
    # Run analysis
    try:
        integrator = MultiOmicsIntegrator(config)
        
        # Load data
        print("Loading data...")
        rna_data, pro_data, met_data = integrator.load_data(
            args.rna, args.pro, args.met
        )
        
        # Execute integration analysis
        pathway_scores, mapped_ids, consistency_matrix = integrator.run_integration(
            rna_data, pro_data, met_data
        )
        
        # Generate report
        print("\n[Step 4] Generating Reports...")
        report_gen = ReportGenerator(args.output)
        
        # Save result files
        result_files = report_gen.save_results(
            pathway_scores, mapped_ids, consistency_matrix
        )
        
        # Generate Markdown report
        report_path = report_gen.generate_report(
            pathway_scores, rna_data, pro_data, met_data, consistency_matrix
        )
        
        print(f"\n{'='*60}")
        print("Analysis Complete!")
        print(f"{'='*60}")
        print(f"Report: {report_path}")
        print(f"Pathway Scores: {result_files['pathway_scores']}")
        print(f"Mapped IDs: {result_files['mapped_ids']}")
        print(f"Consistency Matrix: {result_files['consistency_matrix']}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
