#!/usr/bin/env python3
"""
Translational Gap Analyzer (ID: 209)
评估基础研究模型与人类疾病之间的转化鸿沟
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class DimensionScore:
    """各维度的评分和关注点"""
    score: float  # 0-10, 越高表示差距越大
    concerns: List[str]
    details: Dict[str, any]


@dataclass
class GapAnalysisReport:
    """转化鸿沟分析报告"""
    model: str
    disease: str
    overall_gap_score: float
    risk_level: str
    dimensions: Dict[str, DimensionScore]
    clinical_failure_predictors: List[str]
    recommendations: List[str]


# 知识库：模型-疾病差距数据
TRANSLATIONAL_KNOWLEDGE = {
    "mouse": {
        "anatomy": {
            "brain_structure": 7.5,
            "organ_size_ratio": 6.0,
            "vascular_pattern": 7.0,
            "immune_organs": 5.5
        },
        "physiology": {
            "lifespan": 9.0,
            "heart_rate": 8.0,
            "body_temperature": 7.5,
            "reproductive_cycle": 8.5
        },
        "metabolism": {
            "drug_clearance": 8.0,
            "cytochrome_p450": 7.5,
            "glucose_metabolism": 6.5,
            "lipid_metabolism": 6.0
        },
        "immune": {
            "innate_immunity": 6.0,
            "adaptive_immunity": 5.5,
            "cytokine_profile": 7.0,
            "microglia_function": 8.5
        },
        "genetics": {
            "gene_conservation": 4.0,
            "regulatory_elements": 7.0,
            "chromosome_structure": 6.5,
            "splice_variants": 7.5
        },
        "behavior": {
            "cognitive_assessment": 8.0,
            "social_behavior": 7.5,
            "motor_function": 5.0,
            "pain_perception": 7.0
        }
    },
    "rat": {
        "anatomy": {
            "brain_structure": 6.5,
            "organ_size_ratio": 5.5,
            "vascular_pattern": 6.0,
            "immune_organs": 5.0
        },
        "physiology": {
            "lifespan": 8.5,
            "heart_rate": 7.5,
            "body_temperature": 7.0,
            "reproductive_cycle": 7.5
        },
        "metabolism": {
            "drug_clearance": 7.5,
            "cytochrome_p450": 7.0,
            "glucose_metabolism": 6.0,
            "lipid_metabolism": 5.5
        },
        "immune": {
            "innate_immunity": 5.5,
            "adaptive_immunity": 5.0,
            "cytokine_profile": 6.5,
            "microglia_function": 7.5
        },
        "genetics": {
            "gene_conservation": 4.5,
            "regulatory_elements": 6.5,
            "chromosome_structure": 6.0,
            "splice_variants": 7.0
        },
        "behavior": {
            "cognitive_assessment": 7.0,
            "social_behavior": 6.5,
            "motor_function": 4.5,
            "pain_perception": 6.5
        }
    },
    "zebrafish": {
        "anatomy": {
            "brain_structure": 8.5,
            "organ_structure": 8.0,
            "vascular_pattern": 7.0,
            "immune_organs": 8.5
        },
        "physiology": {
            "water_vs_air": 9.0,
            "temperature_regulation": 9.0,
            "reproduction": 8.5,
            "regeneration": 7.0
        },
        "metabolism": {
            "drug_metabolism": 8.5,
            "energy_metabolism": 7.5,
            "xenobiotic_metabolism": 8.0
        },
        "immune": {
            "adaptive_immunity": 9.0,
            "innate_immunity": 7.0,
            "inflammation": 7.5
        },
        "genetics": {
            "gene_duplication": 8.5,
            "conservation": 6.0,
            "regeneration_genes": 6.5
        },
        "behavior": {
            "cognitive_assessment": 8.5,
            "social_behavior": 8.0,
            "learning": 8.0
        }
    },
    "cell_line": {
        "anatomy": {
            "tissue_architecture": 9.5,
            "cell_interactions": 9.0,
            "extracellular_matrix": 8.5,
            "3d_structure": 9.0
        },
        "physiology": {
            "systemic_regulation": 10.0,
            "homeostasis": 9.5,
            "stress_response": 7.0
        },
        "metabolism": {
            "culture_medium_effects": 8.5,
            "oxygen_levels": 8.0,
            "nutrient_availability": 7.5
        },
        "immune": {
            "immune_interactions": 9.5,
            "inflammation_context": 9.0
        },
        "genetics": {
            "genetic_drift": 8.0,
            "passage_effects": 8.5,
            "mutation_accumulation": 8.0
        }
    },
    "organoid": {
        "anatomy": {
            "maturation": 7.5,
            "vascularization": 9.0,
            "size_limitations": 8.5,
            "cell_diversity": 6.5
        },
        "physiology": {
            "systemic_integration": 9.5,
            "maturity_level": 7.5,
            "functionality": 7.0
        },
        "metabolism": {
            "nutrient_diffusion": 8.0,
            "waste_removal": 8.5,
            "metabolic_activity": 6.5
        },
        "immune": {
            "immune_component": 8.5,
            "inflammation_modeling": 7.5
        },
        "genetics": {
            "genetic_stability": 6.0,
            "patient_variability": 5.5
        }
    },
    "primate": {
        "anatomy": {
            "brain_structure": 2.5,
            "organ_structure": 3.0,
            "vascular_pattern": 3.5,
            "immune_organs": 3.0
        },
        "physiology": {
            "lifespan": 4.5,
            "reproductive_cycle": 5.0,
            "metabolic_rate": 4.0,
            "body_temperature": 3.0
        },
        "metabolism": {
            "drug_metabolism": 4.5,
            "cytochrome_p450": 4.0,
            "glucose_metabolism": 3.5,
            "lipid_metabolism": 3.5
        },
        "immune": {
            "innate_immunity": 3.5,
            "adaptive_immunity": 3.0,
            "cytokine_profile": 4.0,
            "microglia_function": 3.5
        },
        "genetics": {
            "gene_similarity": 2.5,
            "regulatory_elements": 4.0,
            "chromosome_structure": 3.0
        },
        "behavior": {
            "cognitive_assessment": 4.0,
            "social_behavior": 3.5,
            "emotional_response": 4.5
        }
    }
}


# 疾病特异性风险因素
DISEASE_SPECIFIC_FACTORS = {
    "alzheimer": {
        "mouse": {
            "pathology_differences": ["缺乏自然tau病理", "Aβ沉积模式不同", "神经退行速度差异"],
            "genetic_risks": ["APOE4模型有限", "TREM2功能差异"],
            "immune_factors": ["小胶质细胞反应性不同", "神经炎症模式差异"],
            "drug_targets": ["淀粉样蛋白假说多次失败", "tau病理难以复制"]
        },
        "rat": {
            "pathology_differences": ["tau病理有限", "Aβ清除差异"],
            "genetic_risks": ["APOE模型较少"],
            "behavioral_differences": ["认知评估方法局限"]
        }
    },
    "parkinson": {
        "mouse": {
            "pathology_differences": ["缺乏自然路易体", "多巴胺系统差异"],
            "genetic_risks": ["LRRK2突变效应不同", "SNCA过表达模型局限"],
            "drug_targets": ["多巴胺替代疗法模型有效但临床差异大"]
        },
        "rat": {
            "toxin_models": ["MPTP模型与散发性PD差异大", "6-OHDA模型局限性"],
            "genetic_models": ["遗传模型进展缓慢"]
        }
    },
    "cancer": {
        "mouse": {
            "immune_factors": ["免疫系统差异影响免疫治疗效果", "肿瘤微环境不同"],
            "metabolic_factors": ["药物代谢差异显著", "剂量换算困难"],
            "genetic_risks": ["驱动突变保守但背景不同"]
        },
        "cell_line": {
            "model_limitations": ["缺乏微环境", "2D vs 3D差异", "细胞系演化"]
        }
    },
    "diabetes": {
        "mouse": {
            "metabolic_factors": ["胰岛素抵抗机制差异", "脂肪分布不同"],
            "immune_factors": ["1型糖尿病自身免疫差异", "NOD小鼠局限性"],
            "drug_targets": ["GLP-1类似物相对成功", "SGLT2抑制剂差异"]
        },
        "rat": {
            "metabolic_factors": [" Zucker糖尿病肥胖大鼠与人类T2D差异"]
        }
    },
    "autoimmune": {
        "mouse": {
            "immune_factors": ["免疫耐受机制差异", "MHC系统根本不同"],
            "drug_targets": ["TNF抑制剂相对成功", "B细胞靶向差异"],
            "pathology_differences": ["疾病诱导模型与自发疾病差异"]
        }
    },
    "cardiovascular": {
        "mouse": {
            "anatomical_differences": ["冠状动脉分布不同", "心肌再生能力差异"],
            "physiological_differences": ["心率极快", "心电图解读差异"],
            "drug_targets": ["他汀类药物有效", "抗凝血药物代谢差异"]
        },
        "rat": {
            "advantages": ["心血管手术模型更成熟"],
            "differences": ["仍与临床有显著差异"]
        }
    }
}


def normalize_disease_name(disease: str) -> str:
    """标准化疾病名称"""
    disease_lower = disease.lower().replace("'", "").replace(" ", "_")
    disease_mapping = {
        "alzheimer": "alzheimer",
        "alzheimers": "alzheimer",
        "alzheimers_disease": "alzheimer",
        "parkinson": "parkinson",
        "parkinsons": "parkinson",
        "parkinsons_disease": "parkinson",
        "cancer": "cancer",
        "tumor": "cancer",
        "diabetes": "diabetes",
        "autoimmune": "autoimmune",
        "cardiovascular": "cardiovascular",
        "heart_disease": "cardiovascular"
    }
    return disease_mapping.get(disease_lower, disease_lower)


def get_disease_specific_risks(model: str, disease: str) -> List[str]:
    """获取疾病特异性风险"""
    normalized_disease = normalize_disease_name(disease)
    risks = []
    
    if normalized_disease in DISEASE_SPECIFIC_FACTORS:
        disease_data = DISEASE_SPECIFIC_FACTORS[normalized_disease]
        if model in disease_data:
            model_data = disease_data[model]
            for category, items in model_data.items():
                if isinstance(items, list):
                    risks.extend(items)
    
    return risks


def calculate_dimension_score(model: str, dimension: str, focus_areas: List[str]) -> DimensionScore:
    """计算特定维度的分数"""
    if model not in TRANSLATIONAL_KNOWLEDGE:
        return DimensionScore(score=5.0, concerns=["未知模型类型"], details={})
    
    model_data = TRANSLATIONAL_KNOWLEDGE[model]
    
    if dimension not in model_data:
        return DimensionScore(score=5.0, concerns=["该维度数据不可用"], details={})
    
    dim_data = model_data[dimension]
    scores = list(dim_data.values())
    avg_score = sum(scores) / len(scores) if scores else 5.0
    
    # 识别主要关注点
    concerns = []
    for key, value in dim_data.items():
        if value >= 7.0:
            concerns.append(f"{key}: 显著差异 (评分: {value})")
        elif value >= 5.0:
            concerns.append(f"{key}: 中等差异 (评分: {value})")
    
    # 如果该维度是关注重点，列出更详细的concerns
    if dimension in focus_areas:
        concerns = [f"{k}: {v}" for k, v in dim_data.items() if v >= 5.0]
    
    return DimensionScore(
        score=round(avg_score, 1),
        concerns=concerns[:5],  # 限制数量
        details=dim_data
    )


def determine_risk_level(overall_score: float) -> str:
    """确定风险等级"""
    if overall_score >= 8.0:
        return RiskLevel.CRITICAL.value
    elif overall_score >= 6.5:
        return RiskLevel.HIGH.value
    elif overall_score >= 4.0:
        return RiskLevel.MEDIUM.value
    else:
        return RiskLevel.LOW.value


def generate_failure_predictors(model: str, disease: str, dimensions: Dict[str, DimensionScore]) -> List[str]:
    """生成临床试验失败预测因素"""
    predictors = []
    
    # 基于维度评分识别风险
    high_gap_dims = [dim for dim, score in dimensions.items() if score.score >= 7.0]
    
    if "immune" in high_gap_dims:
        predictors.append("免疫相关机制研究可能存在转化失败风险")
    if "metabolism" in high_gap_dims:
        predictors.append("药物代谢动力学差异可能导致临床剂量不当")
    if "anatomy" in high_gap_dims and model in ["mouse", "rat"]:
        predictors.append("器官结构差异可能影响药物分布")
    if "behavior" in high_gap_dims and "alzheimer" in disease.lower():
        predictors.append("认知评估方法的种间差异可能掩盖真实疗效")
    if "genetics" in high_gap_dims:
        predictors.append("基因调控网络差异可能影响靶点有效性")
    
    # 添加疾病特异性风险
    disease_risks = get_disease_specific_risks(model, disease)
    predictors.extend(disease_risks[:3])  # 最多3个
    
    return predictors if predictors else ["未发现特定的高风险因素，但仍需谨慎评估"]


def generate_recommendations(model: str, disease: str, dimensions: Dict[str, DimensionScore]) -> List[str]:
    """生成改进建议"""
    recommendations = []
    
    # 基于模型类型的建议
    if model == "mouse":
        if dimensions.get("immune", DimensionScore(0, [], {})).score >= 7.0:
            recommendations.append("考虑使用人源化免疫系统小鼠模型")
        if dimensions.get("metabolism", DimensionScore(0, [], {})).score >= 7.0:
            recommendations.append("进行药物代谢的体外人肝细胞验证")
        if dimensions.get("behavior", DimensionScore(0, [], {})).score >= 7.0:
            recommendations.append("增加非人灵长类动物的行为学验证")
        recommendations.append("考虑使用基因人源化小鼠以提高转化相关性")
    
    elif model == "rat":
        recommendations.append("利用大鼠更好的行为学特征进行认知评估")
        if dimensions.get("metabolism", DimensionScore(0, [], {})).score >= 6.0:
            recommendations.append("进行人源化肝微粒体代谢研究")
    
    elif model == "zebrafish":
        recommendations.append("主要用于高通量筛选和发育毒性测试")
        recommendations.append("阳性结果需哺乳动物模型验证")
        recommendations.append("关注心血管和神经发育毒性评估")
    
    elif model == "cell_line":
        recommendations.append("使用3D培养或类器官模型提高生理相关性")
        recommendations.append("结合共培养系统模拟肿瘤微环境")
        recommendations.append("定期验证细胞系身份和遗传稳定性")
    
    elif model == "organoid":
        recommendations.append("关注类器官的成熟度和功能性评估")
        recommendations.append("考虑血管化技术以改善营养供应")
        recommendations.append("结合单细胞测序验证细胞异质性")
    
    elif model == "primate":
        recommendations.append("作为临床前最终验证模型使用")
        recommendations.append("严格遵循3R原则，合理设计实验")
    
    # 疾病特异性建议
    normalized_disease = normalize_disease_name(disease)
    if normalized_disease == "alzheimer":
        recommendations.append("关注Aβ和tau以外的病理机制")
        recommendations.append("重视神经免疫和小胶质细胞研究")
    elif normalized_disease == "cancer":
        recommendations.append("重视肿瘤微环境和免疫治疗评估")
        recommendations.append("考虑患者来源的异种移植模型(PDX)")
    elif normalized_disease == "autoimmune":
        recommendations.append("关注人类特异性免疫靶点")
        recommendations.append("考虑使用人源化免疫系统模型")
    
    return recommendations


def analyze_gap(model: str, disease: str, focus_areas: List[str] = None) -> GapAnalysisReport:
    """执行转化鸿沟分析"""
    if focus_areas is None:
        focus_areas = []
    
    dimensions_to_analyze = focus_areas if focus_areas else [
        "anatomy", "physiology", "metabolism", "immune", "genetics", "behavior"
    ]
    
    dimensions = {}
    total_score = 0
    
    for dim in dimensions_to_analyze:
        dim_score = calculate_dimension_score(model, dim, focus_areas)
        dimensions[dim] = dim_score
        total_score += dim_score.score
    
    overall_score = total_score / len(dimensions) if dimensions else 5.0
    risk_level = determine_risk_level(overall_score)
    
    failure_predictors = generate_failure_predictors(model, disease, dimensions)
    recommendations = generate_recommendations(model, disease, dimensions)
    
    # 转换为可序列化的格式
    serializable_dimensions = {}
    for dim, score in dimensions.items():
        serializable_dimensions[dim] = {
            "score": score.score,
            "concerns": score.concerns,
            "details": score.details
        }
    
    return GapAnalysisReport(
        model=model,
        disease=disease,
        overall_gap_score=round(overall_score, 1),
        risk_level=risk_level,
        dimensions=serializable_dimensions,
        clinical_failure_predictors=failure_predictors,
        recommendations=recommendations
    )


def format_report(report: GapAnalysisReport, output_format: str = "json") -> str:
    """格式化报告输出"""
    if output_format == "json":
        return json.dumps(asdict(report), indent=2, ensure_ascii=False)
    
    elif output_format == "markdown":
        md = f"""# 转化鸿沟分析报告

## 基本信息
- **模型**: {report.model}
- **疾病**: {report.disease}
- **总体差距评分**: {report.overall_gap_score}/10
- **风险等级**: {report.risk_level}

## 各维度评估
"""
        for dim, data in report.dimensions.items():
            md += f"\n### {dim.capitalize()}\n"
            md += f"- **评分**: {data['score']}\n"
            if data['concerns']:
                md += "- **关注点**:\n"
                for concern in data['concerns']:
                    md += f"  - {concern}\n"
        
        md += "\n## 临床试验失败预测因素\n"
        for predictor in report.clinical_failure_predictors:
            md += f"- ⚠️ {predictor}\n"
        
        md += "\n## 改进建议\n"
        for rec in report.recommendations:
            md += f"- 💡 {rec}\n"
        
        return md
    
    else:  # table format
        lines = []
        lines.append("=" * 70)
        lines.append(f"转化鸿沟分析报告 - {report.model} vs {report.disease}")
        lines.append("=" * 70)
        lines.append(f"总体评分: {report.overall_gap_score}/10 | 风险等级: {report.risk_level}")
        lines.append("-" * 70)
        lines.append(f"{'维度':<15} {'评分':<10} {'主要关注点'}")
        lines.append("-" * 70)
        
        for dim, data in report.dimensions.items():
            concerns = "; ".join(data['concerns'][:2]) if data['concerns'] else "无"
            lines.append(f"{dim.capitalize():<15} {data['score']:<10} {concerns}")
        
        lines.append("-" * 70)
        lines.append("\n[临床试验失败风险预警]")
        for i, predictor in enumerate(report.clinical_failure_predictors[:3], 1):
            lines.append(f"  {i}. {predictor}")
        
        lines.append("\n[改进建议]")
        for i, rec in enumerate(report.recommendations[:4], 1):
            lines.append(f"  {i}. {rec}")
        
        return "\n".join(lines)


def compare_models(models: List[str], disease: str, focus_areas: List[str] = None) -> str:
    """对比多个模型"""
    reports = []
    for model in models:
        report = analyze_gap(model, disease, focus_areas)
        reports.append(report)
    
    # 排序：评分越低越好（差距越小）
    reports.sort(key=lambda x: x.overall_gap_score)
    
    output = ["=" * 80]
    output.append(f"多模型对比分析: {disease}")
    output.append("=" * 80)
    output.append(f"{'模型':<15} {'差距评分':<12} {'风险等级':<12} {'推荐排序'}")
    output.append("-" * 80)
    
    for i, report in enumerate(reports, 1):
        output.append(f"{report.model:<15} {report.overall_gap_score:<12} {report.risk_level:<12} #{i}")
    
    output.append("\n" + "=" * 80)
    output.append("详细分析")
    output.append("=" * 80)
    
    for report in reports:
        output.append(f"\n[{report.model.upper()}]")
        output.append(f"风险等级: {report.risk_level} | 关键问题: {', '.join(report.clinical_failure_predictors[:2])}")
        output.append(f"主要建议: {report.recommendations[0] if report.recommendations else 'N/A'}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Translational Gap Analyzer - 评估基础研究模型与人类疾病的转化鸿沟",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --model mouse --disease "Alzheimer's" --full
  python main.py --model mouse --disease "Alzheimer's" --quick
  python main.py --models mouse,rat,primate --disease cancer --compare
  python main.py --model mouse --disease diabetes --focus metabolism,immune
        """
    )
    
    parser.add_argument("--model", type=str, help="模型类型 (mouse, rat, zebrafish, cell_line, organoid, primate)")
    parser.add_argument("--models", type=str, help="多模型对比模式，逗号分隔")
    parser.add_argument("--disease", type=str, required=True, help="疾病名称")
    parser.add_argument("--focus", type=str, help="关注领域，逗号分隔 (anatomy, physiology, metabolism, immune, genetics, behavior)")
    parser.add_argument("--full", action="store_true", help="生成完整评估报告")
    parser.add_argument("--quick", action="store_true", help="快速风险评估模式")
    parser.add_argument("--compare", action="store_true", help="多模型对比模式")
    parser.add_argument("--output", type=str, help="输出文件路径")
    parser.add_argument("--format", type=str, choices=["json", "markdown", "table"], default="table", help="输出格式")
    
    args = parser.parse_args()
    
    # 解析关注领域
    focus_areas = []
    if args.focus:
        focus_areas = [f.strip() for f in args.focus.split(",")]
    
    # 多模型对比模式
    if args.compare or args.models:
        if not args.models:
            print("错误: 对比模式需要 --models 参数", file=sys.stderr)
            sys.exit(1)
        
        models = [m.strip() for m in args.models.split(",")]
        result = compare_models(models, args.disease, focus_areas)
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"对比报告已保存至: {args.output}")
        else:
            print(result)
        return
    
    # 单模型分析模式
    if not args.model:
        print("错误: 单模型分析需要 --model 参数", file=sys.stderr)
        sys.exit(1)
    
    # 执行分析
    report = analyze_gap(args.model, args.disease, focus_areas)
    
    # 确定输出格式
    output_format = args.format
    if args.full:
        output_format = "markdown"
    elif args.quick:
        output_format = "table"
    
    result = format_report(report, output_format)
    
    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"报告已保存至: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
