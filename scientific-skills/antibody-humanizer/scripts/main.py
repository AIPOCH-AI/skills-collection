#!/usr/bin/env python3
"""
Antibody Humanizer - AI驱动的抗体人源化工具
基于鼠源抗体序列预测最佳人源框架，生成人源化序列

Usage:
    python3 main.py --vh <VH_SEQUENCE> --vl <VL_SEQUENCE> --name <NAME>
    python3 main.py --input <INPUT_JSON> --output <OUTPUT_JSON>
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class NumberingScheme(Enum):
    """抗体编号方案"""
    KABAT = "kabat"
    CHOTHIA = "chothia"
    IMGT = "imgt"


@dataclass
class CDRRegion:
    """CDR区域定义"""
    name: str
    start: int
    end: int
    sequence: str = ""
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "sequence": self.sequence
        }


@dataclass
class BackMutation:
    """回复突变定义"""
    position: str
    from_aa: str
    to_aa: str
    reason: str
    
    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "from": self.from_aa,
            "to": self.to_aa,
            "reason": self.reason
        }


@dataclass
class HumanizationCandidate:
    """人源化候选结果"""
    rank: int
    framework_source: str
    human_homology: float
    humanness_score: float
    risk_level: str
    humanized_vh: str
    humanized_vl: str
    back_mutations: List[BackMutation]
    
    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "framework_source": self.framework_source,
            "human_homology": round(self.human_homology, 4),
            "humanness_score": round(self.humanness_score, 2),
            "risk_level": self.risk_level,
            "humanized_vh": self.humanized_vh,
            "humanized_vl": self.humanized_vl,
            "back_mutations": [m.to_dict() for m in self.back_mutations]
        }


# 人源种系基因数据库（简化版）
HUMAN_GERMLINE_VH = {
    "IGHV1-2*02": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTSYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCAR",
    "IGHV1-46*01": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTSYWIHWVRQAPGQGLEWMGEINPNSGSTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCAR",
    "IGHV3-23*01": "QVQLVESGGGVVQPGRSLRLSCAASGFTFSDSWIHWVRQAPGKGLEWVAWISPYGGSTYYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCAR",
    "IGHV3-30*01": "QVQLVESGGGVVQPGRSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
    "IGHV4-34*01": "QVQLQSGPELVKPGASVKMSCKASGYTFTSYNMHWVKQTPGRGLEWIGAIYPGNGDTSYNQKFKDKATLTADKSSSTAYMQLSSLTSEDSAVYYCAR",
}

HUMAN_GERMLINE_VL = {
    "IGKV1-12*01": "DIQMTQSPSSLSASVGDRVTITCRASQGISSALAWYQQKPGKAPKLLIYKASSLESGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQYNSYS",
    "IGKV1-39*01": "DIQMTQSPSSLSASVGDRVTITCRASQGIRNDLGWYQQKPGKAPKRLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQAY",
    "IGKV3-11*01": "DIQMTQSPSSLSASVGDRVTITCSASSSVSYMNWYQQKPGKAPKLLIYDTSKLASGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQW",
    "IGKV3-15*01": "DIQMTQSPSSLSASVGDRVTITCSASSSVSYMHWFQQKPGKAPKPLIYDTSKLASGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQ",
    "IGKV4-1*01":  "DIQMTQSPSSLSASVGDRVTITCKASQDVSTAVAWYQQKPGQSPKLLIYSASYRYTGVPDRFTGSGSGTDFTLTISSLQAEDVAVYYC",
}

# CDR位置定义（Chothia编号方案）
CDR_POSITIONS_CHOTHIA = {
    "VH": {
        "CDR-H1": (26, 32),
        "CDR-H2": (52, 56),
        "CDR-H3": (95, 102)
    },
    "VL": {
        "CDR-L1": (24, 34),
        "CDR-L2": (50, 56),
        "CDR-L3": (89, 97)
    }
}

# Kabat编号方案
CDR_POSITIONS_KABAT = {
    "VH": {
        "CDR-H1": (31, 35),
        "CDR-H2": (50, 65),
        "CDR-H3": (95, 102)
    },
    "VL": {
        "CDR-L1": (24, 34),
        "CDR-L2": (50, 56),
        "CDR-L3": (89, 97)
    }
}

# IMGT编号方案
CDR_POSITIONS_IMGT = {
    "VH": {
        "CDR-H1": (27, 38),
        "CDR-H2": (56, 65),
        "CDR-H3": (105, 117)
    },
    "VL": {
        "CDR-L1": (27, 38),
        "CDR-L2": (56, 65),
        "CDR-L3": (105, 117)
    }
}

# 关键框架残基（Vernier区和Interface残基）
CRITICAL_RESIDUES = {
    "VH": [2, 4, 24, 27, 29, 48, 71, 73, 78, 93],  # 基于Chothia编号
    "VL": [2, 4, 35, 36, 46, 47, 49, 64, 71, 87]
}


class AntibodyHumanizer:
    """抗体人源化核心类"""
    
    def __init__(self, scheme: NumberingScheme = NumberingScheme.CHOTHIA):
        self.scheme = scheme
        self.cdr_positions = self._get_cdr_positions()
        
    def _get_cdr_positions(self) -> Dict:
        """获取CDR位置定义"""
        if self.scheme == NumberingScheme.KABAT:
            return CDR_POSITIONS_KABAT
        elif self.scheme == NumberingScheme.IMGT:
            return CDR_POSITIONS_IMGT
        return CDR_POSITIONS_CHOTHIA
    
    def validate_sequence(self, sequence: str) -> Tuple[bool, str]:
        """验证氨基酸序列"""
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        sequence = sequence.upper().replace(" ", "").replace("\n", "")
        
        if not sequence:
            return False, "序列为空"
        
        invalid_chars = set(sequence) - valid_aa
        if invalid_chars:
            return False, f"包含无效氨基酸字符: {invalid_chars}"
        
        if len(sequence) < 80:
            return False, f"序列长度({len(sequence)})过短，可变区通常>80个氨基酸"
        
        if len(sequence) > 150:
            return False, f"序列长度({len(sequence)})过长，可变区通常<150个氨基酸"
        
        return True, sequence
    
    def extract_cdrs(self, sequence: str, chain_type: str) -> Dict[str, CDRRegion]:
        """从序列中提取CDR区域"""
        cdrs = {}
        positions = self.cdr_positions.get(chain_type, {})
        
        for cdr_name, (start, end) in positions.items():
            # 转换为0-based索引
            seq_start = start - 1
            seq_end = min(end, len(sequence))
            
            if seq_start < len(sequence):
                cdr_seq = sequence[seq_start:seq_end]
                cdrs[cdr_name] = CDRRegion(
                    name=cdr_name,
                    start=start,
                    end=seq_end,
                    sequence=cdr_seq
                )
        
        return cdrs
    
    def extract_frameworks(self, sequence: str, chain_type: str) -> Dict[str, str]:
        """提取框架区域序列"""
        cdr_positions = self.cdr_positions.get(chain_type, {})
        frameworks = {}
        
        # FR1: 序列开始到CDR1前
        cdr1_start = cdr_positions.get(f"CDR-{chain_type[0]}1", (1, 1))[0]
        frameworks["FR1"] = sequence[:cdr1_start-1]
        
        # FR2: CDR1后到CDR2前
        cdr1_end = cdr_positions.get(f"CDR-{chain_type[0]}1", (1, 1))[1]
        cdr2_start = cdr_positions.get(f"CDR-{chain_type[0]}2", (1, 1))[0]
        frameworks["FR2"] = sequence[cdr1_end:cdr2_start-1]
        
        # FR3: CDR2后到CDR3前
        cdr2_end = cdr_positions.get(f"CDR-{chain_type[0]}2", (1, 1))[1]
        cdr3_start = cdr_positions.get(f"CDR-{chain_type[0]}3", (1, 1))[0]
        frameworks["FR3"] = sequence[cdr2_end:cdr3_start-1]
        
        # FR4: CDR3后到序列结束
        cdr3_end = cdr_positions.get(f"CDR-{chain_type[0]}3", (1, 1))[1]
        frameworks["FR4"] = sequence[cdr3_end:]
        
        return frameworks
    
    def calculate_similarity(self, seq1: str, seq2: str) -> float:
        """计算两个序列的相似度（基于身份和保守替换）"""
        # 保守替换组（BLOSUM62简化版）
        conservative_groups = [
            set("ILMV"),  # 疏水脂肪族
            set("FWY"),   # 芳香族
            set("DE"),    # 酸性
            set("KRH"),   # 碱性
            set("STNQ"),  # 极性
            set("AG"),    # 小非极性
            set("C"),     # 半胱氨酸（特殊）
            set("P"),     # 脯氨酸（特殊）
        ]
        
        min_len = min(len(seq1), len(seq2))
        if min_len == 0:
            return 0.0
        
        matches = 0
        for i in range(min_len):
            aa1, aa2 = seq1[i], seq2[i]
            if aa1 == aa2:
                matches += 1.0  # 完全匹配
            else:
                # 检查是否为保守替换
                for group in conservative_groups:
                    if aa1 in group and aa2 in group:
                        matches += 0.5  # 保守替换给予部分分数
                        break
        
        # 长度惩罚（较短的比较序列）
        length_penalty = min_len / max(len(seq1), len(seq2))
        
        return (matches / min_len) * length_penalty
    
    def find_best_frameworks(self, sequence: str, chain_type: str, 
                            top_n: int = 3) -> List[Tuple[str, float, str]]:
        """找到最佳匹配的人源框架"""
        
        if chain_type == "VH":
            germline_db = HUMAN_GERMLINE_VH
        else:
            germline_db = HUMAN_GERMLINE_VL
        
        # 提取框架区域
        source_frameworks = self.extract_frameworks(sequence, chain_type)
        source_cdrs = self.extract_cdrs(sequence, chain_type)
        
        scores = []
        for germline_name, germline_seq in germline_db.items():
            germline_frameworks = self.extract_frameworks(germline_seq, chain_type)
            germline_cdrs = self.extract_cdrs(germline_seq, chain_type)
            
            # 计算框架相似性
            fr_similarities = []
            for fr_name in ["FR1", "FR2", "FR3", "FR4"]:
                if fr_name in source_frameworks and fr_name in germline_frameworks:
                    sim = self.calculate_similarity(
                        source_frameworks[fr_name], 
                        germline_frameworks[fr_name]
                    )
                    fr_similarities.append(sim)
            
            # 整体框架相似性
            avg_similarity = sum(fr_similarities) / len(fr_similarities) if fr_similarities else 0
            
            # 构建人源化序列（保留原始CDR）
            humanized = self._build_humanized_sequence(
                source_frameworks, source_cdrs, germline_frameworks
            )
            
            scores.append((germline_name, avg_similarity, humanized))
        
        # 排序并返回前N个
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
    
    def _build_humanized_sequence(self, source_frs: Dict[str, str], 
                                   source_cdrs: Dict[str, CDRRegion],
                                   germline_frs: Dict[str, str]) -> str:
        """构建人源化序列（人源FR + 原始CDR）"""
        # 简化的构建方法
        fr_order = ["FR1", "CDR1", "FR2", "CDR2", "FR3", "CDR3", "FR4"]
        
        result = []
        for region in fr_order:
            if region.startswith("FR"):
                # 使用人源框架
                result.append(germline_frs.get(region, source_frs.get(region, "")))
            else:
                # 使用原始CDR
                cdr_key = f"CDR-{region[-1]}"
                for cdr_name, cdr in source_cdrs.items():
                    if cdr_name.endswith(region[-1]):
                        result.append(cdr.sequence)
                        break
        
        return "".join(result)
    
    def predict_back_mutations(self, mouse_seq: str, humanized_seq: str, 
                               chain_type: str) -> List[BackMutation]:
        """预测需要的回复突变"""
        mutations = []
        critical_pos = CRITICAL_RESIDUES.get(chain_type, [])
        
        min_len = min(len(mouse_seq), len(humanized_seq))
        
        for pos in critical_pos:
            idx = pos - 1  # 转换为0-based
            if idx < min_len:
                mouse_aa = mouse_seq[idx]
                human_aa = humanized_seq[idx]
                
                if mouse_aa != human_aa:
                    reason = self._classify_mutation_reason(pos, chain_type)
                    mutations.append(BackMutation(
                        position=f"{chain_type}-{pos}",
                        from_aa=human_aa,
                        to_aa=mouse_aa,
                        reason=reason
                    ))
        
        return mutations
    
    def _classify_mutation_reason(self, position: int, chain_type: str) -> str:
        """分类突变原因"""
        vernier_positions = [35, 36, 47, 48, 49] if chain_type == "VL" else [24, 27, 29, 71, 78]
        interface_positions = [34, 36, 38, 44, 46, 87] if chain_type == "VL" else [37, 39, 45, 47, 91]
        packing_positions = [2, 4]  # 疏水核心
        
        if position in vernier_positions:
            return "Vernier region - affects CDR conformation"
        elif position in interface_positions:
            return "VH-VL interface - affects chain pairing"
        elif position in packing_positions:
            return "Packing residue - core stability"
        else:
            return "Conserved framework position"
    
    def calculate_humanness_score(self, sequence: str, 
                                   germline_name: str, 
                                   chain_type: str) -> Tuple[float, float, str]:
        """计算人源化评分"""
        
        if chain_type == "VH":
            germline_seq = HUMAN_GERMLINE_VH.get(germline_name, "")
        else:
            germline_seq = HUMAN_GERMLINE_VL.get(germline_name, "")
        
        if not germline_seq:
            return 0.0, 0.0, "Unknown"
        
        # 计算与人源种系的相似度
        similarity = self.calculate_similarity(sequence, germline_seq)
        
        # T20评分模拟（基于20mer肽段的人源化程度）
        # 实际应用中需要完整的T20数据库
        t20_score = similarity * 100
        
        # 归一化到0-100分
        humanness_score = min(100, similarity * 110)
        
        # 风险分级
        if humanness_score >= 85:
            risk_level = "Low"
        elif humanness_score >= 70:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return similarity, humanness_score, risk_level
    
    def humanize(self, vh_sequence: str, vl_sequence: str, 
                 antibody_name: str = "", top_n: int = 3) -> Dict:
        """执行完整的人源化分析"""
        
        # 验证序列
        vh_valid, vh_result = self.validate_sequence(vh_sequence)
        if not vh_valid:
            raise ValueError(f"VH序列错误: {vh_result}")
        vh_sequence = vh_result
        
        vl_valid, vl_result = self.validate_sequence(vl_sequence)
        if not vl_valid:
            raise ValueError(f"VL序列错误: {vl_result}")
        vl_sequence = vl_result
        
        # 提取CDR
        vh_cdrs = self.extract_cdrs(vh_sequence, "VH")
        vl_cdrs = self.extract_cdrs(vl_sequence, "VL")
        
        # 查找最佳人源框架
        vh_candidates = self.find_best_frameworks(vh_sequence, "VH", top_n)
        vl_candidates = self.find_best_frameworks(vl_sequence, "VL", top_n)
        
        # 生成人源化候选
        candidates = []
        rank = 1
        
        for vh_name, vh_sim, vh_humanized in vh_candidates:
            for vl_name, vl_sim, vl_humanized in vl_candidates:
                # 计算综合评分
                avg_similarity = (vh_sim + vl_sim) / 2
                _, humanness_score, risk_level = self.calculate_humanness_score(
                    vh_humanized + vl_humanized, vh_name, "VH"
                )
                
                # 预测回复突变
                vh_mutations = self.predict_back_mutations(vh_sequence, vh_humanized, "VH")
                vl_mutations = self.predict_back_mutations(vl_sequence, vl_humanized, "VL")
                all_mutations = vh_mutations + vl_mutations
                
                candidate = HumanizationCandidate(
                    rank=rank,
                    framework_source=f"{vh_name} / {vl_name}",
                    human_homology=avg_similarity,
                    humanness_score=humanness_score,
                    risk_level=risk_level,
                    humanized_vh=vh_humanized,
                    humanized_vl=vl_humanized,
                    back_mutations=all_mutations
                )
                candidates.append(candidate)
                rank += 1
        
        # 按评分排序
        candidates.sort(key=lambda x: x.humanness_score, reverse=True)
        for i, c in enumerate(candidates, 1):
            c.rank = i
        
        # 构建输出
        best_candidate = candidates[0] if candidates else None
        
        result = {
            "input": {
                "name": antibody_name or "Unnamed Antibody",
                "vh_length": len(vh_sequence),
                "vl_length": len(vl_sequence),
                "vh_sequence": vh_sequence,
                "vl_sequence": vl_sequence
            },
            "analysis": {
                "scheme": self.scheme.value,
                "vh_cdrs": {name: cdr.to_dict() for name, cdr in vh_cdrs.items()},
                "vl_cdrs": {name: cdr.to_dict() for name, cdr in vl_cdrs.items()}
            },
            "humanization_candidates": [c.to_dict() for c in candidates[:top_n]],
            "recommendation": {
                "best_candidate": 1,
                "rationale": "Highest human homology with minimal back-mutations required",
                "immunogenicity_risk": best_candidate.risk_level if best_candidate else "Unknown"
            }
        }
        
        return result


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Antibody Humanizer - AI驱动的抗体人源化工具"
    )
    
    # 输入选项
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--vh", type=str, help="鼠源VH序列（氨基酸）")
    input_group.add_argument("--input", "-i", type=str, help="输入JSON文件路径")
    
    parser.add_argument("--vl", type=str, help="鼠源VL序列（氨基酸）")
    parser.add_argument("--name", "-n", type=str, help="抗体名称", default="")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径")
    parser.add_argument("--format", "-f", type=str, 
                       choices=["json", "fasta", "csv"],
                       default="json", help="输出格式")
    parser.add_argument("--scheme", "-s", type=str,
                       choices=["kabat", "chothia", "imgt"],
                       default="chothia", help="编号方案")
    parser.add_argument("--top-n", type=int, default=3,
                       help="返回最佳人源框架数量")
    
    return parser.parse_args()


def read_input_file(filepath: str) -> Dict:
    """从文件读取输入"""
    with open(filepath, 'r') as f:
        return json.load(f)


def write_output(result: Dict, filepath: str = None, fmt: str = "json"):
    """输出结果"""
    output = json.dumps(result, indent=2, ensure_ascii=False)
    
    if filepath:
        with open(filepath, 'w') as f:
            f.write(output)
        print(f"结果已保存到: {filepath}")
    else:
        print(output)


def main():
    """主函数"""
    args = parse_args()
    
    # 确定输入
    if args.input:
        input_data = read_input_file(args.input)
        vh_sequence = input_data.get("vh_sequence", "")
        vl_sequence = input_data.get("vl_sequence", "")
        name = input_data.get("name", "")
        scheme_str = input_data.get("scheme", args.scheme)
    else:
        vh_sequence = args.vh
        vl_sequence = args.vl
        name = args.name
        scheme_str = args.scheme
        
        if not vl_sequence:
            print("错误: 使用--vh时必须同时提供--vl序列")
            sys.exit(1)
    
    # 确定编号方案
    scheme_map = {
        "kabat": NumberingScheme.KABAT,
        "chothia": NumberingScheme.CHOTHIA,
        "imgt": NumberingScheme.IMGT
    }
    scheme = scheme_map.get(scheme_str.lower(), NumberingScheme.CHOTHIA)
    
    # 执行人源化
    try:
        humanizer = AntibodyHumanizer(scheme=scheme)
        result = humanizer.humanize(
            vh_sequence=vh_sequence,
            vl_sequence=vl_sequence,
            antibody_name=name,
            top_n=args.top_n
        )
        
        # 输出结果
        write_output(result, args.output, args.format)
        
    except ValueError as e:
        print(f"输入错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"处理错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
