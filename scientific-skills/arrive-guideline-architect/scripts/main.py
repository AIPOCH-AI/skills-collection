#!/usr/bin/env python3
"""
ARRIVE Guideline Architect
基于 ARRIVE 2.0 标准设计无可挑剔的动物实验方案

Usage:
    python main.py --interactive          # 交互式实验设计
    python main.py --input file.json      # 从输入文件生成方案
    python main.py --validate file.md     # 验证现有方案合规性
    python main.py --checklist            # 生成 ARRIVE 检查清单
"""

import argparse
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ARRIVEGuidelineArchitect:
    """ARRIVE 2.0 实验方案架构师"""
    
    # ARRIVE 2.0 Essential 10 检查项
    ESSENTIAL_10 = {
        "1. Study Design": {
            "description": "For each experiment, provide brief details of study design including: the number of experimental and control groups; the number of animals per group; and a clear statement of whether the experiment was performed blinded.",
            "checkpoints": [
                "明确实验组和对照组数量",
                "明确每组动物数量",
                "说明是否采用盲法"
            ]
        },
        "2. Sample Size": {
            "description": "Provide details of sample size calculation, including: the effect size of interest; the estimate of variability; the power; and the significance level.",
            "checkpoints": [
                "效应量估计 (effect size)",
                "变异度估计 (variability)",
                "检验效能 (power, 通常≥80%)",
                "显著性水平 (significance level, 通常α=0.05)"
            ]
        },
        "3. Inclusion/Exclusion Criteria": {
            "description": "Provide details of inclusion and exclusion criteria for experimental units, including handling of any data exclusions.",
            "checkpoints": [
                "明确的纳入标准",
                "明确的排除标准",
                "数据排除的处理方式"
            ]
        },
        "4. Randomisation": {
            "description": "Provide details of: the randomisation method used to allocate experimental units to groups; and the randomisation method used to determine the order of treatments and measurements.",
            "checkpoints": [
                "分组随机化方法",
                "治疗和测量顺序的随机化方法",
                "随机化实施细节"
            ]
        },
        "5. Blinding": {
            "description": "Describe who was aware of group allocation at the different stages of the experiment (during the allocation, the conduct of the experiment, the outcome assessment, and the data analysis).",
            "checkpoints": [
                "分组分配阶段：谁知情",
                "实验执行阶段：谁知情",
                "结局评估阶段：谁知情",
                "数据分析阶段：谁知情"
            ]
        },
        "6. Outcome Measures": {
            "description": "Define all outcome measures assessed (primary and secondary), clearly distinguishing between measures assessed as part of the experimental protocol and measures assessed in exploratory analyses.",
            "checkpoints": [
                "主要结局指标定义",
                "次要结局指标定义",
                "区分预设分析与探索性分析"
            ]
        },
        "7. Statistical Methods": {
            "description": "Describe in full how the data were analysed, including all statistical methods applied to the data; and whether assumptions of the statistical approaches were met.",
            "checkpoints": [
                "完整的统计方法描述",
                "假设检验条件验证",
                "多重比较校正方法"
            ]
        },
        "8. Experimental Animals": {
            "description": "Provide full details of the animals used, including: species and strain; sex; age or developmental stage; weight or mass; source (including supplier or breeding centre); and any relevant welfare and housing details.",
            "checkpoints": [
                "物种和品系",
                "性别",
                "年龄或发育阶段",
                "体重/质量",
                "来源（供应商或繁殖中心）",
                "饲养条件和福利"
            ]
        },
        "9. Experimental Procedures": {
            "description": "Provide full details of all procedures carried out on the animals, including: what was done, how it was done, and what was used.",
            "checkpoints": [
                "详细的操作步骤",
                "操作方法和工具",
                "麻醉和镇痛方法",
                "样本采集方法"
            ]
        },
        "10. Results": {
            "description": "Report the results for each analysis carried out, with a measure of precision (e.g., standard error or confidence interval), and include the exact number of experimental units analysed in each group.",
            "checkpoints": [
                "每组的精确数值 (精确到个位)",
                "变异度指标 (SD/SEM/CI)",
                "统计量和P值",
                "效应量及置信区间"
            ]
        }
    }
    
    # Recommended Set (推荐项目)
    RECOMMENDED_SET = {
        "11. Ethical Approval": "提供伦理审批信息，包括机构伦理委员会名称和批准编号",
        "12. Housing and Husbandry": "详细的饲养环境条件（温度、湿度、光照周期、饲养密度等）",
        "13. Animal Care and Monitoring": "动物护理和监测频率，人道终末点设置",
        "14. Adverse Events": "不良事件的定义、监测和处理",
        "15. Data Access": "数据共享和获取声明",
        "16. Conflicts of Interest": "利益冲突声明",
        "17. Funding": "资金来源声明",
        "18. Limitations": "研究局限性说明"
    }
    
    # 常见动物实验类型模板
    STUDY_TEMPLATES = {
        "efficacy": {
            "name": "药效学研究 (Efficacy Study)",
            "description": "评估药物或治疗方案在动物模型中的疗效",
            "typical_groups": ["Sham组", "模型对照组", "阳性对照组", "低剂量组", "中剂量组", "高剂量组"],
            "typical_endpoints": ["疾病活动度评分", "生物标志物", "组织病理学评分"]
        },
        "toxicology": {
            "name": "毒理学研究 (Toxicology Study)",
            "description": "评估化合物的安全性特征",
            "typical_groups": ["溶媒对照组", "低剂量组", "中剂量组", "高剂量组"],
            "typical_endpoints": ["体重", "血液学指标", "临床生化", "脏器重量", "组织病理学"]
        },
        "pharmacokinetics": {
            "name": "药代动力学研究 (PK Study)",
            "description": "评估药物在体内的吸收、分布、代谢、排泄",
            "typical_groups": ["静脉给药组", "口服给药组"],
            "typical_endpoints": ["Cmax", "Tmax", "AUC", "半衰期", "清除率"]
        },
        "behavioral": {
            "name": "行为学研究 (Behavioral Study)",
            "description": "评估动物行为变化",
            "typical_groups": ["对照组", "模型组", "治疗组"],
            "typical_endpoints": ["运动能力", "学习记忆", "焦虑样行为", "抑郁样行为"]
        }
    }
    
    def __init__(self):
        self.protocol_data = {}
    
    def interactive_design(self) -> Dict[str, Any]:
        """交互式实验设计向导"""
        print("=" * 70)
        print("🧬 ARRIVE Guideline Architect - 交互式动物实验设计向导")
        print("=" * 70)
        print("\n本向导将帮助您设计符合 ARRIVE 2.0 标准的动物实验方案。\n")
        
        data = {}
        
        # 基本信息
        print("【第一步】基本信息")
        print("-" * 40)
        data['title'] = input("研究标题: ").strip()
        
        print("\n实验类型选择:")
        for key, template in self.STUDY_TEMPLATES.items():
            print(f"  [{key}] {template['name']}: {template['description']}")
        
        study_type = input("\n请选择实验类型 (默认: efficacy): ").strip() or "efficacy"
        data['study_type'] = study_type
        
        # 动物信息
        print("\n【第二步】实验动物信息 (Item 8)")
        print("-" * 40)
        data['species'] = input("物种 (如: Mus musculus): ").strip() or "Mus musculus"
        data['strain'] = input("品系 (如: C57BL/6J): ").strip()
        data['sex'] = input("性别 (Male/Female/Both): ").strip() or "Male"
        data['age'] = input("年龄/周龄 (如: 8-10周): ").strip() or "8-10周"
        data['weight_range'] = input("体重范围 (如: 20-25g): ").strip() or "20-25g"
        data['source'] = input("动物来源 (供应商或繁殖中心): ").strip() or "SPF级动物中心"
        
        # 实验设计
        print("\n【第三步】实验设计 (Items 1, 2)")
        print("-" * 40)
        
        print("实验组别设置:")
        groups = []
        group_count = int(input("实验组数量 (包含对照组): ").strip() or "3")
        
        for i in range(group_count):
            group_name = input(f"  组 {i+1} 名称: ").strip()
            treatment = input(f"  组 {i+1} 处理方式: ").strip()
            groups.append({"name": group_name, "treatment": treatment})
        data['groups'] = groups
        
        # 样本量
        sample_size = input(f"\n每组动物数量 (默认: 10): ").strip() or "10"
        data['sample_size_per_group'] = int(sample_size)
        data['total_animals'] = data['sample_size_per_group'] * len(groups)
        
        print("\n样本量计算依据:")
        data['effect_size'] = input("  预期效应量 (如: 0.8): ").strip() or "0.8"
        data['power'] = input("  检验效能 (默认: 0.80): ").strip() or "0.80"
        data['alpha'] = input("  显著性水平 α (默认: 0.05): ").strip() or "0.05"
        
        # 随机化和盲法
        print("\n【第四步】随机化与盲法 (Items 4, 5)")
        print("-" * 40)
        data['randomization_method'] = input(
            "随机化方法 (如: 计算机随机数表/随机数字生成器): ").strip() or "计算机随机数生成器"
        data['blinding'] = input("是否采用盲法 (Yes/No): ").strip() or "Yes"
        if data['blinding'].lower() == 'yes':
            data['blinding_details'] = input("盲法实施细节 (谁、何时、如何): ").strip() or "实验操作者和结局评估者均不知晓分组情况"
        
        # 结局指标
        print("\n【第五步】结局指标 (Item 6)")
        print("-" * 40)
        data['primary_endpoint'] = input("主要结局指标: ").strip()
        
        secondary = input("次要结局指标 (用逗号分隔): ").strip()
        data['secondary_endpoints'] = [s.strip() for s in secondary.split(",") if s.strip()]
        
        # 统计分析
        print("\n【第六步】统计方法 (Item 7)")
        print("-" * 40)
        data['statistical_method'] = input(
            "主要统计方法 (如: One-way ANOVA + Tukey's post-hoc): ").strip() or "One-way ANOVA"
        
        # 实验程序
        print("\n【第七步】实验程序 (Item 9)")
        print("-" * 40)
        data['study_duration'] = input("实验周期 (天): ").strip()
        data['dosing_route'] = input("给药途径 (如: 灌胃/腹腔注射/静脉注射): ").strip() or "灌胃"
        data['dosing_frequency'] = input("给药频率 (如: 每日一次/每周三次): ").strip() or "每日一次"
        
        # 伦理
        print("\n【第八步】伦理与福利")
        print("-" * 40)
        data['ethical_approval'] = input("伦理委员会名称: ").strip()
        data['approval_number'] = input("批准编号: ").strip()
        data['housing_conditions'] = input("饲养条件 (如: SPF级, 温度22±2°C, 湿度50±10%): ").strip() or "SPF级环境"
        
        self.protocol_data = data
        return data
    
    def generate_protocol(self, data: Optional[Dict] = None, output_format: str = "markdown") -> str:
        """生成完整实验方案"""
        if data is None:
            data = self.protocol_data
        
        if output_format == "markdown":
            return self._generate_markdown_protocol(data)
        else:
            return self._generate_text_protocol(data)
    
    def _generate_markdown_protocol(self, data: Dict) -> str:
        """生成 Markdown 格式实验方案"""
        md = []
        
        # 标题
        md.append(f"# {data.get('title', '动物实验方案')}")
        md.append(f"\n> 本方案严格遵循 ARRIVE 2.0 指南设计")
        md.append(f"> 生成日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        
        # 1. Study Design
        md.append("## 1. 研究设计 (Study Design)\n")
        md.append(f"**实验类型**: {self.STUDY_TEMPLATES.get(data.get('study_type', 'efficacy'), {}).get('name', '自定义研究')}\n")
        md.append(f"**实验组数**: {len(data.get('groups', []))}")
        md.append(f"**每组动物数**: {data.get('sample_size_per_group', 'N/A')}")
        md.append(f"**总动物数**: {data.get('total_animals', 'N/A')}\n")
        
        md.append("### 实验分组")
        md.append("| 组别 | 处理方式 | 动物数 |")
        md.append("|------|----------|--------|")
        for group in data.get('groups', []):
            md.append(f"| {group.get('name', 'N/A')} | {group.get('treatment', 'N/A')} | {data.get('sample_size_per_group', 'N/A')} |")
        md.append("")
        
        md.append(f"**盲法实施**: {data.get('blinding', 'No')}")
        if data.get('blinding_details'):
            md.append(f"**盲法细节**: {data['blinding_details']}")
        md.append("")
        
        # 2. Sample Size
        md.append("## 2. 样本量计算 (Sample Size)\n")
        md.append("样本量基于以下参数计算:\n")
        md.append(f"- **预期效应量 (Effect size)**: {data.get('effect_size', 'N/A')}")
        md.append(f"- **检验效能 (Power, 1-β)**: {data.get('power', '0.80')}")
        md.append(f"- **显著性水平 (α)**: {data.get('alpha', '0.05')}")
        md.append(f"- **最终每组动物数**: {data.get('sample_size_per_group', 'N/A')} (考虑10%脱落率)\n")
        
        # 3. Inclusion/Exclusion
        md.append("## 3. 纳入与排除标准 (Inclusion/Exclusion Criteria)\n")
        md.append("### 纳入标准")
        md.append(f"- 物种: {data.get('species', 'N/A')}")
        md.append(f"- 品系: {data.get('strain', 'N/A')}")
        md.append(f"- 性别: {data.get('sex', 'N/A')}")
        md.append(f"- 年龄: {data.get('age', 'N/A')}")
        md.append(f"- 体重范围: {data.get('weight_range', 'N/A')}")
        md.append("- 健康状态: 无可见疾病体征\n")
        
        md.append("### 排除标准")
        md.append("- 实验前出现异常健康状况")
        md.append("- 给药期间意外死亡（需进行尸检）")
        md.append("- 样本采集失败\n")
        
        # 4. Randomisation
        md.append("## 4. 随机化方案 (Randomisation)\n")
        md.append(f"**随机化方法**: {data.get('randomization_method', '计算机随机数生成器')}")
        md.append("- 动物按体重分层后随机分配至各组")
        md.append("- 使用SPSS/R/Python生成随机数字")
        md.append("- 随机化由独立于实验操作的人员执行\n")
        
        # 5. Blinding
        md.append("## 5. 盲法 (Blinding)\n")
        if data.get('blinding', 'No').lower() == 'yes':
            md.append("| 阶段 | 知情人员 | 说明 |")
            md.append("|------|----------|------|")
            md.append("| 分组分配 | 仅随机化执行者 | 分配方案密封保存 |")
            md.append("| 实验操作 | 操作者不知情 | 药物编号处理 |")
            md.append("| 结局评估 | 评估者不知情 | 独立评估 |")
            md.append("| 数据分析 | 分析者不知情 | 按组别编码分析 |")
        else:
            md.append("本实验采用开放标签设计，不设盲法。")
        md.append("")
        
        # 6. Outcome Measures
        md.append("## 6. 结局指标 (Outcome Measures)\n")
        md.append(f"**主要结局指标**: {data.get('primary_endpoint', 'N/A')}")
        md.append("\n**次要结局指标**:")
        for endpoint in data.get('secondary_endpoints', []):
            md.append(f"- {endpoint}")
        md.append("")
        
        # 7. Statistical Methods
        md.append("## 7. 统计方法 (Statistical Methods)\n")
        md.append(f"**主要分析方法**: {data.get('statistical_method', 'One-way ANOVA')}")
        md.append("- 正态性检验: Shapiro-Wilk test")
        md.append("- 方差齐性检验: Levene's test")
        md.append("- 多重比较校正: Tukey's HSD 或 Bonferroni")
        md.append("- 显著性水平: α = 0.05 (双侧)")
        md.append("- 软件: GraphPad Prism 9.0 或 SPSS 26.0\n")
        
        # 8. Experimental Animals
        md.append("## 8. 实验动物 (Experimental Animals)\n")
        md.append(f"| 参数 | 详情 |")
        md.append(f"|------|------|")
        md.append(f"| 物种 | {data.get('species', 'N/A')} |")
        md.append(f"| 品系 | {data.get('strain', 'N/A')} |")
        md.append(f"| 性别 | {data.get('sex', 'N/A')} |")
        md.append(f"| 年龄 | {data.get('age', 'N/A')} |")
        md.append(f"| 体重 | {data.get('weight_range', 'N/A')} |")
        md.append(f"| 来源 | {data.get('source', 'N/A')} |")
        md.append(f"| 饲养条件 | {data.get('housing_conditions', 'SPF级')} |")
        md.append("")
        
        # 9. Experimental Procedures
        md.append("## 9. 实验程序 (Experimental Procedures)\n")
        md.append(f"**实验周期**: {data.get('study_duration', 'N/A')} 天")
        md.append(f"**给药途径**: {data.get('dosing_route', 'N/A')}")
        md.append(f"**给药频率**: {data.get('dosing_frequency', 'N/A')}")
        md.append("**样本采集**: 根据实验终点采集血液、组织样本")
        md.append("**安乐死方法**: CO₂ 窒息或过量戊巴比妥钠\n")
        
        md.append("### 实验流程图")
        md.append("```")
        md.append("Day 0: 动物适应 → 随机分组 → 基线测量")
        md.append("Day 1-28: 每日给药 → 体重监测 → 行为观察")
        md.append("Day 28: 终末测量 → 样本采集 → 安乐死")
        md.append("```\n")
        
        # 10. Results (Template)
        md.append("## 10. 预期结果报告模板 (Results)\n")
        md.append("_注: 以下为结果报告模板，实验完成后填写_\n")
        md.append("### 主要结局指标")
        md.append("| 组别 | N | Mean ± SD | 95% CI | P值 (vs 对照) |")
        md.append("|------|---|-----------|--------|---------------|")
        for group in data.get('groups', []):
            md.append(f"| {group.get('name', 'N/A')} | | | | |")
        md.append("")
        
        md.append("### 统计分析")
        md.append("- 正态性检验结果: ")
        md.append("- 方差分析结果: F(df1, df2) = _, P = _")
        md.append("- 事后检验结果: ")
        md.append("- 效应量 (Cohen's d): \n")
        
        # Additional Information
        md.append("## 11. 伦理与福利\n")
        md.append(f"**伦理委员会**: {data.get('ethical_approval', '待填写')}")
        md.append(f"**批准编号**: {data.get('approval_number', '待填写')}")
        md.append("**动物福利**: 实验遵循3R原则，尽量减少动物痛苦和数量")
        md.append("**人道终末点**: 体重下降>20%、严重行为异常、无法进食饮水\n")
        
        # ARRIVE Checklist
        md.append("---\n")
        md.append("# ARRIVE 2.0 合规检查清单\n")
        md.append("| 项目 | 内容 | 是否完成 | 页码 |")
        md.append("|------|------|----------|------|")
        for item, details in self.ESSENTIAL_10.items():
            md.append(f"| {item} | {details['description'][:50]}... | ☐ | |")
        md.append("")
        
        md.append("---\n*本方案由 ARRIVE Guideline Architect 自动生成*")
        
        return "\n".join(md)
    
    def _generate_text_protocol(self, data: Dict) -> str:
        """生成纯文本格式实验方案"""
        return self._generate_markdown_protocol(data).replace('#', '').replace('|', '').replace('-', '')
    
    def generate_checklist(self, format_type: str = "markdown") -> str:
        """生成 ARRIVE 2.0 检查清单"""
        lines = []
        lines.append("# ARRIVE 2.0 Essential 10 检查清单\n")
        lines.append(f"检查日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        
        for item, details in self.ESSENTIAL_10.items():
            lines.append(f"## {item}")
            lines.append(f"描述: {details['description']}\n")
            lines.append("检查要点:")
            for checkpoint in details['checkpoints']:
                lines.append(f"  ☐ {checkpoint}")
            lines.append("")
        
        lines.append("\n# Recommended Set 检查清单\n")
        for item, description in self.RECOMMENDED_SET.items():
            lines.append(f"## {item}")
            lines.append(f"  ☐ {description}\n")
        
        return "\n".join(lines)
    
    def validate_protocol(self, protocol_text: str) -> Dict[str, Any]:
        """验证实验方案是否符合 ARRIVE 2.0 标准"""
        results = {
            "score": 0,
            "max_score": len(self.ESSENTIAL_10),
            "compliance": {},
            "recommendations": []
        }
        
        text_lower = protocol_text.lower()
        
        # 检查 Essential 10 各项
        checks = {
            "1. Study Design": ["group", "design", "blind"],
            "2. Sample Size": ["sample size", "power", "effect size", "significance"],
            "3. Inclusion/Exclusion Criteria": ["inclusion", "exclusion", "criteria"],
            "4. Randomisation": ["random", "allocation"],
            "5. Blinding": ["blind", "mask"],
            "6. Outcome Measures": ["outcome", "primary", "secondary", "endpoint"],
            "7. Statistical Methods": ["statistical", "analysis", "anova", "t-test"],
            "8. Experimental Animals": ["species", "strain", "age", "weight", "source"],
            "9. Experimental Procedures": ["procedure", "treatment", "dosing", "administration"],
            "10. Results": ["result", "mean", "sd", "sem", "confidence interval"]
        }
        
        for item, keywords in checks.items():
            found = any(kw in text_lower for kw in keywords)
            results["compliance"][item] = found
            if found:
                results["score"] += 1
            else:
                results["recommendations"].append(f"缺少 {item} 相关内容")
        
        results["percentage"] = round(results["score"] / results["max_score"] * 100, 1)
        
        return results
    
    def save_protocol(self, content: str, filepath: str):
        """保存方案到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 方案已保存至: {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="ARRIVE Guideline Architect - 基于 ARRIVE 2.0 标准设计动物实验方案"
    )
    parser.add_argument("--interactive", "-i", action="store_true", 
                        help="交互式实验设计向导")
    parser.add_argument("--input", "-in", type=str,
                        help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", type=str, default="protocol.md",
                        help="输出文件路径 (默认: protocol.md)")
    parser.add_argument("--validate", "-v", type=str,
                        help="验证现有方案文件")
    parser.add_argument("--checklist", "-c", action="store_true",
                        help="生成 ARRIVE 2.0 检查清单")
    parser.add_argument("--format", "-f", type=str, default="markdown",
                        choices=["markdown", "text"],
                        help="输出格式")
    
    args = parser.parse_args()
    
    architect = ARRIVEGuidelineArchitect()
    
    if args.checklist:
        # 生成检查清单
        checklist = architect.generate_checklist(args.format)
        architect.save_protocol(checklist, args.output)
        print("\n📋 ARRIVE 2.0 检查清单已生成!")
        
    elif args.validate:
        # 验证现有方案
        try:
            with open(args.validate, 'r', encoding='utf-8') as f:
                protocol_text = f.read()
            
            results = architect.validate_protocol(protocol_text)
            
            print(f"\n{'='*50}")
            print("ARRIVE 2.0 合规性验证报告")
            print(f"{'='*50}")
            print(f"\n合规得分: {results['score']}/{results['max_score']} ({results['percentage']}%)")
            
            print("\n逐项检查结果:")
            for item, compliant in results['compliance'].items():
                status = "✅" if compliant else "❌"
                print(f"  {status} {item}")
            
            if results['recommendations']:
                print("\n改进建议:")
                for rec in results['recommendations']:
                    print(f"  • {rec}")
            else:
                print("\n🎉 恭喜！您的方案符合 ARRIVE 2.0 所有必需项要求！")
                
        except FileNotFoundError:
            print(f"❌ 错误: 找不到文件 {args.validate}")
            sys.exit(1)
            
    elif args.input:
        # 从文件生成方案
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            protocol = architect.generate_protocol(data, args.format)
            architect.save_protocol(protocol, args.output)
            print(f"\n✅ 实验方案已生成: {args.output}")
            
        except FileNotFoundError:
            print(f"❌ 错误: 找不到输入文件 {args.input}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ 错误: 输入文件不是有效的 JSON 格式")
            sys.exit(1)
            
    elif args.interactive:
        # 交互式向导
        data = architect.interactive_design()
        protocol = architect.generate_protocol(data, args.format)
        architect.save_protocol(protocol, args.output)
        
        print(f"\n{'='*50}")
        print("✅ 实验方案设计完成!")
        print(f"{'='*50}")
        print(f"\n文件保存位置: {args.output}")
        print(f"总动物数: {data.get('total_animals', 'N/A')}")
        print(f"实验组数: {len(data.get('groups', []))}")
        print("\n下一步建议:")
        print("  1. 将方案提交给机构伦理委员会审批")
        print("  2. 根据方案进行预实验验证")
        print("  3. 使用 --validate 验证最终方案完整性")
        
    else:
        # 显示帮助
        parser.print_help()
        print("\n💡 提示: 使用 --interactive 启动交互式向导")


if __name__ == "__main__":
    main()
