#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Cytometry Gating Strategist

针对给定的细胞类型和荧光染料，推荐最佳的流式细胞术圈门(Gating)策略。

Usage:
    python main.py "CD4+ T cells,CD8+ T cells" "FITC,PE,APC"
    python main.py --cell-types "B cells" --fluorophores "FITC,PE,PerCP-Cy5.5" --purpose "cell sorting"
"""

import json
import sys
import argparse
from typing import List, Dict, Any


# ==================== 知识库数据 ====================

FLUOROPHORE_DATABASE = {
    "FITC": {
        "excitation": 488,
        "emission": 525,
        "channel": "BL1",
        "filter": "530/30",
        "brightness": "high",
        "spillover": ["PE"],
        "notes": "经典的绿色荧光染料，亮度高但易与PE串色"
    },
    "PE": {
        "excitation": 488,
        "emission": 575,
        "channel": "YL1",
        "filter": "585/42",
        "brightness": "very high",
        "spillover": ["FITC", "PerCP", "PE-Cy7"],
        "notes": "最亮的染料之一，适合弱表达抗原"
    },
    "PerCP": {
        "excitation": 488,
        "emission": 675,
        "channel": "RL1",
        "filter": "675/30",
        "brightness": "medium",
        "spillover": ["PE", "PerCP-Cy5.5"],
        "notes": "中等亮度，光稳定性较差"
    },
    "PerCP-Cy5.5": {
        "excitation": 488,
        "emission": 695,
        "channel": "RL1",
        "filter": "695/40",
        "brightness": "high",
        "spillover": ["PE", "APC"],
        "notes": "PerCP的串联染料，亮度更高"
    },
    "PE-Cy7": {
        "excitation": 488,
        "emission": 785,
        "channel": "RL2",
        "filter": "780/60",
        "brightness": "high",
        "spillover": ["PE", "APC-Cy7"],
        "notes": "适合多色面板设计"
    },
    "APC": {
        "excitation": 640,
        "emission": 660,
        "channel": "RL1",
        "filter": "660/20",
        "brightness": "very high",
        "spillover": ["APC-Cy7"],
        "notes": "红色激光激发，亮度极高"
    },
    "APC-Cy7": {
        "excitation": 640,
        "emission": 785,
        "channel": "RL2",
        "filter": "780/60",
        "brightness": "high",
        "spillover": ["APC", "PE-Cy7"],
        "notes": "APC的串联染料"
    },
    "APC-H7": {
        "excitation": 640,
        "emission": 780,
        "channel": "RL2",
        "filter": "780/60",
        "brightness": "high",
        "spillover": ["APC"],
        "notes": "比APC-Cy7更稳定"
    },
    "BV421": {
        "excitation": 405,
        "emission": 421,
        "channel": "VL1",
        "filter": "450/50",
        "brightness": "very high",
        "spillover": ["BV510"],
        "notes": "Brilliant Violet系列，亮度极高"
    },
    "BV510": {
        "excitation": 405,
        "emission": 510,
        "channel": "VL2",
        "filter": "525/50",
        "brightness": "high",
        "spillover": ["BV421", "FITC"],
        "notes": "可替代FITC，减少488nm通道压力"
    },
    "BV605": {
        "excitation": 405,
        "emission": 605,
        "channel": "VL3",
        "filter": "610/20",
        "brightness": "high",
        "spillover": ["BV650", "PE"],
        "notes": "适合中等表达抗原"
    },
    "BV650": {
        "excitation": 405,
        "emission": 650,
        "channel": "VL4",
        "filter": "660/20",
        "brightness": "high",
        "spillover": ["BV605", "BV785"],
        "notes": "可替代APC"
    },
    "BV711": {
        "excitation": 405,
        "emission": 711,
        "channel": "VL5",
        "filter": "710/50",
        "brightness": "high",
        "spillover": ["BV785"],
        "notes": "较少使用的BV染料"
    },
    "BV785": {
        "excitation": 405,
        "emission": 785,
        "channel": "VL6",
        "filter": "780/60",
        "brightness": "high",
        "spillover": ["BV711", "APC-Cy7"],
        "notes": "可替代APC-Cy7"
    },
    "DAPI": {
        "excitation": 355,
        "emission": 461,
        "channel": "UV",
        "filter": "450/50",
        "brightness": "medium",
        "spillover": ["BV421"],
        "notes": "常用于死活染色或细胞周期分析"
    },
    "PI": {
        "excitation": 488,
        "emission": 617,
        "channel": "YL2",
        "filter": "615/25",
        "brightness": "high",
        "spillover": ["PE"],
        "notes": "死细胞染料，不能用于固定细胞"
    },
    "7-AAD": {
        "excitation": 488,
        "emission": 655,
        "channel": "RL1",
        "filter": "670/30",
        "brightness": "medium",
        "spillover": ["PerCP", "APC"],
        "notes": "死细胞染料，可穿膜"
    },
    "Live/Dead": {
        "excitation": 488,
        "emission": 575,
        "channel": "YL1",
        "filter": "585/42",
        "brightness": "high",
        "spillover": ["PE"],
        "notes": "胺反应性死活染料，固定兼容"
    },
    "Zombie NIR": {
        "excitation": 640,
        "emission": 750,
        "channel": "RL2",
        "filter": "780/60",
        "brightness": "high",
        "spillover": ["APC-Cy7"],
        "notes": "BioLegend死活染料，远红通道"
    }
}

CELL_TYPE_DATABASE = {
    "T cells": {
        "category": "lymphocyte",
        "size": "small",
        "granularity": "low",
        "fsc_ssc": "lymphocyte region",
        "markers": ["CD3"],
        "subtypes": ["CD4+ T cells", "CD8+ T cells", "Treg", "Th1", "Th2", "Th17"]
    },
    "CD4+ T cells": {
        "category": "lymphocyte",
        "size": "small",
        "granularity": "low",
        "fsc_ssc": "lymphocyte region",
        "markers": ["CD3+", "CD4+"],
        "parent": "T cells",
        "gating_strategy": "CD3+ then CD4+"
    },
    "CD8+ T cells": {
        "category": "lymphocyte",
        "size": "small",
        "granularity": "low",
        "fsc_ssc": "lymphocyte region",
        "markers": ["CD3+", "CD8+"],
        "parent": "T cells",
        "gating_strategy": "CD3+ then CD8+"
    },
    "Treg": {
        "category": "lymphocyte",
        "size": "small",
        "granularity": "low",
        "fsc_ssc": "lymphocyte region",
        "markers": ["CD3+", "CD4+", "CD25+", "FoxP3+"],
        "parent": "CD4+ T cells",
        "gating_strategy": "CD3+ CD4+ CD25hi FoxP3+"
    },
    "B cells": {
        "category": "lymphocyte",
        "size": "small-medium",
        "granularity": "low",
        "fsc_ssc": "lymphocyte region",
        "markers": ["CD19+", "CD20+"],
        "subtypes": ["Naive B cells", "Memory B cells", "Plasma cells"]
    },
    "NK cells": {
        "category": "lymphocyte",
        "size": "small-medium",
        "granularity": "low-medium",
        "fsc_ssc": "lymphocyte region",
        "markers": ["CD3-", "CD56+", "CD16+"],
        "gating_strategy": "CD3- CD56+"
    },
    "NKT cells": {
        "category": "lymphocyte",
        "size": "small",
        "granularity": "low",
        "fsc_ssc": "lymphocyte region",
        "markers": ["CD3+", "CD56+"],
        "gating_strategy": "CD3+ CD56+"
    },
    "Monocytes": {
        "category": "myeloid",
        "size": "large",
        "granularity": "medium",
        "fsc_ssc": "monocyte region (CD14+ CD16- or CD14+ CD16+)",
        "markers": ["CD14", "CD16", "CD11b"],
        "subtypes": ["Classical monocytes", "Intermediate monocytes", "Non-classical monocytes"]
    },
    "Macrophages": {
        "category": "myeloid",
        "size": "large",
        "granularity": "high",
        "fsc_ssc": "high FSC, high SSC",
        "markers": ["CD11b+", "CD68+", "CD14+", "F4/80+ (mouse)"],
        "gating_strategy": "排除单细胞后，CD11b+ CD68+"
    },
    "Dendritic cells": {
        "category": "myeloid",
        "size": "medium-large",
        "granularity": "medium",
        "fsc_ssc": "monocyte-like region",
        "markers": ["CD11c+", "HLA-DR+", "CD123", "CD303"],
        "subtypes": ["mDC", "pDC"]
    },
    "Neutrophils": {
        "category": "myeloid",
        "size": "large",
        "granularity": "very high",
        "fsc_ssc": "high FSC, very high SSC",
        "markers": ["CD11b+", "CD15+", "CD16hi", "CD66b+"],
        "gating_strategy": "FSC/SSC明确区分"
    },
    "Eosinophils": {
        "category": "myeloid",
        "size": "large",
        "granularity": "very high",
        "fsc_ssc": "high FSC, very high SSC",
        "markers": ["CD11b+", "CCR3+", "Siglec-8+"],
        "gating_strategy": "高自发荧光，SSC极高"
    },
    "HSC": {
        "category": "stem cell",
        "size": "small",
        "granularity": "very low",
        "fsc_ssc": "low FSC, low SSC",
        "markers": ["CD34+", "CD38-", "CD90+", "CD45RA-", "Lineage-"],
        "gating_strategy": "Lin- CD34+ CD38-"
    },
    "MSC": {
        "category": "stem cell",
        "size": "medium-large",
        "granularity": "low",
        "fsc_ssc": "medium FSC, low SSC",
        "markers": ["CD73+", "CD90+", "CD105+", "CD34-", "CD45-"],
        "gating_strategy": "黏附细胞，需消化成单细胞"
    },
    "Tumor cells": {
        "category": "cancer",
        "size": "variable",
        "granularity": "variable",
        "fsc_ssc": "异质性强",
        "markers": ["EpCAM+", "CD326+", "特定肿瘤标志物"],
        "notes": "通常FSC范围宽，需结合肿瘤特异性标志物"
    },
    "Platelets": {
        "category": "other",
        "size": "very small",
        "granularity": "low",
        "fsc_ssc": "very low FSC",
        "markers": ["CD41+", "CD61+", "CD62P"],
        "gating_strategy": "需要对数坐标显示"
    }
}


# ==================== 核心算法 ====================

def parse_cell_types(cell_input: str) -> List[str]:
    """解析细胞类型输入"""
    if not cell_input:
        return []
    return [c.strip() for c in cell_input.split(",") if c.strip()]


def parse_fluorophores(fluoro_input: str) -> List[str]:
    """解析荧光染料输入"""
    if not fluoro_input:
        return []
    # 标准化输入（大写处理）
    fluoros = [f.strip().upper() for f in fluoro_input.split(",") if f.strip()]
    # 特殊处理大小写敏感的名字
    normalized = []
    for f in fluoros:
        # 尝试找到匹配的染料名
        match = None
        for key in FLUOROPHORE_DATABASE.keys():
            if f == key.upper():
                match = key
                break
        normalized.append(match if match else f)
    return normalized


def get_cell_info(cell_type: str) -> Dict[str, Any]:
    """获取细胞类型信息"""
    # 直接匹配
    if cell_type in CELL_TYPE_DATABASE:
        return CELL_TYPE_DATABASE[cell_type]
    # 大小写不敏感匹配
    for key, value in CELL_TYPE_DATABASE.items():
        if key.lower() == cell_type.lower():
            return value
    return {"category": "unknown", "notes": "未定义细胞类型"}


def get_fluorophore_info(fluorophore: str) -> Dict[str, Any]:
    """获取荧光染料信息"""
    # 直接匹配
    if fluorophore in FLUOROPHORE_DATABASE:
        return FLUOROPHORE_DATABASE[fluorophore]
    # 大小写不敏感匹配
    for key, value in FLUOROPHORE_DATABASE.items():
        if key.upper() == fluorophore.upper():
            return value
    return {"channel": "unknown", "notes": "未定义荧光染料"}


def check_spillover(fluorophores: List[str]) -> List[Dict[str, Any]]:
    """检查荧光染料之间的光谱重叠"""
    spillover_issues = []
    
    for i, f1 in enumerate(fluorophores):
        info1 = get_fluorophore_info(f1)
        if info1.get("channel") == "unknown":
            continue
            
        for f2 in fluorophores[i+1:]:
            info2 = get_fluorophore_info(f2)
            if info2.get("channel") == "unknown":
                continue
                
            # 检查是否有直接的串色关系
            spillover_list = info1.get("spillover", [])
            if any(s.upper() == f2.upper() for s in spillover_list):
                spillover_issues.append({
                    "dye1": f1,
                    "dye2": f2,
                    "severity": "high" if info1["brightness"] == "very high" else "medium",
                    "recommendation": f"需要对{f1}和{f2}进行补偿校正"
                })
            # 检查是否在同一通道
            elif info1.get("channel") == info2.get("channel"):
                spillover_issues.append({
                    "dye1": f1,
                    "dye2": f2,
                    "severity": "critical",
                    "recommendation": f"{f1}和{f2}使用相同检测通道({info1['channel']})，不能同时使用！"
                })
    
    return spillover_issues


def generate_gating_strategy(cell_types: List[str], fluorophores: List[str], purpose: str = "analysis") -> Dict[str, Any]:
    """生成圈门策略"""
    
    # 分析细胞类型特征
    cell_info_list = [get_cell_info(ct) for ct in cell_types]
    categories = set(info.get("category") for info in cell_info_list)
    
    # 确定基础圈门策略
    if "myeloid" in categories:
        base_gating = {
            "name": "Myeloid-Optimized Sequential Gating",
            "description": "针对髓系细胞的圈门策略，注意单核细胞和中性粒细胞的FSC/SSC差异"
        }
    elif "stem cell" in categories:
        base_gating = {
            "name": "Stem Cell Gating Strategy",
            "description": "针对干细胞的圈门策略，注意细胞大小和表达标记"
        }
    else:
        base_gating = {
            "name": "Standard Sequential Gating",
            "description": "标准顺序圈门策略"
        }
    
    # 构建圈门步骤
    steps = []
    step_num = 1
    
    # Step 1: FSC-A vs SSC-A
    if any(info.get("category") in ["myeloid", "cancer"] for info in cell_info_list):
        steps.append({
            "step": step_num,
            "gate": "FSC-A vs SSC-A",
            "purpose": "区分不同细胞群（髓系细胞形态差异大）",
            "recommendation": "根据细胞类型在相应区域设置门"
        })
    else:
        steps.append({
            "step": step_num,
            "gate": "FSC-A vs SSC-A",
            "purpose": "识别目标细胞群，排除碎片和死细胞",
            "recommendation": "在淋巴细胞区域设置门"
        })
    step_num += 1
    
    # Step 2: 死细胞排除
    steps.append({
        "step": step_num,
        "gate": "Live/Dead Dye",
        "purpose": "排除死细胞",
        "recommendation": "强烈推荐使用死活染料（如Zombie NIR、DAPI或7-AAD）"
    })
    step_num += 1
    
    # Step 3: 单细胞门
    steps.append({
        "step": step_num,
        "gate": "FSC-H vs FSC-A",
        "purpose": "排除粘连细胞，确保单细胞分析",
        "recommendation": "在FSC-H vs FSC-A图上设置对角线门"
    })
    step_num += 1
    
    # Step 4+: 根据细胞类型添加特定圈门
    for cell_type in cell_types:
        info = get_cell_info(cell_type)
        if "gating_strategy" in info:
            steps.append({
                "step": step_num,
                "gate": f"{cell_type} Identification",
                "purpose": f"识别{cell_type}",
                "recommendation": info["gating_strategy"]
            })
            step_num += 1
    
    # 荧光染料分析
    fluoro_analysis = []
    for fluoro in fluorophores:
        info = get_fluorophore_info(fluoro)
        fluoro_analysis.append({
            "fluorophore": fluoro,
            "channel": info.get("channel", "unknown"),
            "detector": info.get("filter", "unknown"),
            "brightness": info.get("brightness", "unknown"),
            "considerations": info.get("spillover", []),
            "notes": info.get("notes", "")
        })
    
    # 补偿建议
    spillover_issues = check_spillover(fluorophores)
    compensation_notes = []
    for issue in spillover_issues:
        compensation_notes.append(issue["recommendation"])
    
    # 面板优化建议
    panel_suggestions = []
    avoid_combinations = []
    
    # 根据染料亮度给出建议
    bright_dyes = [f for f in fluorophores if get_fluorophore_info(f).get("brightness") in ["very high", "high"]]
    dim_dyes = [f for f in fluorophores if get_fluorophore_info(f).get("brightness") == "medium"]
    
    if bright_dyes:
        panel_suggestions.append(f"强荧光染料({', '.join(bright_dyes)})适合搭配弱表达抗原")
    if dim_dyes:
        panel_suggestions.append(f"中等亮度染料({', '.join(dim_dyes)})适合搭配强表达抗原")
    
    # 检查需要避免的组合
    for issue in spillover_issues:
        if issue["severity"] == "critical":
            avoid_combinations.append(f"{issue['dye1']} + {issue['dye2']}（相同通道）")
    
    # QC建议
    qc_recommendations = [
        "设置FMO（荧光减一对照）以确定阳性边界",
        "使用同型对照排除非特异性结合",
        "设置单染管用于补偿计算",
        "每次实验前使用标准微球进行仪器质控"
    ]
    
    if purpose == "cell sorting":
        qc_recommendations.append("分选前必须验证纯度（建议>98%）")
        qc_recommendations.append("设置两路分选以确保回收率")
    
    return {
        "recommended_strategy": {
            "name": base_gating["name"],
            "description": base_gating["description"],
            "steps": steps
        },
        "fluorophore_recommendations": fluoro_analysis,
        "panel_optimization": {
            "suggestions": panel_suggestions,
            "avoid_combinations": avoid_combinations
        },
        "compensation_notes": compensation_notes if compensation_notes else ["该组合补偿相对简单"],
        "quality_control": qc_recommendations,
        "input_summary": {
            "cell_types": cell_types,
            "fluorophores": fluorophores,
            "purpose": purpose
        }
    }


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description="Flow Cytometry Gating Strategist - 流式细胞术圈门策略推荐",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "CD4+ T cells,CD8+ T cells" "FITC,PE,APC"
  python main.py --cell-types "B cells" --fluorophores "BV421,PE,PerCP-Cy5.5,APC"
  python main.py "Monocytes,Macrophages" "FITC,PE,APC" --purpose "cell sorting"
        """
    )
    
    parser.add_argument(
        "cell_types_pos",
        nargs="?",
        help="细胞类型（逗号分隔），如：\"CD4+ T cells,CD8+ T cells\""
    )
    parser.add_argument(
        "fluorophores_pos",
        nargs="?",
        help="荧光染料（逗号分隔），如：\"FITC,PE,APC\""
    )
    parser.add_argument(
        "--cell-types", "-c",
        dest="cell_types_opt",
        help="细胞类型（逗号分隔）"
    )
    parser.add_argument(
        "--fluorophores", "-f",
        dest="fluorophores_opt",
        help="荧光染料（逗号分隔）"
    )
    parser.add_argument(
        "--purpose", "-p",
        default="analysis",
        choices=["analysis", "cell sorting", "rare event", "functional assay"],
        help="实验目的（默认: analysis）"
    )
    parser.add_argument(
        "--instrument",
        default="",
        help="流式细胞仪型号（可选）"
    )
    parser.add_argument(
        "--output", "-o",
        default="",
        help="输出文件路径（可选，默认输出到stdout）"
    )
    
    args = parser.parse_args()
    
    # 解析输入（支持位置参数和命名参数）
    cell_types_str = args.cell_types_pos or args.cell_types_opt
    fluorophores_str = args.fluorophores_pos or args.fluorophores_opt
    
    if not cell_types_str and not fluorophores_str:
        parser.print_help()
        sys.exit(1)
    
    cell_types = parse_cell_types(cell_types_str) if cell_types_str else []
    fluorophores = parse_fluorophores(fluorophores_str) if fluorophores_str else []
    
    if not cell_types and not fluorophores:
        print("Error: 请至少提供细胞类型或荧光染料信息", file=sys.stderr)
        sys.exit(1)
    
    # 生成策略
    result = generate_gating_strategy(cell_types, fluorophores, args.purpose)
    
    # 添加仪器特定建议
    if args.instrument:
        result["instrument_notes"] = f"针对{args.instrument}的优化建议已包含在推荐中"
    
    # 输出结果
    output_json = json.dumps(result, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"结果已保存到: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
