#!/usr/bin/env python3
"""
In Silico Perturbation Oracle - Main Script
虚拟基因敲除预测主入口

功能: 利用生物基础大模型进行in silico基因敲除预测
作者: OpenClaw Bioinformatics Team
版本: 1.0.0
"""

import os
import sys
import json
import argparse
import logging
import warnings
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
import pandas as pd
from collections import defaultdict

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PerturbationOracle")


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class PerturbationConfig:
    """扰动预测配置"""
    model_name: str = "geneformer"
    cell_type: str = "fibroblast"
    perturbation_type: str = "complete_ko"  # complete_ko, kd, crispr
    n_permutations: int = 100
    batch_size: int = 32
    pval_threshold: float = 0.05
    logfc_threshold: float = 1.0
    top_k: int = 50
    pathways: List[str] = None
    
    def __post_init__(self):
        if self.pathways is None:
            self.pathways = ["KEGG", "GO_BP"]


@dataclass
class DifferentialExpressionResult:
    """差异表达结果"""
    gene_symbol: str
    log2_fold_change: float
    p_value: float
    adjusted_p_value: float
    perturbation_gene: str
    cell_type: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PathwayResult:
    """通路富集结果"""
    pathway_name: str
    p_value: float
    enrichment_ratio: float
    overlap_genes: List[str]
    database: str


@dataclass
class TargetScore:
    """靶点评分结果"""
    target_gene: str
    efficacy_score: float
    safety_score: float
    druggability_score: float
    novelty_score: float
    overall_score: float
    recommendation: str


# ============================================================================
# Base Model Adapter
# ============================================================================

class BaseModelAdapter:
    """基础模型适配器抽象类"""
    
    def __init__(self, model_name: str, config: Dict):
        self.model_name = model_name
        self.config = config
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """加载预训练模型"""
        raise NotImplementedError
        
    def predict_perturbation(
        self, 
        genes: List[str], 
        cell_type: str,
        perturbation_type: str = "complete_ko"
    ) -> np.ndarray:
        """
        预测基因扰动后的表达谱
        
        Args:
            genes: 待敲除的基因列表
            cell_type: 细胞类型
            perturbation_type: 扰动类型
            
        Returns:
            预测表达谱矩阵
        """
        raise NotImplementedError
        
    def get_reference_expression(self, cell_type: str) -> np.ndarray:
        """获取参考表达谱"""
        raise NotImplementedError
        
    def is_gene_in_vocabulary(self, gene: str) -> bool:
        """检查基因是否在模型词汇表中"""
        raise NotImplementedError


class GeneformerAdapter(BaseModelAdapter):
    """Geneformer模型适配器"""
    
    def __init__(self, config: Dict):
        super().__init__("geneformer", config)
        self.embedding_dim = 256
        
    def load_model(self):
        """加载Geneformer模型"""
        logger.info("Loading Geneformer model...")
        try:
            # 实际使用时需要安装: pip install geneformer
            # from geneformer import TranscriptomeTokenizer, EmbExtractor
            # self.model = EmbExtractor(...)
            logger.info("Geneformer model loaded successfully (simulated)")
        except ImportError:
            logger.warning("Geneformer not installed, using mock implementation")
            self.model = MockModel(self.model_name)
            
    def predict_perturbation(
        self, 
        genes: List[str], 
        cell_type: str,
        perturbation_type: str = "complete_ko"
    ) -> np.ndarray:
        """模拟Geneformer扰动预测"""
        logger.info(f"Predicting {perturbation_type} for genes {genes} in {cell_type}")
        
        # 获取参考表达谱
        ref_expr = self.get_reference_expression(cell_type)
        
        # 模拟扰动效果 (实际实现中调用Geneformer API)
        perturbed_expr = self._simulate_perturbation(
            ref_expr, genes, perturbation_type
        )
        
        return perturbed_expr
        
    def _simulate_perturbation(
        self, 
        expression: np.ndarray, 
        genes: List[str],
        perturbation_type: str
    ) -> np.ndarray:
        """模拟扰动效果 (占位实现)"""
        # 在实际实现中，这里会调用Geneformer的in silico perturbation功能
        # 当前为演示目的使用随机扰动模拟
        np.random.seed(42)
        noise = np.random.normal(0, 0.5, expression.shape)
        
        # 根据扰动类型调整
        if perturbation_type == "complete_ko":
            # 完全敲除: 下调表达
            perturbed = expression * 0.1 + noise
        elif perturbation_type == "kd":
            # 敲低: 部分下调
            perturbed = expression * 0.5 + noise
        else:
            perturbed = expression + noise
            
        return np.maximum(perturbed, 0)  # 确保非负
        
    def get_reference_expression(self, cell_type: str) -> np.ndarray:
        """获取参考表达谱 (模拟)"""
        # 模拟基因表达谱 (约20,000个基因)
        np.random.seed(hash(cell_type) % 2**32)
        n_genes = 20000
        
        # 使用对数正态分布模拟基因表达
        expression = np.random.lognormal(0, 1, n_genes)
        
        # 根据细胞类型调整特征表达
        cell_type_markers = self._get_cell_type_markers(cell_type)
        for marker in cell_type_markers:
            marker_idx = hash(marker) % n_genes
            expression[marker_idx] *= 10  # 高表达标记基因
            
        return expression
        
    def _get_cell_type_markers(self, cell_type: str) -> List[str]:
        """获取细胞类型标记基因"""
        markers = {
            "hepatocyte": ["ALB", "AFP", "CYP3A4", "HNF4A"],
            "cardiomyocyte": ["MYH6", "MYH7", "TNNT2", "ACTC1"],
            "fibroblast": ["COL1A1", "COL1A2", "VIM", "FAP"],
            "t_cell_cd4": ["CD4", "IL2", "IFNG", "FOXP3"],
            "macrophage": ["CD68", "CD14", "CSF1R", "MARCO"],
            "lung_epithelial": ["EPCAM", "SFTPA1", "SCGB1A1", "MUC5AC"],
            "neuron_excitatory": ["SLC17A7", "CAMK2A", "NRGN", "SATB2"],
        }
        return markers.get(cell_type, ["GAPDH", "ACTB"])
        
    def is_gene_in_vocabulary(self, gene: str) -> bool:
        """检查基因是否在词汇表中"""
        # Geneformer通常包含约30,000个基因
        # 实际实现中应检查模型的tokenizer词汇表
        common_genes = set([
            "TP53", "BRCA1", "EGFR", "MYC", "KRAS", "BCL2", "MCL1",
            "PIK3CA", "PTEN", "MTOR", "AKT1", "CDKN1A", "MDM2",
            "ALB", "AFP", "MYH6", "COL1A1", "CD4", "CD68", "EPCAM",
            "GAPDH", "ACTB", "TUBB", "RPLP0"
        ])
        return gene.upper() in common_genes


class scGPTAdapter(BaseModelAdapter):
    """scGPT模型适配器"""
    
    def __init__(self, config: Dict):
        super().__init__("scgpt", config)
        self.embedding_dim = 512
        
    def load_model(self):
        """加载scGPT模型"""
        logger.info("Loading scGPT model...")
        try:
            # 实际使用时需要安装: pip install scgpt
            # from scgpt.model import TransformerModel
            # self.model = TransformerModel.load_from_checkpoint(...)
            logger.info("scGPT model loaded successfully (simulated)")
        except ImportError:
            logger.warning("scGPT not installed, using mock implementation")
            self.model = MockModel(self.model_name)
            
    def predict_perturbation(
        self, 
        genes: List[str], 
        cell_type: str,
        perturbation_type: str = "complete_ko"
    ) -> np.ndarray:
        """模拟scGPT扰动预测"""
        logger.info(f"Predicting {perturbation_type} for genes {genes} in {cell_type}")
        
        ref_expr = self.get_reference_expression(cell_type)
        perturbed_expr = self._simulate_perturbation(ref_expr, genes, perturbation_type)
        
        return perturbed_expr
        
    def _simulate_perturbation(
        self, 
        expression: np.ndarray, 
        genes: List[str],
        perturbation_type: str
    ) -> np.ndarray:
        """模拟扰动效果 (占位实现)"""
        np.random.seed(42)
        
        if perturbation_type == "complete_ko":
            scale = 0.1
        elif perturbation_type == "kd":
            scale = 0.5
        else:
            scale = 0.8
            
        perturbed = expression * scale + np.random.normal(0, 0.3, expression.shape)
        return np.maximum(perturbed, 0)
        
    def get_reference_expression(self, cell_type: str) -> np.ndarray:
        """获取参考表达谱 (模拟)"""
        np.random.seed(hash(cell_type) % 2**32)
        n_genes = 20000
        expression = np.random.lognormal(0, 1.2, n_genes)
        return expression
        
    def is_gene_in_vocabulary(self, gene: str) -> bool:
        """检查基因是否在词汇表中"""
        return True  # scGPT通常有较大的词汇表


class MockModel:
    """模拟模型用于演示"""
    def __init__(self, model_name: str):
        self.model_name = model_name
        
    def predict(self, *args, **kwargs):
        return np.random.randn(100, 256)


# ============================================================================
# Core Analysis Modules
# ============================================================================

class DifferentialExpressionAnalyzer:
    """差异表达分析器"""
    
    def __init__(self, gene_names: List[str]):
        self.gene_names = gene_names
        
    def analyze(
        self, 
        control_expr: np.ndarray, 
        perturbed_expr: np.ndarray,
        perturbation_gene: str,
        cell_type: str,
        pval_threshold: float = 0.05,
        logfc_threshold: float = 1.0
    ) -> List[DifferentialExpressionResult]:
        """
        执行差异表达分析
        
        Args:
            control_expr: 对照组表达谱
            perturbed_expr: 扰动组表达谱
            perturbation_gene: 被扰动的基因
            cell_type: 细胞类型
            
        Returns:
            差异表达结果列表
        """
        logger.info("Running differential expression analysis...")
        
        results = []
        
        for i, gene in enumerate(self.gene_names[:len(control_expr)]):
            control_val = control_expr[i]
            perturbed_val = perturbed_expr[i]
            
            # 计算log2 fold change
            logfc = self._calculate_logfc(control_val, perturbed_val)
            
            # 模拟p值计算 (实际应使用统计检验)
            pval = self._simulate_pvalue(logfc)
            adj_pval = min(pval * len(control_expr), 1.0)  # Bonferroni校正
            
            if abs(logfc) >= logfc_threshold or adj_pval < pval_threshold:
                result = DifferentialExpressionResult(
                    gene_symbol=gene,
                    log2_fold_change=logfc,
                    p_value=pval,
                    adjusted_p_value=adj_pval,
                    perturbation_gene=perturbation_gene,
                    cell_type=cell_type
                )
                results.append(result)
                
        # 按p值排序
        results.sort(key=lambda x: x.p_value)
        
        logger.info(f"Found {len(results)} differentially expressed genes")
        return results
        
    def _calculate_logfc(self, control: float, perturbed: float) -> float:
        """计算log2 fold change"""
        # 添加小值避免log(0)
        control = max(control, 1e-6)
        perturbed = max(perturbed, 1e-6)
        return np.log2(perturbed / control)
        
    def _simulate_pvalue(self, logfc: float) -> float:
        """模拟p值 (基于fold change大小)"""
        # 更大的fold change = 更小的p值
        import random
        base_pval = np.exp(-abs(logfc) * 2)
        noise = random.uniform(0.8, 1.2)
        return min(base_pval * noise, 0.999)


class PathwayEnricher:
    """通路富集分析器"""
    
    def __init__(self):
        # 预定义的通路数据库 (实际应用中使用gseapy等库)
        self.pathway_db = self._load_pathway_databases()
        
    def _load_pathway_databases(self) -> Dict:
        """加载通路数据库"""
        return {
            "KEGG": {
                "p53_signaling_pathway": ["TP53", "MDM2", "CDKN1A", "GADD45A", "BAX", "BCL2"],
                "PI3K_Akt_signaling": ["PIK3CA", "AKT1", "MTOR", "PTEN", "FOXO3", "GSK3B"],
                "MAPK_signaling": ["MAPK1", "MAPK3", "KRAS", "BRAF", "MEK1", "ERK1"],
                "JAK_STAT_signaling": ["JAK1", "JAK2", "STAT1", "STAT3", "SOCS1", "IL6"],
                "TGF_beta_signaling": ["TGFB1", "TGFBR1", "SMAD2", "SMAD3", "SMAD4", "ID1"],
                "Cell_cycle": ["CCND1", "CDK4", "CDK6", "RB1", "E2F1", "MYC"],
                "Apoptosis": ["CASP3", "CASP8", "CASP9", "BCL2", "BAX", "FAS"],
            },
            "GO_BP": {
                "cell_proliferation": ["MYC", "CCND1", "CDK4", "EGFR", "IGF1R"],
                "DNA_repair": ["BRCA1", "BRCA2", "ATM", "ATR", "RAD51", "TP53BP1"],
                "immune_response": ["IL2", "IFNG", "CD4", "CD8A", "FOXP3", "TNF"],
                "metabolic_process": ["MTOR", "AMPK", "SIRT1", "PGC1A", "ACACA"],
                "stress_response": ["HSP90", "HSP70", "ATF4", "DDIT3", "XBP1"],
            }
        }
        
    def enrich(
        self, 
        gene_list: List[str], 
        databases: List[str] = None
    ) -> Dict[str, List[PathwayResult]]:
        """
        执行通路富集分析
        
        Args:
            gene_list: 差异表达基因列表
            databases: 数据库列表
            
        Returns:
            各数据库的富集结果
        """
        if databases is None:
            databases = ["KEGG"]
            
        logger.info(f"Running pathway enrichment for {len(gene_list)} genes...")
        
        results = {}
        
        for db_name in databases:
            if db_name not in self.pathway_db:
                continue
                
            db_results = []
            pathways = self.pathway_db[db_name]
            
            for pathway_name, pathway_genes in pathways.items():
                # 计算重叠
                overlap = set(gene_list) & set(pathway_genes)
                
                if len(overlap) > 0:
                    # 计算富集比率和p值 (简化版Fisher精确检验模拟)
                    enrichment_ratio = len(overlap) / len(pathway_genes)
                    pval = self._calculate_pathway_pvalue(
                        len(overlap), len(gene_list), len(pathway_genes), 20000
                    )
                    
                    result = PathwayResult(
                        pathway_name=pathway_name,
                        p_value=pval,
                        enrichment_ratio=enrichment_ratio,
                        overlap_genes=list(overlap),
                        database=db_name
                    )
                    db_results.append(result)
                    
            # 按p值排序
            db_results.sort(key=lambda x: x.p_value)
            results[db_name] = db_results
            
        logger.info(f"Enrichment analysis completed for {len(results)} databases")
        return results
        
    def _calculate_pathway_pvalue(
        self, 
        overlap: int, 
        gene_set_size: int, 
        pathway_size: int, 
        total_genes: int
    ) -> float:
        """计算通路富集的p值 (超几何分布近似)"""
        from math import comb
        
        # 使用超几何分布计算p值
        try:
            pval = sum(
                comb(pathway_size, k) * comb(total_genes - pathway_size, gene_set_size - k)
                for k in range(overlap, min(gene_set_size, pathway_size) + 1)
            ) / comb(total_genes, gene_set_size)
        except:
            # 简化计算
            expected = (gene_set_size * pathway_size) / total_genes
            if overlap > expected:
                pval = np.exp(-(overlap - expected) ** 2 / (2 * expected))
            else:
                pval = 1.0
                
        return max(min(pval, 1.0), 1e-300)


class TargetScorer:
    """靶点评分器"""
    
    def __init__(self):
        # 权重配置
        self.weights = {
            "efficacy": 0.35,
            "safety": 0.25,
            "druggability": 0.25,
            "novelty": 0.15
        }
        
        # 必需基因数据库 (敲除致死或严重毒性)
        self.essential_genes = set([
            "RPLP0", "RPL13A", "GAPDH", "ACTB", "TUBB",  # 管家基因
            "POLR2A", "POLR2B",  # RNA聚合酶
            "RPS6", "RPS18",  # 核糖体蛋白
        ])
        
        # 已知可成药靶点
        self.druggable_targets = set([
            "EGFR", "ERBB2", "BRAF", "MEK1", "MEK2",
            "PIK3CA", "MTOR", "AKT1", "AKT2",
            "BCL2", "BCLXL", "MCL1",
            "CDK4", "CDK6", "CDK2",
            "JAK1", "JAK2", "STAT3",
        ])
        
    def score(
        self,
        target_gene: str,
        deg_results: List[DifferentialExpressionResult],
        pathway_results: Dict[str, List[PathwayResult]]
    ) -> TargetScore:
        """
        计算靶点综合评分
        
        Args:
            target_gene: 靶点基因
            deg_results: 差异表达结果
            pathway_results: 通路富集结果
            
        Returns:
            靶点评分结果
        """
        # 1. 效果评分 (基于DEG数量和通路变化)
        efficacy = self._calculate_efficacy(deg_results, pathway_results)
        
        # 2. 安全性评分 (避免必需基因)
        safety = self._calculate_safety(target_gene, deg_results)
        
        # 3. 可成药性评分
        druggability = self._calculate_druggability(target_gene)
        
        # 4. 新颖性评分
        novelty = self._calculate_novelty(target_gene)
        
        # 综合评分
        overall = (
            efficacy * self.weights["efficacy"] +
            safety * self.weights["safety"] +
            druggability * self.weights["druggability"] +
            novelty * self.weights["novelty"]
        )
        
        # 生成建议
        recommendation = self._generate_recommendation(
            target_gene, overall, efficacy, safety, druggability
        )
        
        return TargetScore(
            target_gene=target_gene,
            efficacy_score=efficacy,
            safety_score=safety,
            druggability_score=druggability,
            novelty_score=novelty,
            overall_score=overall,
            recommendation=recommendation
        )
        
    def _calculate_efficacy(
        self, 
        deg_results: List[DifferentialExpressionResult],
        pathway_results: Dict[str, List[PathwayResult]]
    ) -> float:
        """计算效果评分"""
        # 基于DEG数量
        n_degs = len(deg_results)
        deg_score = min(n_degs / 500, 1.0)  # 上限500个DEG
        
        # 基于通路富集
        pathway_score = 0
        for db_results in pathway_results.values():
            significant_pathways = sum(1 for r in db_results if r.p_value < 0.05)
            pathway_score = max(pathway_score, significant_pathways / 5)
            
        pathway_score = min(pathway_score, 1.0)
        
        return (deg_score * 0.6 + pathway_score * 0.4)
        
    def _calculate_safety(
        self, 
        target_gene: str,
        deg_results: List[DifferentialExpressionResult]
    ) -> float:
        """计算安全性评分"""
        # 检查是否为必需基因
        if target_gene.upper() in self.essential_genes:
            return 0.1
            
        # 检查DEG中是否有严重毒性标志
        toxicity_markers = ["CASP3", "BAX", "FAS", "TNF", "IL1B"]
        toxic_changes = sum(
            1 for deg in deg_results 
            if deg.gene_symbol in toxicity_markers and abs(deg.log2_fold_change) > 2
        )
        
        if toxic_changes >= 3:
            return 0.3
        elif toxic_changes >= 1:
            return 0.6
        else:
            return 0.9
            
    def _calculate_druggability(self, target_gene: str) -> float:
        """计算可成药性评分"""
        base_score = 0.5
        
        # 已知可成药靶点加分
        if target_gene.upper() in self.druggable_targets:
            base_score += 0.3
            
        # 激酶类靶点通常可成药
        if any(kinase in target_gene.upper() for kinase in ["KRAS", "EGFR", "BRAF", "CDK", "JAK"]):
            base_score += 0.1
            
        return min(base_score, 1.0)
        
    def _calculate_novelty(self, target_gene: str) -> float:
        """计算新颖性评分"""
        # 已知靶点得分低，新靶点得分高
        if target_gene.upper() in self.druggable_targets:
            return 0.3
        elif target_gene.upper().startswith(("ORF", "LOC")):
            return 0.9  # 未表征基因
        else:
            return 0.7
            
    def _generate_recommendation(
        self,
        target_gene: str,
        overall: float,
        efficacy: float,
        safety: float,
        druggability: float
    ) -> str:
        """生成验证建议"""
        if overall >= 0.8 and safety >= 0.7:
            return "HIGH_PRIORITY: 优先进行湿实验验证"
        elif overall >= 0.6 and efficacy >= 0.7:
            return "MEDIUM_PRIORITY: 建议验证，需关注安全性"
        elif druggability >= 0.7:
            return "LOW_PRIORITY: 可成药性好但效果待验证"
        else:
            return "NOT_RECOMMENDED: 不建议优先验证"


# ============================================================================
# Visualization Module
# ============================================================================

class ResultVisualizer:
    """结果可视化器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_volcano_plot(
        self, 
        deg_results: List[DifferentialExpressionResult],
        filename: str = "volcano_plot.png"
    ) -> str:
        """创建火山图"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            genes = [r.gene_symbol for r in deg_results]
            logfc = [r.log2_fold_change for r in deg_results]
            pvals = [-np.log10(r.p_value) for r in deg_results]
            
            # 颜色区分上调/下调
            colors = ['red' if fc > 0 else 'blue' for fc in logfc]
            
            ax.scatter(logfc, pvals, c=colors, alpha=0.6, s=20)
            
            # 标记Top基因
            top_genes = sorted(deg_results, key=lambda x: x.p_value)[:10]
            for gene in top_genes:
                ax.annotate(
                    gene.gene_symbol,
                    (gene.log2_fold_change, -np.log10(gene.p_value)),
                    fontsize=8
                )
                
            ax.axhline(y=-np.log10(0.05), color='gray', linestyle='--', alpha=0.5)
            ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
            
            ax.set_xlabel('Log2 Fold Change')
            ax.set_ylabel('-Log10 P-value')
            ax.set_title('Differential Expression Volcano Plot')
            
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Volcano plot saved to {filepath}")
            return str(filepath)
        except ImportError:
            logger.warning("matplotlib not installed, skipping visualization")
            return None
            
    def create_target_ranking_plot(
        self,
        target_scores: List[TargetScore],
        filename: str = "target_ranking.png"
    ) -> str:
        """创建靶点排序图"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            scores = sorted(target_scores, key=lambda x: x.overall_score, reverse=True)[:20]
            
            genes = [s.target_gene for s in scores]
            overall_scores = [s.overall_score for s in scores]
            
            y_pos = range(len(genes))
            ax.barh(y_pos, overall_scores, color='steelblue')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(genes)
            ax.invert_yaxis()
            ax.set_xlabel('Overall Score')
            ax.set_title('Top 20 Target Gene Rankings')
            
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Target ranking plot saved to {filepath}")
            return str(filepath)
        except ImportError:
            logger.warning("matplotlib not installed, skipping visualization")
            return None


# ============================================================================
# Main Oracle Class
# ============================================================================

class PerturbationOracle:
    """
    In Silico Perturbation Oracle 主类
    
    虚拟基因敲除预测的核心接口
    """
    
    def __init__(
        self,
        model_name: str = "geneformer",
        cell_type: str = "fibroblast",
        output_dir: str = "./results",
        config: Optional[Dict] = None
    ):
        """
        初始化Oracle
        
        Args:
            model_name: 模型名称 (geneformer/scgpt)
            cell_type: 细胞类型
            output_dir: 输出目录
            config: 额外配置
        """
        self.model_name = model_name
        self.cell_type = cell_type
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # 初始化模型
        self.model_adapter = self._create_model_adapter()
        self.model_adapter.load_model()
        
        # 初始化分析模块
        self.gene_names = [f"GENE_{i}" for i in range(20000)]  # 模拟基因名
        self.de_analyzer = DifferentialExpressionAnalyzer(self.gene_names)
        self.pathway_enricher = PathwayEnricher()
        self.target_scorer = TargetScorer()
        self.visualizer = ResultVisualizer(str(self.output_dir))
        
        logger.info(f"PerturbationOracle initialized: {model_name} + {cell_type}")
        
    def _create_model_adapter(self) -> BaseModelAdapter:
        """创建模型适配器"""
        if self.model_name.lower() == "geneformer":
            return GeneformerAdapter(self.config)
        elif self.model_name.lower() == "scgpt":
            return scGPTAdapter(self.config)
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")
            
    def predict_knockout(
        self,
        genes: List[str],
        perturbation_type: str = "complete_ko",
        n_permutations: int = 100,
        **kwargs
    ) -> 'PerturbationResult':
        """
        预测基因敲除效果
        
        Args:
            genes: 待敲除的基因列表
            perturbation_type: 扰动类型
            n_permutations: 置换次数
            
        Returns:
            PerturbationResult对象
        """
        all_results = []
        
        for gene in genes:
            logger.info(f"Analyzing knockout of {gene}...")
            
            # 获取参考表达
            control_expr = self.model_adapter.get_reference_expression(self.cell_type)
            
            # 预测扰动后表达
            perturbed_expr = self.model_adapter.predict_perturbation(
                [gene], self.cell_type, perturbation_type
            )
            
            # 差异表达分析
            deg_results = self.de_analyzer.analyze(
                control_expr, perturbed_expr, gene, self.cell_type
            )
            
            # 通路富集
            deg_genes = [r.gene_symbol for r in deg_results]
            pathway_results = self.pathway_enricher.enrich(
                deg_genes, databases=["KEGG", "GO_BP"]
            )
            
            # 靶点评分
            target_score = self.target_scorer.score(gene, deg_results, pathway_results)
            
            all_results.append({
                "gene": gene,
                "deg_results": deg_results,
                "pathway_results": pathway_results,
                "target_score": target_score
            })
            
        return PerturbationResult(all_results, self.output_dir)
        
    def predict_combinatorial_ko(
        self,
        gene_pairs: List[Tuple[str, str]],
        synergy_threshold: float = 0.3,
        **kwargs
    ) -> 'CombinatorialResult':
        """
        预测组合基因敲除
        
        Args:
            gene_pairs: 基因对列表
            synergy_threshold: 协同效应阈值
            
        Returns:
            CombinatorialResult对象
        """
        logger.info(f"Analyzing {len(gene_pairs)} gene combinations...")
        
        results = []
        for g1, g2 in gene_pairs:
            # 单独敲除
            single1 = self.predict_knockout([g1])
            single2 = self.predict_knockout([g2])
            
            # 组合敲除
            double = self.predict_knockout([g1, g2])
            
            # 计算协同效应 (简化版Bliss模型)
            synergy = self._calculate_synergy(single1, single2, double)
            
            results.append({
                "genes": (g1, g2),
                "synergy_score": synergy,
                "is_synergistic": synergy > synergy_threshold
            })
            
        return CombinatorialResult(results)
        
    def _calculate_synergy(
        self, 
        single1: 'PerturbationResult',
        single2: 'PerturbationResult',
        double: 'PerturbationResult'
    ) -> float:
        """计算协同效应分数"""
        # 简化计算: 基于DEG数量的协同
        n_single1 = len(single1.results[0]["deg_results"])
        n_single2 = len(single2.results[0]["deg_results"])
        n_double = len(double.results[0]["deg_results"])
        
        expected = n_single1 + n_single2
        if expected == 0:
            return 0
            
        synergy = (n_double - expected) / max(expected, 1)
        return synergy
        
    def export_validation_guide(
        self,
        top_targets: int = 10,
        include_controls: bool = True,
        format: str = "lab_protocol"
    ) -> str:
        """
        导出湿实验验证指南
        
        Args:
            top_targets: Top靶点数量
            include_controls: 是否包含对照
            format: 输出格式
            
        Returns:
            指南文件路径
        """
        guide_path = self.output_dir / "validation_guide.txt"
        
        with open(guide_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("湿实验验证指南 - In Silico Perturbation Oracle\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"生成时间: {datetime.now().isoformat()}\n")
            f.write(f"模型: {self.model_name}\n")
            f.write(f"细胞类型: {self.cell_type}\n\n")
            
            f.write("实验设计建议:\n")
            f.write("-" * 40 + "\n")
            f.write("1. CRISPR-Cas9敲除实验\n")
            f.write("   - 设计至少2个独立sgRNA per target\n")
            f.write("   - 包含非靶向对照(NTC)\n")
            f.write("   - 使用qPCR验证敲除效率(>80%)\n\n")
            
            f.write("2. 表型检测建议\n")
            f.write("   - 细胞增殖: CCK-8或EdU\n")
            f.write("   - 凋亡检测: Annexin V/PI\n")
            f.write("   - 转录组验证: RNA-seq (n=3 per group)\n\n")
            
            f.write("3. 数据分析要点\n")
            f.write("   - 与in silico预测的一致性评估\n")
            f.write("   - 差异表达基因重叠分析\n")
            f.write("   - 通路富集一致性验证\n\n")
            
        logger.info(f"Validation guide exported to {guide_path}")
        return str(guide_path)


class PerturbationResult:
    """扰动预测结果容器"""
    
    def __init__(self, results: List[Dict], output_dir: Path):
        self.results = results
        self.output_dir = output_dir
        
    def get_differential_expression(
        self,
        pval_threshold: float = 0.05,
        logfc_threshold: float = 1.0
    ) -> pd.DataFrame:
        """获取差异表达基因DataFrame"""
        all_degs = []
        
        for result in self.results:
            for deg in result["deg_results"]:
                if (deg.p_value < pval_threshold and 
                    abs(deg.log2_fold_change) >= logfc_threshold):
                    all_degs.append(deg.to_dict())
                    
        return pd.DataFrame(all_degs)
        
    def enrich_pathways(
        self,
        database: List[str] = None,
        top_n: int = 10
    ) -> Dict:
        """获取通路富集结果"""
        if database is None:
            database = ["KEGG"]
            
        all_pathways = defaultdict(list)
        
        for result in self.results:
            for db_name, pathways in result["pathway_results"].items():
                if db_name in database:
                    all_pathways[db_name].extend(pathways[:top_n])
                    
        return dict(all_pathways)
        
    def score_targets(self) -> pd.DataFrame:
        """获取靶点评分DataFrame"""
        scores = [r["target_score"] for r in self.results]
        data = [{
            "target_gene": s.target_gene,
            "efficacy_score": s.efficacy_score,
            "safety_score": s.safety_score,
            "druggability_score": s.druggability_score,
            "novelty_score": s.novelty_score,
            "overall_score": s.overall_score,
            "recommendation": s.recommendation
        } for s in scores]
        
        df = pd.DataFrame(data)
        return df.sort_values("overall_score", ascending=False)
        
    def save(self, prefix: str = ""):
        """保存所有结果"""
        # 保存DEG结果
        deg_df = self.get_differential_expression()
        deg_path = self.output_dir / f"{prefix}deg_results.csv"
        deg_df.to_csv(deg_path, index=False)
        logger.info(f"DEG results saved to {deg_path}")
        
        # 保存靶点评分
        score_df = self.score_targets()
        score_path = self.output_dir / f"{prefix}target_scores.csv"
        score_df.to_csv(score_path, index=False)
        logger.info(f"Target scores saved to {score_path}")
        
        # 保存通路富集结果
        pathways = self.enrich_pathways()
        pathway_path = self.output_dir / f"{prefix}pathway_enrichment.json"
        
        # 转换为可序列化格式
        pathways_serializable = {}
        for db, results in pathways.items():
            pathways_serializable[db] = [
                {
                    "pathway_name": r.pathway_name,
                    "p_value": r.p_value,
                    "enrichment_ratio": r.enrichment_ratio,
                    "overlap_genes": r.overlap_genes,
                    "database": r.database
                }
                for r in results
            ]
            
        with open(pathway_path, 'w') as f:
            json.dump(pathways_serializable, f, indent=2)
        logger.info(f"Pathway enrichment saved to {pathway_path}")
        
        return {
            "deg_results": str(deg_path),
            "target_scores": str(score_path),
            "pathway_enrichment": str(pathway_path)
        }


class CombinatorialResult:
    """组合敲除结果容器"""
    
    def __init__(self, results: List[Dict]):
        self.results = results
        
    def get_synergistic_pairs(self, threshold: float = 0.3) -> List[Tuple[str, str]]:
        """获取协同作用基因对"""
        return [
            r["genes"] for r in self.results 
            if r["synergy_score"] > threshold
        ]
        
    def to_dataframe(self) -> pd.DataFrame:
        """转换为DataFrame"""
        data = [
            {
                "gene1": r["genes"][0],
                "gene2": r["genes"][1],
                "synergy_score": r["synergy_score"],
                "is_synergistic": r["is_synergistic"]
            }
            for r in self.results
        ]
        return pd.DataFrame(data)


# ============================================================================
# CLI Interface
# ============================================================================

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="In Silico Perturbation Oracle - Virtual Gene Knockout Prediction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 单基因敲除预测
  python main.py --model geneformer --genes TP53,BRCA1 --cell-type hepatocyte
  
  # 批量靶点筛选
  python main.py --model scgpt --genes-file targets.txt --cell-type fibroblast --top-k 20
  
  # 组合敲除预测
  python main.py --combinatorial --gene-pairs "BCL2,MCL1" --gene-pairs "PIK3CA,PTEN"
        """
    )
    
    # 必需参数
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="geneformer",
        choices=["geneformer", "scgpt"],
        help="基础模型选择 (default: geneformer)"
    )
    parser.add_argument(
        "--genes", "-g",
        type=str,
        help="逗号分隔的基因列表，如 TP53,BRCA1,EGFR"
    )
    parser.add_argument(
        "--genes-file",
        type=str,
        help="包含基因列表的文件路径"
    )
    parser.add_argument(
        "--cell-type", "-c",
        type=str,
        required=True,
        help="细胞类型，如 hepatocyte, cardiomyocyte, fibroblast"
    )
    
    # 可选参数
    parser.add_argument(
        "--perturbation-type", "-p",
        type=str,
        default="complete_ko",
        choices=["complete_ko", "kd", "crispr"],
        help="扰动类型 (default: complete_ko)"
    )
    parser.add_argument(
        "--n-permutations",
        type=int,
        default=100,
        help="置换检验次数 (default: 100)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=50,
        help="输出Top K靶点 (default: 50)"
    )
    parser.add_argument(
        "--pathways",
        type=str,
        default="KEGG,GO_BP",
        help="逗号分隔的通路数据库"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./results",
        help="输出目录 (default: ./results)"
    )
    
    # 组合敲除
    parser.add_argument(
        "--combinatorial",
        action="store_true",
        help="启用组合敲除模式"
    )
    parser.add_argument(
        "--gene-pairs",
        type=str,
        action="append",
        help='基因对，格式: "GENE1,GENE2"，可多次使用'
    )
    parser.add_argument(
        "--synergy-threshold",
        type=float,
        default=0.3,
        help="协同效应阈值 (default: 0.3)"
    )
    
    # 其他
    parser.add_argument(
        "--export-guide",
        action="store_true",
        help="导出湿实验验证指南"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    return parser.parse_args()


def main():
    """主入口函数"""
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # 解析基因列表
    genes = []
    if args.genes:
        genes = [g.strip().upper() for g in args.genes.split(",")]
    elif args.genes_file:
        with open(args.genes_file, 'r') as f:
            genes = [line.strip().upper() for line in f if line.strip()]
    elif not args.combinatorial:
        logger.error("必须提供 --genes 或 --genes-file 参数")
        sys.exit(1)
        
    # 解析通路数据库
    pathways = [p.strip() for p in args.pathways.split(",")]
    
    # 初始化Oracle
    oracle = PerturbationOracle(
        model_name=args.model,
        cell_type=args.cell_type,
        output_dir=args.output
    )
    
    logger.info("=" * 60)
    logger.info("In Silico Perturbation Oracle")
    logger.info("=" * 60)
    logger.info(f"Model: {args.model}")
    logger.info(f"Cell Type: {args.cell_type}")
    logger.info(f"Output: {args.output}")
    logger.info("=" * 60)
    
    # 执行预测
    if args.combinatorial and args.gene_pairs:
        # 组合敲除模式
        gene_pairs = []
        for pair_str in args.gene_pairs:
            g1, g2 = pair_str.split(",")
            gene_pairs.append((g1.strip().upper(), g2.strip().upper()))
            
        logger.info(f"Running combinatorial knockout for {len(gene_pairs)} pairs...")
        results = oracle.predict_combinatorial_ko(
            gene_pairs=gene_pairs,
            synergy_threshold=args.synergy_threshold
        )
        
        # 输出协同作用结果
        synergistic = results.get_synergistic_pairs()
        logger.info(f"Found {len(synergistic)} synergistic pairs")
        for pair in synergistic[:5]:
            logger.info(f"  - {pair[0]} + {pair[1]}")
            
        # 保存结果
        df = results.to_dataframe()
        output_path = Path(args.output) / "combinatorial_results.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Results saved to {output_path}")
        
    else:
        # 单基因敲除模式
        logger.info(f"Analyzing {len(genes)} genes: {', '.join(genes[:5])}{'...' if len(genes) > 5 else ''}")
        
        results = oracle.predict_knockout(
            genes=genes,
            perturbation_type=args.perturbation_type,
            n_permutations=args.n_permutations
        )
        
        # 保存结果
        saved_paths = results.save()
        
        # 靶点评分
        target_scores = results.score_targets()
        logger.info("\n" + "=" * 60)
        logger.info("Top Target Recommendations:")
        logger.info("=" * 60)
        for _, row in target_scores.head(args.top_k).iterrows():
            logger.info(f"  {row['target_gene']:10s} | Score: {row['overall_score']:.3f} | {row['recommendation']}")
            
        logger.info("=" * 60)
        
    # 导出验证指南
    if args.export_guide:
        guide_path = oracle.export_validation_guide()
        logger.info(f"Validation guide: {guide_path}")
        
    logger.info("Analysis completed successfully!")


if __name__ == "__main__":
    main()
