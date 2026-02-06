#!/usr/bin/env python3
"""
Lab Result Interpretation Tool
Transforms complex biochemical test results into patient-friendly explanations.
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class LabResult:
    """Represents a single lab test result."""
    test_name: str
    value: float
    unit: str
    reference_min: Optional[float] = None
    reference_max: Optional[float] = None
    status: str = "normal"  # normal, low, high, critical
    severity: str = "none"  # none, mild, moderate, severe
    explanation: str = ""
    recommendation: str = ""


class LabResultInterpreter:
    """Interprets lab test results and generates patient-friendly explanations."""
    
    # Common test name mappings (Chinese/English variations)
    TEST_NAME_MAPPINGS = {
        # Blood Routine
        "wbc": "白细胞计数", "白细胞": "白细胞计数", "white blood cell": "白细胞计数",
        "rbc": "红细胞计数", "红细胞": "红细胞计数", "red blood cell": "红细胞计数",
        "hgb": "血红蛋白", "血红蛋白": "血红蛋白", "hemoglobin": "血红蛋白",
        "plt": "血小板计数", "血小板": "血小板计数", "platelet": "血小板计数",
        "hct": "红细胞压积", "红细胞压积": "红细胞压积", "hematocrit": "红细胞压积",
        
        # Lipid Panel
        "tc": "总胆固醇", "总胆固醇": "总胆固醇", "cholesterol": "总胆固醇",
        "ldl": "低密度脂蛋白胆固醇", "ldl-c": "低密度脂蛋白胆固醇", "低密度脂蛋白": "低密度脂蛋白胆固醇",
        "hdl": "高密度脂蛋白胆固醇", "hdl-c": "高密度脂蛋白胆固醇", "高密度脂蛋白": "高密度脂蛋白胆固醇",
        "tg": "甘油三酯", "甘油三酯": "甘油三酯", "triglyceride": "甘油三酯",
        
        # Liver Function
        "alt": "谷丙转氨酶", "谷丙转氨酶": "谷丙转氨酶", "gpt": "谷丙转氨酶",
        "ast": "谷草转氨酶", "谷草转氨酶": "谷草转氨酶", "got": "谷草转氨酶",
        "alp": "碱性磷酸酶", "碱性磷酸酶": "碱性磷酸酶",
        "ggt": "γ-谷氨酰转肽酶", "ggt": "γ-谷氨酰转肽酶",
        "tbil": "总胆红素", "总胆红素": "总胆红素", "bilirubin": "总胆红素",
        "tp": "总蛋白", "总蛋白": "总蛋白", "total protein": "总蛋白",
        "alb": "白蛋白", "白蛋白": "白蛋白", "albumin": "白蛋白",
        
        # Kidney Function
        "crea": "肌酐", "肌酐": "肌酐", "creatinine": "肌酐",
        "bun": "尿素氮", "尿素氮": "尿素氮", "urea": "尿素氮",
        "egfr": "肾小球滤过率", "gfr": "肾小球滤过率",
        "ua": "尿酸", "尿酸": "尿酸", "uric acid": "尿酸",
        
        # Blood Sugar
        "glu": "空腹血糖", "空腹血糖": "空腹血糖", "glucose": "空腹血糖",
        "hba1c": "糖化血红蛋白", "糖化血红蛋白": "糖化血红蛋白",
        
        # Thyroid
        "tsh": "促甲状腺激素", "促甲状腺激素": "促甲状腺激素",
        "t3": "三碘甲状腺原氨酸", "三碘甲状腺原氨酸": "三碘甲状腺原氨酸",
        "t4": "甲状腺素", "甲状腺素": "甲状腺素",
        "ft3": "游离三碘甲状腺原氨酸", "游离三碘甲状腺原氨酸": "游离三碘甲状腺原氨酸",
        "ft4": "游离甲状腺素", "游离甲状腺素": "游离甲状腺素",
        
        # Electrolytes
        "na": "钠", "钠": "钠", "sodium": "钠",
        "k": "钾", "钾": "钾", "potassium": "钾",
        "cl": "氯", "氯": "氯", "chloride": "氯",
        "ca": "钙", "钙": "钙", "calcium": "钙",
        "mg": "镁", "镁": "镁", "magnesium": "镁",
        
        # Inflammation
        "crp": "C反应蛋白", "c反应蛋白": "C反应蛋白",
        "esr": "血沉", "血沉": "血沉", "erythrocyte sedimentation rate": "血沉",
    }
    
    # Standard reference ranges
    REFERENCE_RANGES = {
        "白细胞计数": {"min": 4.0, "max": 10.0, "unit": "10^9/L"},
        "红细胞计数": {"min": 4.0, "max": 5.5, "unit": "10^12/L"},
        "血红蛋白": {"min": 120.0, "max": 160.0, "unit": "g/L"},
        "血小板计数": {"min": 100.0, "max": 300.0, "unit": "10^9/L"},
        "红细胞压积": {"min": 0.40, "max": 0.50, "unit": "L/L"},
        "总胆固醇": {"min": 3.1, "max": 5.7, "unit": "mmol/L"},
        "低密度脂蛋白胆固醇": {"min": 0.0, "max": 3.4, "unit": "mmol/L"},
        "高密度脂蛋白胆固醇": {"min": 1.0, "max": 2.0, "unit": "mmol/L"},
        "甘油三酯": {"min": 0.0, "max": 1.7, "unit": "mmol/L"},
        "谷丙转氨酶": {"min": 0.0, "max": 40.0, "unit": "U/L"},
        "谷草转氨酶": {"min": 0.0, "max": 40.0, "unit": "U/L"},
        "碱性磷酸酶": {"min": 40.0, "max": 150.0, "unit": "U/L"},
        "γ-谷氨酰转肽酶": {"min": 10.0, "max": 60.0, "unit": "U/L"},
        "总胆红素": {"min": 0.0, "max": 21.0, "unit": "μmol/L"},
        "总蛋白": {"min": 60.0, "max": 80.0, "unit": "g/L"},
        "白蛋白": {"min": 35.0, "max": 55.0, "unit": "g/L"},
        "肌酐": {"min": 44.0, "max": 133.0, "unit": "μmol/L"},
        "尿素氮": {"min": 2.6, "max": 7.5, "unit": "mmol/L"},
        "尿酸": {"min": 208.0, "max": 428.0, "unit": "μmol/L"},
        "空腹血糖": {"min": 3.9, "max": 6.1, "unit": "mmol/L"},
        "糖化血红蛋白": {"min": 4.0, "max": 6.0, "unit": "%"},
        "促甲状腺激素": {"min": 0.27, "max": 4.2, "unit": "mIU/L"},
        "钠": {"min": 137.0, "max": 147.0, "unit": "mmol/L"},
        "钾": {"min": 3.5, "max": 5.3, "unit": "mmol/L"},
        "氯": {"min": 99.0, "max": 110.0, "unit": "mmol/L"},
        "钙": {"min": 2.1, "max": 2.6, "unit": "mmol/L"},
        "C反应蛋白": {"min": 0.0, "max": 10.0, "unit": "mg/L"},
    }
    
    def __init__(self):
        self.disclaimer = "\n【免责声明】本解读仅供参考，不能替代专业医疗建议。如有疑问请咨询医生。"
    
    def normalize_test_name(self, name: str) -> str:
        """Normalize test name to standard form."""
        name_lower = name.lower().strip()
        return self.TEST_NAME_MAPPINGS.get(name_lower, name)
    
    def parse_lab_line(self, line: str) -> Optional[LabResult]:
        """Parse a single line of lab result."""
        # Pattern 1: "Name: Value Unit (Ref: Min-Max)" or "Name: Value (Min-Max)" or "Name: Value Unit"
        pattern1 = r"(.+?)[:\s]+([\d.]+)\s*(\S*)?(?:\s*[\(\（]?[^\d]*([\d.]+)?\s*[-~至]\s*([\d.]+)?[^\)]*[\)\）]?)?"
        
        # Pattern 2: "Name Value Unit" (simpler format)
        pattern2 = r"^(.+?)\s+([\d.]+)\s+(\S+)$"
        
        for pattern in [pattern1, pattern2]:
            match = re.search(pattern, line.strip())
            if match:
                groups = match.groups()
                test_name = self.normalize_test_name(groups[0].strip())
                value = float(groups[1])
                unit = groups[2] if groups[2] else ""
                ref_min = float(groups[3]) if groups[3] else None
                ref_max = float(groups[4]) if groups[4] else None
                
                # Use standard reference range if not provided
                if test_name in self.REFERENCE_RANGES:
                    std_range = self.REFERENCE_RANGES[test_name]
                    if ref_min is None:
                        ref_min = std_range["min"]
                    if ref_max is None:
                        ref_max = std_range["max"]
                    if not unit:
                        unit = std_range["unit"]
                
                return LabResult(
                    test_name=test_name,
                    value=value,
                    unit=unit,
                    reference_min=ref_min,
                    reference_max=ref_max
                )
        
        return None
    
    def determine_status(self, result: LabResult) -> tuple:
        """Determine status and severity of a result."""
        if result.reference_min is None or result.reference_max is None:
            return "unknown", "none"
        
        value = result.value
        min_val = result.reference_min
        max_val = result.reference_max
        
        if min_val <= value <= max_val:
            return "normal", "none"
        
        # Calculate deviation percentage
        if value < min_val:
            deviation = (min_val - value) / min_val if min_val > 0 else 0
            if deviation > 0.5:
                return "low", "severe"
            elif deviation > 0.2:
                return "low", "moderate"
            else:
                return "low", "mild"
        else:  # value > max_val
            deviation = (value - max_val) / max_val if max_val > 0 else 0
            if deviation > 0.5:
                return "high", "severe"
            elif deviation > 0.2:
                return "high", "moderate"
            else:
                return "high", "mild"
    
    def generate_explanation(self, result: LabResult) -> str:
        """Generate patient-friendly explanation."""
        explanations = {
            "白细胞计数": {
                "normal": "白细胞计数在正常范围内，说明免疫系统功能正常。",
                "low": "白细胞计数偏低，可能提示免疫力下降，建议咨询医生。",
                "high": "白细胞计数偏高，可能提示存在感染或炎症反应。"
            },
            "红细胞计数": {
                "normal": "红细胞计数正常，血液携氧能力良好。",
                "low": "红细胞计数偏低，可能存在贫血，建议进一步检查。",
                "high": "红细胞计数偏高，可能提示血液浓缩或其他情况。"
            },
            "血红蛋白": {
                "normal": "血红蛋白水平正常，血液携氧功能良好。",
                "low": "血红蛋白偏低，可能存在贫血症状，如疲劳、乏力。",
                "high": "血红蛋白偏高，可能提示脱水或红细胞增多。"
            },
            "血小板计数": {
                "normal": "血小板计数正常，凝血功能良好。",
                "low": "血小板计数偏低，可能影响凝血功能，需关注。",
                "high": "血小板计数偏高，可能增加血栓风险。"
            },
            "总胆固醇": {
                "normal": "总胆固醇水平在正常范围内，血脂控制良好。",
                "low": "总胆固醇偏低，需注意营养均衡。",
                "high": "总胆固醇偏高，建议减少高脂食物摄入，增加运动。"
            },
            "低密度脂蛋白胆固醇": {
                "normal": "低密度脂蛋白（坏胆固醇）控制良好。",
                "high": "低密度脂蛋白偏高，是心血管疾病的危险因素，建议改善饮食和运动。"
            },
            "高密度脂蛋白胆固醇": {
                "normal": "高密度脂蛋白（好胆固醇）水平良好。",
                "low": "高密度脂蛋白偏低，建议增加有氧运动，保护心血管健康。",
                "high": "高密度脂蛋白较高，对心血管有保护作用。"
            },
            "甘油三酯": {
                "normal": "甘油三酯水平正常。",
                "high": "甘油三酯偏高，建议减少糖分和油脂摄入，控制体重。"
            },
            "谷丙转氨酶": {
                "normal": "肝功能指标正常。",
                "high": "谷丙转氨酶偏高，可能提示肝细胞损伤，建议进一步检查肝功能。"
            },
            "谷草转氨酶": {
                "normal": "肝功能指标正常。",
                "high": "谷草转氨酶偏高，可能提示肝脏或心肌损伤。"
            },
            "肌酐": {
                "normal": "肾功能指标正常。",
                "high": "肌酐偏高，可能提示肾功能下降，建议咨询肾内科医生。"
            },
            "尿酸": {
                "normal": "尿酸水平正常。",
                "high": "尿酸偏高，可能增加痛风风险，建议多喝水，减少高嘌呤食物。"
            },
            "空腹血糖": {
                "normal": "血糖水平正常。",
                "high": "空腹血糖偏高，可能存在糖代谢异常，建议控制饮食并复查。"
            },
            "糖化血红蛋白": {
                "normal": "糖化血红蛋白正常，近3个月血糖控制良好。",
                "high": "糖化血红蛋白偏高，提示近期血糖控制不佳。"
            },
        }
        
        test_explanations = explanations.get(result.test_name, {
            "normal": f"{result.test_name}在正常范围内。",
            "low": f"{result.test_name}偏低。",
            "high": f"{result.test_name}偏高。"
        })
        
        return test_explanations.get(result.status, test_explanations.get("normal", ""))
    
    def generate_recommendation(self, result: LabResult) -> str:
        """Generate health recommendations."""
        recommendations = {
            "总胆固醇": {
                "high": "建议：减少动物脂肪摄入，多吃蔬菜水果，每周至少150分钟中等强度运动。"
            },
            "低密度脂蛋白胆固醇": {
                "high": "建议：限制饱和脂肪摄入，选择橄榄油等健康油脂，定期监测血脂。"
            },
            "甘油三酯": {
                "high": "建议：控制精制糖和甜食，限制饮酒，增加有氧运动。"
            },
            "谷丙转氨酶": {
                "high": "建议：避免饮酒，勿滥用药物，复查肝功能，必要时做肝脏超声。"
            },
            "尿酸": {
                "high": "建议：每日饮水2000ml以上，少吃海鲜、动物内脏、浓肉汤等高嘌呤食物。"
            },
            "空腹血糖": {
                "high": "建议：控制主食量，选择低升糖指数食物，餐后适当运动，定期复查。"
            },
        }
        
        test_recs = recommendations.get(result.test_name, {})
        return test_recs.get(result.status, "")
    
    def interpret(self, input_text: str) -> List[LabResult]:
        """Interpret lab results from input text."""
        results = []
        
        # Split by lines and common separators
        lines = re.split(r'[\n,;，；]', input_text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            result = self.parse_lab_line(line)
            if result:
                # Determine status and severity
                result.status, result.severity = self.determine_status(result)
                # Generate explanation
                result.explanation = self.generate_explanation(result)
                # Generate recommendation
                result.recommendation = self.generate_recommendation(result)
                results.append(result)
        
        return results
    
    def format_output(self, results: List[LabResult]) -> str:
        """Format results as patient-friendly output."""
        if not results:
            return "未能识别有效的检验结果，请检查输入格式。"
        
        output_lines = ["=== 检验结果解读 ===\n"]
        
        for r in results:
            # Status emoji
            status_emoji = {
                "normal": "✅",
                "low": "⚠️",
                "high": "⚠️",
                "critical": "🚨",
                "unknown": "❓"
            }.get(r.status, "❓")
            
            # Status text
            status_text = {
                "normal": "正常",
                "low": "偏低",
                "high": "偏高",
                "critical": "危急",
                "unknown": "未知"
            }.get(r.status, "未知")
            
            ref_range = ""
            if r.reference_min is not None and r.reference_max is not None:
                ref_range = f" (参考: {r.reference_min}-{r.reference_max} {r.unit})"
            
            output_lines.append(f"{status_emoji} {r.test_name}: {r.value} {r.unit}{ref_range}")
            output_lines.append(f"   状态: {status_text}")
            output_lines.append(f"   解读: {r.explanation}")
            if r.recommendation:
                output_lines.append(f"   {r.recommendation}")
            output_lines.append("")
        
        output_lines.append(self.disclaimer)
        return "\n".join(output_lines)
    
    def to_dict(self, results: List[LabResult]) -> List[Dict[str, Any]]:
        """Convert results to dictionary format."""
        return [asdict(r) for r in results]


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Lab Result Interpretation Tool")
    parser.add_argument("--file", "-f", help="Input file containing lab results")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    interpreter = LabResultInterpreter()
    
    if args.interactive:
        print("检验结果解读工具 - 交互模式")
        print("输入检验结果（每行一个，或逗号分隔），输入'quit'退出")
        print("示例: 总胆固醇: 5.8 mmol/L (参考: 3.1-5.7)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n请输入检验结果: ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                if not user_input:
                    continue
                
                results = interpreter.interpret(user_input)
                print(interpreter.format_output(results))
            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
            results = interpreter.interpret(content)
            
            if args.json:
                print(json.dumps(interpreter.to_dict(results), ensure_ascii=False, indent=2))
            else:
                print(interpreter.format_output(results))
        except FileNotFoundError:
            print(f"错误: 找不到文件 {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"错误: {e}")
            sys.exit(1)
    
    else:
        # Read from stdin
        print("检验结果解读工具")
        print("使用方式:")
        print("  python main.py --interactive    # 交互模式")
        print("  python main.py --file lab.txt   # 从文件读取")
        print("  echo '总胆固醇: 5.8' | python main.py  # 从标准输入")
        print("\n请输入检验结果（Ctrl+D结束）:")
        
        try:
            content = sys.stdin.read()
            if content.strip():
                results = interpreter.interpret(content)
                print(interpreter.format_output(results))
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()
