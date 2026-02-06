#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Omics Integration Strategist
===================================
多组学（RNA/Pro/Met）整合分析与通路互证

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
    """组学数据结构"""
    data_type: str  # 'rna', 'pro', 'met'
    df: pd.DataFrame
    id_column: str
    fc_column: str
    pvalue_column: str
    
    @property
    def significant_features(self) -> pd.DataFrame:
        """获取显著差异的特征"""
        if 'padj' in self.df.columns:
            return self.df[self.df['padj'] < 0.05]
        return self.df[self.df[self.pvalue_column] < 0.05]


@dataclass
class PathwayScore:
    """通路互证评分结构"""
    pathway_id: str
    pathway_name: str
    database: str
    rna_genes: List[str]
    pro_genes: List[str]
    met_ids: List[str]
    directional_score: float  # 方向一致性评分
    correlation_score: float  # 相关性评分
    enrichment_score: float   # 富集一致性评分
    overall_score: float      # 综合评分
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ==================== ID Mapping Module ====================

class IDMapper:
    """跨组学ID映射器"""
    
    def __init__(self):
        self.rna_to_pro_map = {}
        self.pro_to_met_map = {}
        self.kegg_map = {}
    
    def load_mapping_databases(self, config_path: Optional[str] = None):
        """加载ID映射数据库"""
        # 内置简化映射表（实际使用时需接入真实数据库）
        self.rna_to_pro_map = self._build_rna_pro_mapping()
        self.pro_to_met_map = self._build_pro_met_mapping()
        
    def _build_rna_pro_mapping(self) -> Dict[str, str]:
        """构建RNA到Protein的映射（基于Gene Symbol）"""
        # 简化示例映射
        return {}
    
    def _build_pro_met_mapping(self) -> Dict[str, List[str]]:
        """构建Protein到Metabolite的映射（基于KEGG酶-代谢物关系）"""
        # 简化示例映射
        return {}
    
    def map_rna_to_protein(self, gene_symbols: List[str]) -> Dict[str, str]:
        """将Gene Symbol映射到Protein ID"""
        # 简化实现：假设Gene Symbol相同
        return {g: g for g in gene_symbols}
    
    def map_to_kegg(self, gene_symbols: List[str], organism: str = 'hsa') -> Dict[str, str]:
        """映射到KEGG ID"""
        # 简化实现
        return {g: f"{organism}:{g}" for g in gene_symbols}


# ==================== Pathway Analysis Module ====================

class PathwayAnalyzer:
    """通路分析器"""
    
    def __init__(self, databases: List[str] = ['KEGG']):
        self.databases = databases
        self.pathway_db = self._load_pathway_database()
    
    def _load_pathway_database(self) -> Dict[str, Dict]:
        """加载通路数据库"""
        # 简化的KEGG通路示例
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
        """通路富集分析（简化版超几何检验）"""
        results = []
        total_genes = 20000  # 假设背景基因数
        
        for pathway_id, pathway_info in self.pathway_db.items():
            pathway_genes = set(pathway_info['genes'])
            gene_set = set(gene_list)
            
            overlap = pathway_genes & gene_set
            if len(overlap) < 2:
                continue
            
            # 超几何检验
            k = len(overlap)  # 通路中差异基因数
            M = len(pathway_genes)  # 通路基因数
            n = len(gene_set)  # 差异基因总数
            N = total_genes  # 背景基因数
            
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
        # BH校正 (Benjamini-Hochberg)
        pvalues = df['pvalue'].values
        n = len(pvalues)
        if n > 0:
            sorted_indices = np.argsort(pvalues)
            sorted_pvalues = pvalues[sorted_indices]
            padj = np.zeros(n)
            padj[sorted_indices] = np.minimum.accumulate(sorted_pvalues * n / np.arange(1, n + 1))
            padj = np.minimum(padj, 1.0)  # 确保不超过1
            df['padj'] = padj
        else:
            df['padj'] = df['pvalue']
        df = df.sort_values('pvalue')
        
        return df


# ==================== Cross-Validation Module ====================

class CrossValidator:
    """跨组学互证验证器"""
    
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
        验证同一通路中各组学变化方向的一致性
        
        Returns:
            一致性评分 (-1 到 1，1表示完全一致)
        """
        pathway_info = self.pathway_analyzer.pathway_db.get(pathway_id, {})
        if not pathway_info:
            return 0.0
        
        pathway_genes = set(pathway_info.get('genes', []))
        pathway_mets = set(pathway_info.get('metabolites', []))
        
        # 获取各组学在该通路中的变化
        rna_changes = []
        pro_changes = []
        met_changes = []
        
        # RNA变化
        rna_sig = rna_data.significant_features
        for gene in pathway_genes:
            matches = rna_sig[rna_sig['gene_name'] == gene] if 'gene_name' in rna_sig.columns else pd.DataFrame()
            if len(matches) > 0:
                rna_changes.append(np.sign(matches[rna_data.fc_column].iloc[0]))
        
        # Protein变化
        pro_sig = pro_data.significant_features
        for gene in pathway_genes:
            matches = pro_sig[pro_sig['gene_name'] == gene] if 'gene_name' in pro_sig.columns else pd.DataFrame()
            if len(matches) > 0:
                pro_changes.append(np.sign(matches[pro_data.fc_column].iloc[0]))
        
        # Metabolite变化
        met_sig = met_data.significant_features
        for met in pathway_mets:
            matches = met_sig[met_sig['kegg_id'] == met] if 'kegg_id' in met_sig.columns else pd.DataFrame()
            if len(matches) == 0:
                # 尝试通过名称匹配
                matches = met_sig[met_sig['metabolite_id'] == met] if 'metabolite_id' in met_sig.columns else pd.DataFrame()
            if len(matches) > 0:
                # 代谢物变化方向与基因通常相反（底物消耗vs产物生成）
                met_changes.append(-np.sign(matches[met_data.fc_column].iloc[0]))
        
        # 计算一致性
        all_changes = rna_changes + pro_changes + met_changes
        if len(all_changes) < 2:
            return 0.0
        
        # 多数方向
        positive_ratio = sum(1 for c in all_changes if c > 0) / len(all_changes)
        consistency = 2 * abs(positive_ratio - 0.5)
        
        # 根据多数方向确定符号
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
        验证RNA和Protein表达的相关性
        
        Returns:
            (平均相关系数, 详细相关矩阵)
        """
        # 简化实现：基于Fold Change的相关性
        rna_sig = rna_data.significant_features
        pro_sig = pro_data.significant_features
        
        # 匹配基因
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
            merged[pro_data.fc_column + '_pro']
        )
        
        return correlation, merged
    
    def validate_enrichment_concordance(
        self,
        rna_enrichment: pd.DataFrame,
        pro_enrichment: pd.DataFrame,
        met_enrichment: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        验证各组学通路富集结果的一致性
        
        Returns:
            各通路的一致性评分字典
        """
        concordance = {}
        
        # 合并RNA和Protein的富集结果
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
                
                # 两者都显著则一致度高
                if p_rna < 0.05 and p_pro < 0.05:
                    concordance[pid] = 1.0
                elif (p_rna < 0.05) != (p_pro < 0.05):
                    concordance[pid] = 0.0  # 不一致
                else:
                    concordance[pid] = 0.5  # 都不显著，中性
        
        return concordance


# ==================== Report Generator ====================

class ReportGenerator:
    """分析报告生成器"""
    
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
        """生成整合分析报告"""
        
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
        
        # 高分通路
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
        
        # 冲突通路
        conflict = [p for p in pathway_scores if p.directional_score < -0.3]
        report_lines.append("### Conflicting Pathways (Directional Score < -0.3)")
        report_lines.append("")
        if conflict:
            for ps in sorted(conflict, key=lambda x: x.directional_score):
                report_lines.append(f"- **{ps.pathway_name}**: {ps.directional_score:.3f}")
        else:
            report_lines.append("_No conflicting pathways found._")
        report_lines.append("")
        
        # 可视化建议
        report_lines.extend([
            "## Visualization Recommendations",
            "",
            "Based on the cross-validation results, the following visualizations are recommended:",
            "",
            "### 1. Circos Plot (跨组学关系全景)",
            "- **Purpose**: Show relationships between RNA, Protein, and Metabolite",
            "- **Data**: Use `mapped_ids.json` for link data",
            "- **Tool**: matplotlib + circlize (R) or circos (Perl)",
            "",
            "### 2. Pathway Heatmap (通路层面变化)",
            "- **Purpose**: Display fold changes across omics for top pathways",
            "- **Data**: Top 20 pathways by overall score",
            "- **Tool**: seaborn.clustermap or ComplexHeatmap (R)",
            "",
            "### 3. Sankey Diagram (数据流向)",
            "- **Purpose**: Show flow from genes → proteins → metabolites",
            "- **Data**: Significant features mapped to pathways",
            "- **Tool**: plotly.graph_objects.Sankey",
            "",
            "### 4. Correlation Network (相关性网络)",
            "- **Purpose**: Cross-omics correlation network",
            "- **Data**: Features with significant correlation",
            "- **Tool**: networkx + matplotlib or Cytoscape",
            "",
            "### 5. Bubble Plot (富集分析整合)",
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
        
        # 保存报告
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
        """保存分析结果文件"""
        
        # 保存通路评分
        scores_df = pd.DataFrame([p.to_dict() for p in pathway_scores])
        scores_path = self.output_dir / "pathway_scores.csv"
        scores_df.to_csv(scores_path, index=False)
        
        # 保存ID映射
        mapped_path = self.output_dir / "mapped_ids.json"
        with open(mapped_path, 'w') as f:
            json.dump(mapped_ids, f, indent=2)
        
        # 保存一致性矩阵
        matrix_path = self.output_dir / "consistency_matrix.csv"
        consistency_matrix.to_csv(matrix_path)
        
        return {
            'pathway_scores': str(scores_path),
            'mapped_ids': str(mapped_path),
            'consistency_matrix': str(matrix_path)
        }


# ==================== Main Analysis Pipeline ====================

class MultiOmicsIntegrator:
    """多组学整合分析主类"""
    
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
        """加载多组学数据"""
        
        # 加载RNA数据
        rna_df = pd.read_csv(rna_path)
        rna_data = OmicsData(
            data_type='rna',
            df=rna_df,
            id_column='gene_id',
            fc_column='log2fc',
            pvalue_column='pvalue'
        )
        
        # 加载Protein数据
        pro_df = pd.read_csv(pro_path)
        pro_data = OmicsData(
            data_type='pro',
            df=pro_df,
            id_column='protein_id',
            fc_column='log2fc',
            pvalue_column='pvalue'
        )
        
        # 加载Metabolite数据
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
        """执行整合分析"""
        
        print("=" * 60)
        print("Multi-Omics Integration Analysis")
        print("=" * 60)
        
        # Step 1: ID映射
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
        
        # Step 2: 通路富集分析
        print("\n[Step 2] Pathway Enrichment Analysis...")
        rna_sig_genes = rna_data.significant_features['gene_name'].tolist() if 'gene_name' in rna_data.significant_features.columns else []
        pro_sig_genes = pro_data.significant_features['gene_name'].tolist() if 'gene_name' in pro_data.significant_features.columns else []
        
        rna_enrich = self.pathway_analyzer.enrich_pathways(rna_sig_genes)
        pro_enrich = self.pathway_analyzer.enrich_pathways(pro_sig_genes)
        
        print(f"  - RNA enriched pathways: {len(rna_enrich)}")
        print(f"  - Protein enriched pathways: {len(pro_enrich)}")
        
        # Step 3: 跨组学互证
        print("\n[Step 3] Cross-Validation...")
        
        # 富集一致性
        enrichment_concordance = self.cross_validator.validate_enrichment_concordance(
            rna_enrich, pro_enrich
        )
        
        # 各通路评分
        pathway_scores = []
        all_pathways = set(rna_enrich['pathway_id'].tolist() if len(rna_enrich) > 0 else []) | \
                      set(pro_enrich['pathway_id'].tolist() if len(pro_enrich) > 0 else [])
        
        for pathway_id in all_pathways:
            pathway_info = self.pathway_analyzer.pathway_db.get(pathway_id, {})
            if not pathway_info:
                continue
            
            # 方向一致性
            dir_score = self.cross_validator.validate_directional_consistency(
                rna_data, pro_data, met_data, pathway_id
            )
            
            # 相关性评分（简化：基于富集一致性）
            corr_score = enrichment_concordance.get(pathway_id, 0.5)
            
            # 富集评分
            enrich_score = 1.0 if pathway_id in enrichment_concordance and enrichment_concordance[pathway_id] > 0.5 else 0.0
            
            # 综合评分
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
        
        # 构建一致性矩阵
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
        """构建跨组学一致性矩阵"""
        
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
    """创建示例数据用于测试"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # RNA数据
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
    
    # Protein数据
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
    
    # Metabolite数据
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
        description='Multi-Omics Integration Strategist - 多组学整合分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 基本用法
  python main.py --rna rna_data.csv --pro pro_data.csv --met met_data.csv --output ./results
  
  # 创建示例数据
  python main.py --create-sample --output ./sample_data
  
  # 指定数据库
  python main.py --rna rna.csv --pro pro.csv --met met.csv --databases KEGG,Reactome --output ./results
        """
    )
    
    parser.add_argument('--rna', type=str, help='转录组数据文件路径 (CSV)')
    parser.add_argument('--pro', type=str, help='蛋白质组数据文件路径 (CSV)')
    parser.add_argument('--met', type=str, help='代谢组数据文件路径 (CSV)')
    parser.add_argument('--output', '-o', type=str, default='./results', 
                       help='输出目录 (默认: ./results)')
    parser.add_argument('--databases', type=str, default='KEGG',
                       help='通路数据库，逗号分隔 (默认: KEGG)')
    parser.add_argument('--create-sample', action='store_true',
                       help='创建示例数据用于测试')
    parser.add_argument('--format', type=str, default='md,csv,json',
                       help='输出格式，逗号分隔 (默认: md,csv,json)')
    
    args = parser.parse_args()
    
    # 创建示例数据
    if args.create_sample:
        create_sample_data(args.output)
        return
    
    # 验证必需参数
    if not all([args.rna, args.pro, args.met]):
        parser.print_help()
        print("\nError: --rna, --pro, and --met are required for analysis.")
        sys.exit(1)
    
    # 检查文件存在
    for f in [args.rna, args.pro, args.met]:
        if not Path(f).exists():
            print(f"Error: File not found: {f}")
            sys.exit(1)
    
    # 配置
    config = {
        'databases': args.databases.split(','),
        'output_formats': args.format.split(',')
    }
    
    # 运行分析
    try:
        integrator = MultiOmicsIntegrator(config)
        
        # 加载数据
        print("Loading data...")
        rna_data, pro_data, met_data = integrator.load_data(
            args.rna, args.pro, args.met
        )
        
        # 执行整合分析
        pathway_scores, mapped_ids, consistency_matrix = integrator.run_integration(
            rna_data, pro_data, met_data
        )
        
        # 生成报告
        print("\n[Step 4] Generating Reports...")
        report_gen = ReportGenerator(args.output)
        
        # 保存结果文件
        result_files = report_gen.save_results(
            pathway_scores, mapped_ids, consistency_matrix
        )
        
        # 生成Markdown报告
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
