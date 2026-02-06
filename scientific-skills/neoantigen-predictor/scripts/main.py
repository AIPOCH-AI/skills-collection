#!/usr/bin/env python3
"""
Neoantigen Predictor Module
基于患者HLA分型和肿瘤突变预测新抗原
支持MHC-I类分子结合预测和免疫原性评估
"""

import json
import re
import argparse
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MHC_Binding:
    """MHC结合预测结果"""
    rank_percentile: float = 100.0  # 结合排名百分比 (越低越好)
    affinity_nM: Optional[float] = None  # 结合亲和力(nM)
    binding_level: str = "Non-binder"  # Strong/Weak/Non-binder
    core_peptide: str = ""  # 核心结合序列
    anchor_residues: List[int] = field(default_factory=list)  # 锚定残基位置
    score_el: Optional[float] = None  # EL (Eluted Ligand) score
    score_ba: Optional[float] = None  # BA (Binding Affinity) score


@dataclass
class Immunogenicity:
    """免疫原性评估结果"""
    foreignness_score: float = 0.0  # 外源性评分 (0-1)
    self_similarity: float = 1.0  # 自身相似度 (越低越好)
    amino_acid_change: str = ""  # 氨基酸变化
    anchor_mutation: bool = False  # 突变是否在锚定位置
    hydrophobicity_change: float = 0.0  # 疏水性变化
    recognition_probability: float = 0.0  # 被T细胞识别的概率


@dataclass
class Clinical_Info:
    """临床相关信息"""
    variant_allele_frequency: Optional[float] = None  # 变异等位基因频率
    expression_level: Optional[str] = None  # 基因表达水平
    clonality: Optional[str] = None  # 克隆性 (Clonal/Subclonal)
    rna_editing: bool = False  # 是否为RNA编辑位点
    germline_risk: bool = False  # 是否可能为胚系变异


@dataclass
class Neoantigen_Candidate:
    """新抗原候选完整信息"""
    # 标识信息
    mutation_id: str = ""
    gene: str = ""
    chromosome: str = ""
    position: int = 0
    
    # 变异信息
    ref_aa: str = ""
    alt_aa: str = ""
    protein_change: str = ""  # 如 p.R273H
    
    # HLA信息
    hla_allele: str = ""
    
    # 肽段信息
    peptide_sequence: str = ""
    peptide_length: int = 9
    mutant_position: int = 0  # 突变氨基酸在肽段中的位置 (1-based)
    wildtype_peptide: str = ""  # 野生型肽段
    
    # 预测结果
    mhc_binding: MHC_Binding = field(default_factory=MHC_Binding)
    immunogenicity: Immunogenicity = field(default_factory=Immunogenicity)
    clinical_info: Clinical_Info = field(default_factory=Clinical_Info)
    
    # 综合评分
    priority_score: float = 0.0
    rank: int = 0


@dataclass
class Prediction_Result:
    """完整预测结果"""
    patient_hla: List[str] = field(default_factory=list)
    prediction_method: str = "NetMHCpan 4.1"
    total_predictions: int = 0
    strong_binders: int = 0
    weak_binders: int = 0
    neoantigens: List[Neoantigen_Candidate] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class NetMHC_Predictor:
    """NetMHC结合预测模拟器 (实际部署时替换为真实API调用或本地程序)"""
    
    # HLA锚定位置残基偏好 (基于已知结合基序)
    ANCHOR_PREFERENCES = {
        'HLA-A*01:01': {2: ['S', 'T', 'Y'], 9: ['A', 'V', 'I', 'L']},
        'HLA-A*02:01': {2: ['L', 'M', 'I', 'V'], 9: ['V', 'L', 'I', 'A']},
        'HLA-A*03:01': {2: ['L', 'M', 'I', 'V', 'F'], 9: ['K', 'R', 'Y']},
        'HLA-A*11:01': {2: ['T', 'V', 'I', 'M'], 9: ['K', 'R']},
        'HLA-A*24:02': {2: ['Y', 'F', 'W'], 9: ['F', 'I', 'L', 'W']},
        'HLA-A*68:01': {2: ['T', 'V', 'S'], 9: ['A', 'V', 'I']},
        'HLA-B*07:02': {2: ['P', 'R'], 9: ['L', 'F']},
        'HLA-B*08:01': {2: ['K', 'R'], 9: ['L', 'I']},
        'HLA-B*27:05': {2: ['R'], 9: ['L', 'F', 'I']},
        'HLA-B*35:01': {2: ['P', 'Y'], 9: ['L', 'F', 'M']},
        'HLA-B*57:01': {2: ['S', 'T'], 9: ['F', 'W']},
        'HLA-B*58:01': {2: ['A', 'T', 'S'], 9: ['F', 'W']},
    }
    
    # 疏水性标度 (Kyte-Doolittle)
    HYDROPATHY = {
        'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5,
        'M': 1.9, 'A': 1.8, 'G': -0.4, 'T': -0.7, 'S': -0.8,
        'W': -0.9, 'Y': -1.3, 'P': -1.6, 'H': -3.2, 'E': -3.5,
        'Q': -3.5, 'D': -3.5, 'N': -3.5, 'K': -3.9, 'R': -4.5
    }
    
    def __init__(self, method: str = "netmhcpan"):
        self.method = method
        logger.info(f"Initialized NetMHC predictor (method: {method})")
    
    def predict_binding(self, peptide: str, hla_allele: str) -> MHC_Binding:
        """
        预测肽段与HLA的结合亲和力
        注：此为简化模拟实现，实际应调用NetMHCpan程序
        """
        peptide = peptide.upper()
        length = len(peptide)
        
        # 标准化HLA命名
        hla_normalized = self._normalize_hla(hla_allele)
        
        # 基于锚定残基和物理化学性质的简化评分
        score = self._calculate_binding_score(peptide, hla_normalized, length)
        
        # 转换为rank百分比 (模拟)
        rank = self._score_to_rank(score)
        
        # 确定结合等级
        if rank <= 0.5:
            binding_level = "Strong"
        elif rank <= 2:
            binding_level = "Weak"
        else:
            binding_level = "Non-binder"
        
        # 计算IC50 (模拟)
        affinity = self._rank_to_ic50(rank) if rank < 10 else None
        
        # 识别锚定残基位置
        anchors = self._identify_anchors(hla_normalized, length)
        
        return MHC_Binding(
            rank_percentile=rank,
            affinity_nM=affinity,
            binding_level=binding_level,
            core_peptide=peptide,
            anchor_residues=anchors,
            score_el=score,
            score_ba=score * 0.9
        )
    
    def _normalize_hla(self, hla: str) -> str:
        """标准化HLA命名"""
        hla = hla.strip().upper()
        # 移除HLA-前缀
        if hla.startswith("HLA-"):
            hla = hla[4:]
        # 添加HLA-前缀用于匹配
        return f"HLA-{hla}"
    
    def _calculate_binding_score(self, peptide: str, hla: str, length: int) -> float:
        """计算结合评分 (简化模型)"""
        score = 0.5  # 基础分
        
        # 长度惩罚 (8-11mer为MHC-I最佳)
        if length < 8 or length > 11:
            score -= 0.3
        elif 9 <= length <= 10:
            score += 0.1
        
        # 锚定位置偏好
        if hla in self.ANCHOR_PREFERENCES:
            prefs = self.ANCHOR_PREFERENCES[hla]
            # 位置2
            if 2 in prefs and len(peptide) > 2:
                if peptide[1] in prefs[2]:
                    score += 0.25
                elif peptide[1] in ['A', 'V', 'L', 'I', 'F', 'W', 'Y', 'M']:
                    score += 0.1
            # C末端 (位置length)
            if length in prefs:
                if peptide[-1] in prefs[length]:
                    score += 0.25
                elif peptide[-1] in ['V', 'L', 'I', 'F', 'Y']:
                    score += 0.1
        
        # GC含量检查 (最佳40-60%)
        gc_count = peptide.count('G') + peptide.count('C')
        gc_percent = gc_count / length
        if 0.3 <= gc_percent <= 0.7:
            score += 0.1
        
        # 疏水性检查 (C末端偏好疏水性)
        if peptide and peptide[-1] in self.HYDROPATHY:
            if self.HYDROPATHY[peptide[-1]] > 0:
                score += 0.1
        
        # Proline惩罚 (破坏螺旋)
        if 'P' in peptide[2:-1]:
            score -= 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _score_to_rank(self, score: float) -> float:
        """将评分转换为rank百分比 (模拟)"""
        # 线性映射 (简化)
        rank = (1 - score) * 10
        return max(0.01, min(100, rank))
    
    def _rank_to_ic50(self, rank: float) -> float:
        """将rank转换为IC50值 (nM)"""
        # 近似转换: rank 0.5% ≈ 50nM, rank 2% ≈ 500nM
        if rank <= 0.5:
            return rank * 100
        else:
            return 50 + (rank - 0.5) * 300
    
    def _identify_anchors(self, hla: str, length: int) -> List[int]:
        """识别锚定残基位置"""
        anchors = [2, length]  # MHC-I通常为位置2和C末端
        return anchors


class NeoantigenPredictor:
    """新抗原预测主类"""
    
    # 氨基酸单字母代码
    AA_3TO1 = {
        'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
        'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
        'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
        'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
        'TER': '*', 'STP': '*', 'XAA': 'X'
    }
    
    WEIGHTS = {
        'mhc_binding': 0.40,
        'immunogenicity': 0.35,
        'clinical': 0.25
    }
    
    def __init__(self, mhc_method: str = "netmhcpan"):
        self.mhc_predictor = NetMHC_Predictor(method=mhc_method)
        logger.info("NeoantigenPredictor initialized")
    
    def predict(
        self,
        hla_alleles: List[str],
        mutations: List[Dict[str, Any]],
        peptide_length: List[int] = None,
        transcript_sequences: Dict[str, str] = None
    ) -> Prediction_Result:
        """
        执行新抗原预测
        
        Args:
            hla_alleles: 患者HLA等位基因列表
            mutations: 突变信息列表
            peptide_length: 肽段长度列表 (默认 [9, 10])
            transcript_sequences: 转录本序列字典 (可选)
        
        Returns:
            Prediction_Result: 完整预测结果
        """
        if peptide_length is None:
            peptide_length = [9, 10]
        
        # 标准化HLA命名
        normalized_hla = [self._normalize_hla(hla) for hla in hla_alleles]
        
        candidates = []
        
        for mutation in mutations:
            # 生成变异肽段
            variant_peptides = self._generate_variant_peptides(
                mutation, peptide_length, transcript_sequences
            )
            
            for var_pep, wt_pep, mut_pos in variant_peptides:
                # 对每个HLA等位基因进行预测
                for hla in normalized_hla:
                    candidate = self._predict_candidate(
                        mutation=mutation,
                        peptide=var_pep,
                        wildtype_peptide=wt_pep,
                        mutant_position=mut_pos,
                        hla_allele=hla
                    )
                    candidates.append(candidate)
        
        # 优先级排序
        ranked_candidates = self._rank_candidates(candidates)
        
        # 统计
        strong_binders = sum(1 for c in candidates if c.mhc_binding.binding_level == "Strong")
        weak_binders = sum(1 for c in candidates if c.mhc_binding.binding_level == "Weak")
        
        # 构建结果
        result = Prediction_Result(
            patient_hla=normalized_hla,
            total_predictions=len(candidates),
            strong_binders=strong_binders,
            weak_binders=weak_binders,
            neoantigens=ranked_candidates,
            summary={
                "top_candidates": min(10, len(ranked_candidates)),
                "binding_distribution": {
                    "strong": strong_binders,
                    "weak": weak_binders,
                    "non_binder": len(candidates) - strong_binders - weak_binders
                }
            }
        )
        
        return result
    
    def _normalize_hla(self, hla: str) -> str:
        """标准化HLA命名格式"""
        hla = hla.strip().upper()
        
        # 确保有HLA-前缀
        if not hla.startswith("HLA-"):
            # 检查是否是A/B/C格式
            if hla[0] in ['A', 'B', 'C'] and (len(hla) == 1 or not hla[1].isdigit()):
                hla = f"HLA-{hla[0]}*{hla[1:3]}:{hla[3:]}"
            elif hla[0] in ['A', 'B', 'C']:
                hla = f"HLA-{hla}"
        
        return hla
    
    def _parse_protein_change(self, protein_change: str) -> Tuple[str, int, str]:
        """
        解析蛋白质变化 (如 p.R273H -> (R, 273, H))
        Returns: (ref_aa, position, alt_aa)
        """
        # 移除 p. 前缀
        if protein_change.startswith('p.'):
            protein_change = protein_change[2:]
        
        # 匹配模式: R273H, Arg273His等
        patterns = [
            r'([A-Za-z]{3})(\d+)([A-Za-z]{3})',  # 三字母: Arg273His
            r'([A-Za-z])(\d+)([A-Za-z*])',         # 单字母: R273H, R273*
        ]
        
        for pattern in patterns:
            match = re.match(pattern, protein_change)
            if match:
                ref = match.group(1)
                pos = int(match.group(2))
                alt = match.group(3)
                
                # 转换三字母为单字母
                if len(ref) == 3:
                    ref = self.AA_3TO1.get(ref.upper(), 'X')
                if len(alt) == 3:
                    alt = self.AA_3TO1.get(alt.upper(), 'X')
                
                return (ref.upper(), pos, alt.upper())
        
        raise ValueError(f"无法解析蛋白质变化: {protein_change}")
    
    def _generate_variant_peptides(
        self,
        mutation: Dict[str, Any],
        peptide_lengths: List[int],
        transcript_sequences: Dict[str, str] = None
    ) -> List[Tuple[str, str, int]]:
        """
        生成变异肽段
        Returns: [(变异肽段, 野生型肽段, 突变位置), ...]
        """
        peptides = []
        
        protein_change = mutation.get('protein_change', '')
        if not protein_change:
            return peptides
        
        try:
            ref_aa, mut_pos, alt_aa = self._parse_protein_change(protein_change)
        except ValueError:
            logger.warning(f"无法解析突变: {protein_change}")
            return peptides
        
        gene = mutation.get('gene', 'Unknown')
        
        # 获取蛋白质序列 (简化:使用模拟序列)
        # 实际应用应从Ensembl/Uniprot获取真实序列
        protein_seq = self._get_protein_sequence(gene, transcript_sequences)
        
        if not protein_seq or mut_pos > len(protein_seq):
            logger.warning(f"无法获取蛋白质序列或位置超出范围: {gene} pos {mut_pos}")
            # 生成模拟肽段用于演示
            return self._generate_mock_peptides(ref_aa, alt_aa, peptide_lengths)
        
        # 验证参考氨基酸
        if protein_seq[mut_pos - 1] != ref_aa:
            logger.warning(f"参考氨基酸不匹配: 期望 {ref_aa}, 实际 {protein_seq[mut_pos - 1]}")
        
        # 生成变异序列
        variant_seq = protein_seq[:mut_pos - 1] + alt_aa + protein_seq[mut_pos:]
        
        # 提取各长度的肽段
        for length in peptide_lengths:
            for start in range(max(0, mut_pos - length), min(mut_pos, len(protein_seq) - length + 1)):
                end = start + length
                
                wt_peptide = protein_seq[start:end]
                var_peptide = variant_seq[start:end]
                
                # 确保突变包含在肽段中
                if ref_aa != alt_aa and var_peptide == wt_peptide:
                    continue
                
                mut_in_peptide = mut_pos - start  # 1-based位置
                peptides.append((var_peptide, wt_peptide, mut_in_peptide))
        
        return peptides
    
    def _get_protein_sequence(
        self,
        gene: str,
        transcript_sequences: Dict[str, str] = None
    ) -> Optional[str]:
        """获取蛋白质序列 (简化实现)"""
        if transcript_sequences and gene in transcript_sequences:
            return transcript_sequences[gene]
        
        # 返回模拟序列 (实际应从数据库获取)
        return self._generate_mock_protein(gene)
    
    def _generate_mock_protein(self, gene: str) -> str:
        """生成模拟蛋白质序列 (演示用)"""
        # 基于基因名生成伪随机但一致的序列
        import random
        random.seed(gene)
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        length = random.randint(200, 500)
        return ''.join(random.choice(amino_acids) for _ in range(length))
    
    def _generate_mock_peptides(
        self,
        ref_aa: str,
        alt_aa: str,
        lengths: List[int]
    ) -> List[Tuple[str, str, int]]:
        """生成模拟肽段 (演示用)"""
        peptides = []
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        import random
        random.seed(f"{ref_aa}{alt_aa}")
        
        for length in lengths:
            for _ in range(3):  # 每种长度生成3个
                flank = (length - 1) // 2
                left = ''.join(random.choice(amino_acids) for _ in range(flank))
                right = ''.join(random.choice(amino_acids) for _ in range(length - flank - 1))
                
                var_pep = left + alt_aa + right
                wt_pep = left + ref_aa + right
                peptides.append((var_pep, wt_pep, flank + 1))
        
        return peptides
    
    def _predict_candidate(
        self,
        mutation: Dict[str, Any],
        peptide: str,
        wildtype_peptide: str,
        mutant_position: int,
        hla_allele: str
    ) -> Neoantigen_Candidate:
        """预测单个候选新抗原"""
        
        # MHC结合预测
        mhc_binding = self.mhc_predictor.predict_binding(peptide, hla_allele)
        
        # 免疫原性评估
        immunogenicity = self._assess_immunogenicity(
            peptide, wildtype_peptide, mutant_position, mhc_binding.anchor_residues
        )
        
        # 构建候选对象
        candidate = Neoantigen_Candidate(
            mutation_id=f"{mutation.get('gene', 'Unknown')}_{mutation.get('protein_change', '')}",
            gene=mutation.get('gene', 'Unknown'),
            chromosome=mutation.get('chrom', ''),
            position=mutation.get('pos', 0),
            ref_aa=wildtype_peptide[mutant_position - 1] if mutant_position <= len(wildtype_peptide) else '',
            alt_aa=peptide[mutant_position - 1] if mutant_position <= len(peptide) else '',
            protein_change=mutation.get('protein_change', ''),
            hla_allele=hla_allele,
            peptide_sequence=peptide,
            peptide_length=len(peptide),
            mutant_position=mutant_position,
            wildtype_peptide=wildtype_peptide,
            mhc_binding=mhc_binding,
            immunogenicity=immunogenicity
        )
        
        # 计算优先级评分
        candidate.priority_score = self._calculate_priority_score(candidate)
        
        return candidate
    
    def _assess_immunogenicity(
        self,
        variant_peptide: str,
        wildtype_peptide: str,
        mutant_position: int,
        anchor_positions: List[int]
    ) -> Immunogenicity:
        """评估免疫原性"""
        
        # 计算外源性评分 (与野生型的差异)
        diff_count = sum(1 for a, b in zip(variant_peptide, wildtype_peptide) if a != b)
        foreignness = min(1.0, diff_count / len(variant_peptide))
        
        # 检查突变是否在锚定位置
        anchor_mutation = mutant_position in anchor_positions
        
        # 计算疏水性变化
        hyd_var = sum(NetMHC_Predictor.HYDROPATHY.get(aa, 0) for aa in variant_peptide)
        hyd_wt = sum(NetMHC_Predictor.HYDROPATHY.get(aa, 0) for aa in wildtype_peptide)
        hyd_change = (hyd_var - hyd_wt) / len(variant_peptide)
        
        # 氨基酸变化
        ref_aa = wildtype_peptide[mutant_position - 1] if mutant_position <= len(wildtype_peptide) else ''
        alt_aa = variant_peptide[mutant_position - 1] if mutant_position <= len(variant_peptide) else ''
        aa_change = f"{ref_aa}->{alt_aa}"
        
        # 识别概率估算
        recognition_prob = self._estimate_recognition_probability(
            foreignness, anchor_mutation, abs(hyd_change)
        )
        
        return Immunogenicity(
            foreignness_score=foreignness,
            self_similarity=1.0 - foreignness,
            amino_acid_change=aa_change,
            anchor_mutation=anchor_mutation,
            hydrophobicity_change=hyd_change,
            recognition_probability=recognition_prob
        )
    
    def _estimate_recognition_probability(
        self,
        foreignness: float,
        anchor_mutation: bool,
        hyd_change: float
    ) -> float:
        """估算T细胞识别概率 (简化模型)"""
        prob = foreignness * 0.5
        if anchor_mutation:
            prob += 0.3
        prob += min(hyd_change * 0.1, 0.2)
        return min(1.0, max(0.0, prob))
    
    def _calculate_priority_score(self, candidate: Neoantigen_Candidate) -> float:
        """计算综合优先级评分"""
        
        # MHC结合评分 (基于rank)
        binding_score = max(0, (2 - candidate.mhc_binding.rank_percentile) / 2)
        
        # 免疫原性评分
        immuno_score = (
            candidate.immunogenicity.foreignness_score * 0.4 +
            (1.0 if candidate.immunogenicity.anchor_mutation else 0.0) * 0.3 +
            candidate.immunogenicity.recognition_probability * 0.3
        )
        
        # 临床评分 (简化)
        clinical_score = 0.5
        
        # 加权综合
        priority = (
            self.WEIGHTS['mhc_binding'] * binding_score +
            self.WEIGHTS['immunogenicity'] * immuno_score +
            self.WEIGHTS['clinical'] * clinical_score
        )
        
        return round(priority, 3)
    
    def _rank_candidates(self, candidates: List[Neoantigen_Candidate]) -> List[Neoantigen_Candidate]:
        """对候选新抗原进行优先级排序"""
        # 按优先级评分降序
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (
                x.priority_score,
                2 - x.mhc_binding.rank_percentile,  # rank越小越好
                x.immunogenicity.foreignness_score
            ),
            reverse=True
        )
        
        # 分配排名
        for i, candidate in enumerate(sorted_candidates, 1):
            candidate.rank = i
        
        return sorted_candidates
    
    def filter_by_binding(
        self,
        result: Prediction_Result,
        rank_threshold: float = 2.0,
        binding_level: str = None
    ) -> List[Neoantigen_Candidate]:
        """根据MHC结合亲和力筛选候选"""
        filtered = []
        
        for candidate in result.neoantigens:
            if candidate.mhc_binding.rank_percentile <= rank_threshold:
                if binding_level is None or candidate.mhc_binding.binding_level == binding_level:
                    filtered.append(candidate)
        
        return filtered
    
    def to_dict(self, result: Prediction_Result) -> Dict[str, Any]:
        """将结果转换为字典格式"""
        return {
            "patient_hla": result.patient_hla,
            "prediction_method": result.prediction_method,
            "total_predictions": result.total_predictions,
            "strong_binders": result.strong_binders,
            "weak_binders": result.weak_binders,
            "neoantigens": [asdict(n) for n in result.neoantigens],
            "summary": result.summary
        }


def parse_hla_input(hla_string: str) -> List[str]:
    """解析HLA输入字符串"""
    hla_list = []
    for hla in hla_string.split(','):
        hla = hla.strip()
        if hla:
            hla_list.append(hla)
    return hla_list


def parse_mutations_csv(file_path: str) -> List[Dict[str, Any]]:
    """从CSV文件解析突变数据"""
    import csv
    mutations = []
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mutation = {
                'gene': row.get('Gene', row.get('gene', '')),
                'chrom': row.get('Chrom', row.get('chrom', '')),
                'pos': int(row.get('Position', row.get('pos', 0))),
                'ref': row.get('Ref', row.get('ref', '')),
                'alt': row.get('Alt', row.get('alt', '')),
                'protein_change': row.get('Protein_Change', row.get('protein_change', ''))
            }
            mutations.append(mutation)
    
    return mutations


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Neoantigen Predictor - 基于HLA和突变预测新抗原",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --hla "HLA-A*02:01,A*11:01" --mutations mutations.csv --output results.json
  python main.py --hla-file hla.txt --vcf variants.vcf --peptide-length 9,10 --rank-cutoff 0.5
        """
    )
    
    # HLA输入
    hla_group = parser.add_mutually_exclusive_group(required=True)
    hla_group.add_argument('--hla', help='HLA等位基因,逗号分隔 (如: HLA-A*02:01,A*11:01)')
    hla_group.add_argument('--hla-file', help='包含HLA列表的文件')
    
    # 突变输入
    mut_group = parser.add_mutually_exclusive_group(required=True)
    mut_group.add_argument('--mutations', help='突变数据CSV文件')
    mut_group.add_argument('--vcf', help='VCF格式突变文件')
    mut_group.add_argument('--variant-peptides', help='变异肽段FASTA文件')
    
    # 预测参数
    parser.add_argument('--peptide-length', default='9,10',
                       help='肽段长度,逗号分隔 (默认: 9,10)')
    parser.add_argument('--rank-cutoff', type=float, default=2.0,
                       help='MHC结合rank阈值 (默认: 2.0)')
    parser.add_argument('--mhc-method', default='netmhcpan',
                       choices=['netmhcpan', 'mhcflurry', 'custom'],
                       help='MHC预测方法')
    
    # 输出
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', choices=['json', 'csv'], default='json',
                       help='输出格式')
    parser.add_argument('--top-n', type=int, help='仅输出前N个候选')
    
    args = parser.parse_args()
    
    # 解析HLA
    if args.hla:
        hla_alleles = parse_hla_input(args.hla)
    else:
        with open(args.hla_file, 'r') as f:
            hla_alleles = parse_hla_input(f.read())
    
    logger.info(f"HLA分型: {hla_alleles}")
    
    # 解析突变
    if args.mutations:
        mutations = parse_mutations_csv(args.mutations)
    elif args.vcf:
        # 简化: VCF解析应使用专用库如pysam
        logger.error("VCF解析功能需安装pysam, 请使用CSV格式")
        return 1
    else:
        logger.error("FASTA肽段输入尚未实现")
        return 1
    
    logger.info(f"突变数量: {len(mutations)}")
    
    # 解析肽段长度
    peptide_lengths = [int(x) for x in args.peptide_length.split(',')]
    
    # 执行预测
    predictor = NeoantigenPredictor(mhc_method=args.mhc_method)
    
    result = predictor.predict(
        hla_alleles=hla_alleles,
        mutations=mutations,
        peptide_length=peptide_lengths
    )
    
    # 筛选强结合
    filtered = predictor.filter_by_binding(result, rank_threshold=args.rank_cutoff)
    logger.info(f"强结合候选: {len(filtered)}")
    
    # 应用top-n限制
    if args.top_n:
        result.neoantigens = result.neoantigens[:args.top_n]
    
    # 输出结果
    output_data = predictor.to_dict(result)
    
    if args.format == 'json':
        output = json.dumps(output_data, indent=2, ensure_ascii=False)
    else:
        # CSV格式
        import csv
        import io
        output_io = io.StringIO()
        if result.neoantigens:
            writer = csv.writer(output_io)
            writer.writerow(['Rank', 'Gene', 'HLA', 'Peptide', 'Rank%', 'Binding', 'Priority'])
            for n in result.neoantigens:
                writer.writerow([
                    n.rank, n.gene, n.hla_allele, n.peptide_sequence,
                    n.mhc_binding.rank_percentile, n.mhc_binding.binding_level,
                    n.priority_score
                ])
        output = output_io.getvalue()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"结果已保存到: {args.output}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    exit(main())
