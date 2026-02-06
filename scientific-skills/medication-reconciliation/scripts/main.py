#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medication Reconciliation Skill
药物核对 - 对比入院前用药清单和住院医嘱

ID: 164
功能: 自动识别遗漏或重复的药物
"""

import json
import argparse
import difflib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Medication:
    """药物数据模型"""
    drug_name: str
    generic_name: str = ""
    dosage: str = ""
    frequency: str = ""
    route: str = ""
    indication: str = ""
    order_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Medication":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class MatchResult:
    """药物匹配结果"""
    pre_admission_med: Medication
    inpatient_med: Optional[Medication]
    match_type: str  # 'exact', 'fuzzy', 'none'
    similarity: float
    is_duplicate: bool = False
    warning: Optional[str] = None


class MedicationReconciler:
    """药物核对核心类"""
    
    # 关键药物类别 - 遗漏时需要警告
    CRITICAL_DRUG_CLASSES = [
        "抗凝", "抗血小板", "降压", "降糖", "胰岛素",
        "抗癫痫", "抗心律失常", "激素", "免疫抑制"
    ]
    
    # 常见药物别名映射
    DRUG_SYNONYMS = {
        "阿托伐他汀": ["atorvastatin", "立普妥", "lipitor"],
        "氨氯地平": ["amlodipine", "络活喜", "norvasc"],
        "氯吡格雷": ["clopidogrel", "波立维", "plavix"],
        "阿司匹林": ["aspirin", "拜阿司匹林", "aspirin"],
        "二甲双胍": ["metformin", "格华止", "glucophage"],
        "美托洛尔": ["metoprolol", "倍他乐克", "betaloc"],
    }
    
    def __init__(self, fuzzy_threshold: float = 0.8):
        self.pre_admission_meds: List[Medication] = []
        self.inpatient_meds: List[Medication] = []
        self.fuzzy_threshold = fuzzy_threshold
        self.match_results: List[MatchResult] = []
        
    def load_pre_admission(self, filepath: str) -> None:
        """加载入院前用药清单"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.patient_id = data.get('patient_id', 'Unknown')
        self.patient_name = data.get('patient_name', 'Unknown')
        self.admission_date = data.get('admission_date', datetime.now().strftime('%Y-%m-%d'))
        
        self.pre_admission_meds = [
            Medication.from_dict(med) for med in data.get('medications', [])
        ]
        print(f"✓ 加载入院前用药: {len(self.pre_admission_meds)} 种药物")
        
    def load_inpatient_orders(self, filepath: str) -> None:
        """加载住院医嘱"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.inpatient_meds = [
            Medication.from_dict(med) for med in data.get('medications', [])
        ]
        print(f"✓ 加载住院医嘱: {len(self.inpatient_meds)} 种药物")
        
    def _normalize_name(self, name: str) -> str:
        """标准化药物名称（小写、去空格）"""
        return name.lower().replace(' ', '').replace('片', '').replace('胶囊', '')
        
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """计算两个药物名称的相似度"""
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # 精确匹配
        if norm1 == norm2:
            return 1.0
            
        # 检查别名
        for drug, synonyms in self.DRUG_SYNONYMS.items():
            names = [drug.lower()] + [s.lower() for s in synonyms]
            if norm1 in names and norm2 in names:
                return 1.0
        
        # 模糊匹配
        return difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
    def _find_best_match(self, pre_med: Medication) -> Tuple[Optional[Medication], float, str]:
        """为入院前药物找到最佳匹配的住院医嘱药物"""
        best_match = None
        best_score = 0.0
        match_type = 'none'
        
        for in_med in self.inpatient_meds:
            # 通用名匹配
            if pre_med.generic_name and in_med.generic_name:
                score = self._calculate_similarity(pre_med.generic_name, in_med.generic_name)
                if score > best_score:
                    best_score = score
                    best_match = in_med
                    match_type = 'exact' if score == 1.0 else 'fuzzy'
            
            # 商品名匹配
            score = self._calculate_similarity(pre_med.drug_name, in_med.drug_name)
            if score > best_score:
                best_score = score
                best_match = in_med
                match_type = 'exact' if score == 1.0 else 'fuzzy'
                
        return best_match, best_score, match_type
        
    def _is_critical_drug(self, med: Medication) -> bool:
        """判断是否为关键药物"""
        combined_text = f"{med.drug_name} {med.generic_name} {med.indication}".lower()
        return any(cls_name in combined_text for cls_name in self.CRITICAL_DRUG_CLASSES)
        
    def _check_duplicate(self, pre_med: Medication, in_med: Medication) -> bool:
        """检查是否为重复用药（相同药物不同名称）"""
        if not pre_med.generic_name or not in_med.generic_name:
            return False
            
        # 通用名相同，剂量范围相近
        if self._calculate_similarity(pre_med.generic_name, in_med.generic_name) >= 0.9:
            # 简化剂量比较（实际应用中需要更复杂的解析）
            pre_dose = ''.join(filter(str.isdigit, pre_med.dosage)) if pre_med.dosage else ""
            in_dose = ''.join(filter(str.isdigit, in_med.dosage)) if in_med.dosage else ""
            if pre_dose and in_dose and pre_dose == in_dose:
                return True
        return False
        
    def reconcile(self) -> Dict[str, Any]:
        """执行药物核对"""
        print("\n🔍 开始药物核对...")
        
        continued_meds = []
        discontinued_meds = []
        duplicate_meds = []
        warnings = []
        
        # 遍历入院前用药
        for pre_med in self.pre_admission_meds:
            best_match, score, match_type = self._find_best_match(pre_med)
            
            if best_match and score >= self.fuzzy_threshold:
                # 药物继续
                is_dup = self._check_duplicate(pre_med, best_match)
                
                result = MatchResult(
                    pre_admission_med=pre_med,
                    inpatient_med=best_match,
                    match_type=match_type,
                    similarity=score,
                    is_duplicate=is_dup
                )
                
                if is_dup:
                    duplicate_meds.append(result)
                    warnings.append({
                        "level": "warning",
                        "type": "duplicate",
                        "message": f"可能的重复用药: {pre_med.drug_name} / {best_match.drug_name}",
                        "drug": pre_med.drug_name
                    })
                else:
                    continued_meds.append(result)
                    
            else:
                # 药物遗漏/停用
                result = MatchResult(
                    pre_admission_med=pre_med,
                    inpatient_med=None,
                    match_type='none',
                    similarity=0.0
                )
                discontinued_meds.append(result)
                
                # 关键药物遗漏警告
                if self._is_critical_drug(pre_med):
                    warnings.append({
                        "level": "critical",
                        "type": "discontinued_critical",
                        "message": f"关键药物可能遗漏: {pre_med.drug_name} ({pre_med.indication})",
                        "drug": pre_med.drug_name,
                        "suggestion": "请确认是否故意停用，或考虑继续使用"
                    })
                else:
                    warnings.append({
                        "level": "info",
                        "type": "discontinued",
                        "message": f"药物停用: {pre_med.drug_name}",
                        "drug": pre_med.drug_name
                    })
        
        # 查找新增药物
        new_meds = []
        for in_med in self.inpatient_meds:
            is_new = True
            for result in continued_meds + duplicate_meds:
                if result.inpatient_med == in_med:
                    is_new = False
                    break
            if is_new:
                new_meds.append(in_med)
        
        # 生成报告
        report = {
            "report_id": f"MR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "patient_id": getattr(self, 'patient_id', 'Unknown'),
            "patient_name": getattr(self, 'patient_name', 'Unknown'),
            "admission_date": getattr(self, 'admission_date', ''),
            "summary": {
                "pre_admission_count": len(self.pre_admission_meds),
                "inpatient_count": len(self.inpatient_meds),
                "continued_count": len(continued_meds),
                "discontinued_count": len(discontinued_meds),
                "new_count": len(new_meds),
                "duplicate_count": len(duplicate_meds),
                "warning_count": len(warnings)
            },
            "details": {
                "continued": [
                    {
                        "pre_admission": r.pre_admission_med.to_dict(),
                        "inpatient": r.inpatient_med.to_dict() if r.inpatient_med else None,
                        "match_confidence": r.similarity
                    } for r in continued_meds
                ],
                "discontinued": [
                    {
                        "medication": r.pre_admission_med.to_dict(),
                        "is_critical": self._is_critical_drug(r.pre_admission_med)
                    } for r in discontinued_meds
                ],
                "new_medications": [m.to_dict() for m in new_meds],
                "duplicates": [
                    {
                        "pre_admission": r.pre_admission_med.to_dict(),
                        "inpatient": r.inpatient_med.to_dict() if r.inpatient_med else None
                    } for r in duplicate_meds
                ],
                "warnings": warnings
            },
            "recommendations": self._generate_recommendations(
                continued_meds, discontinued_meds, duplicate_meds, warnings
            )
        }
        
        self.match_results = continued_meds + discontinued_meds + duplicate_meds
        return report
        
    def _generate_recommendations(
        self, 
        continued: List[MatchResult],
        discontinued: List[MatchResult],
        duplicates: List[MatchResult],
        warnings: List[Dict]
    ) -> List[str]:
        """生成临床建议"""
        recommendations = []
        
        # 关键药物遗漏建议
        critical_discontinued = [w for w in warnings if w['level'] == 'critical']
        if critical_discontinued:
            recommendations.append(
                f"⚠️ 发现 {len(critical_discontinued)} 种关键药物可能遗漏，建议医生审核"
            )
        
        # 重复用药建议
        if duplicates:
            recommendations.append(
                f"⚠️ 发现 {len(duplicates)} 种可能的重复用药，请确认是否为治疗需要"
            )
        
        # 停药记录建议
        if discontinued:
            recommendations.append(
                f"ℹ️ 共 {len(discontinued)} 种入院前药物未在医嘱中体现，建议记录停药原因"
            )
        
        # 新增药物提醒
        new_count = len([w for w in warnings if 'new' in w.get('type', '')])
        if new_count > 0:
            recommendations.append(f"ℹ️ 住院期间新增 {new_count} 种药物")
        
        if not recommendations:
            recommendations.append("✅ 药物核对完成，未发现明显问题")
            
        return recommendations


def generate_example_data():
    """生成示例数据用于测试"""
    # 入院前用药清单
    pre_admission = {
        "patient_id": "P20260206001",
        "patient_name": "王某某",
        "admission_date": "2026-02-06",
        "medications": [
            {
                "drug_name": "阿托伐他汀钙片",
                "generic_name": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "每晚一次",
                "route": "口服",
                "indication": "高血脂"
            },
            {
                "drug_name": "氨氯地平片",
                "generic_name": "Amlodipine",
                "dosage": "5mg",
                "frequency": "每日一次",
                "route": "口服",
                "indication": "高血压"
            },
            {
                "drug_name": "阿司匹林肠溶片",
                "generic_name": "Aspirin",
                "dosage": "100mg",
                "frequency": "每日一次",
                "route": "口服",
                "indication": "冠心病二级预防"
            },
            {
                "drug_name": "二甲双胍片",
                "generic_name": "Metformin",
                "dosage": "500mg",
                "frequency": "每日三次",
                "route": "口服",
                "indication": "2型糖尿病"
            },
            {
                "drug_name": "维生素C片",
                "generic_name": "Vitamin C",
                "dosage": "100mg",
                "frequency": "每日一次",
                "route": "口服",
                "indication": "营养补充"
            }
        ]
    }
    
    # 住院医嘱
    inpatient_orders = {
        "patient_id": "P20260206001",
        "order_date": "2026-02-06",
        "medications": [
            {
                "drug_name": "立普妥",
                "generic_name": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "qn",
                "route": "po",
                "order_type": "长期医嘱"
            },
            {
                "drug_name": "络活喜",
                "generic_name": "Amlodipine",
                "dosage": "5mg",
                "frequency": "qd",
                "route": "po",
                "order_type": "长期医嘱"
            },
            {
                "drug_name": "拜阿司匹林",
                "generic_name": "Aspirin",
                "dosage": "100mg",
                "frequency": "qd",
                "route": "po",
                "order_type": "长期医嘱"
            },
            {
                "drug_name": "氯化钠注射液",
                "generic_name": "Sodium Chloride",
                "dosage": "500ml",
                "frequency": "qd",
                "route": "ivgtt",
                "order_type": "临时医嘱"
            }
        ]
    }
    
    # 保存示例数据
    skill_dir = Path(__file__).parent.parent
    example_dir = skill_dir / "examples"
    example_dir.mkdir(exist_ok=True)
    
    with open(example_dir / "pre_admission.json", 'w', encoding='utf-8') as f:
        json.dump(pre_admission, f, ensure_ascii=False, indent=2)
    
    with open(example_dir / "inpatient_orders.json", 'w', encoding='utf-8') as f:
        json.dump(inpatient_orders, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 示例数据已保存到 {example_dir}")
    return example_dir / "pre_admission.json", example_dir / "inpatient_orders.json"


def main():
    parser = argparse.ArgumentParser(
        description="药物核对工具 - 对比入院前用药和住院医嘱",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --example                    # 运行示例
  python main.py -p pre.json -i orders.json   # 指定输入文件
  python main.py -p pre.json -i orders.json -o report.json  # 指定输出文件
        """
    )
    
    parser.add_argument('-p', '--pre-admission', help='入院前用药清单JSON文件路径')
    parser.add_argument('-i', '--inpatient', help='住院医嘱JSON文件路径')
    parser.add_argument('-o', '--output', help='输出报告JSON文件路径')
    parser.add_argument('--example', action='store_true', help='使用示例数据运行')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 使用示例数据
    if args.example:
        pre_file, in_file = generate_example_data()
        args.pre_admission = str(pre_file)
        args.inpatient = str(in_file)
    
    # 检查必需参数
    if not args.pre_admission or not args.inpatient:
        parser.print_help()
        print("\n❌ 错误: 请提供入院前用药清单和住院医嘱文件路径，或使用 --example 运行示例")
        return 1
    
    try:
        # 创建核对器
        reconciler = MedicationReconciler()
        
        # 加载数据
        reconciler.load_pre_admission(args.pre_admission)
        reconciler.load_inpatient_orders(args.inpatient)
        
        # 执行核对
        report = reconciler.reconcile()
        
        # 输出报告
        report_json = json.dumps(report, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report_json)
            print(f"\n✓ 报告已保存到: {args.output}")
        else:
            print("\n" + "="*60)
            print("药物核对报告")
            print("="*60)
            print(report_json)
        
        # 简洁摘要
        print("\n" + "="*60)
        print("核对摘要")
        print("="*60)
        summary = report['summary']
        print(f"  入院前用药: {summary['pre_admission_count']} 种")
        print(f"  住院医嘱:   {summary['inpatient_count']} 种")
        print(f"  ├─ 继续用药: {summary['continued_count']} 种")
        print(f"  ├─ 新增用药: {summary['new_count']} 种")
        print(f"  ├─ 可能遗漏: {summary['discontinued_count']} 种")
        print(f"  └─ 重复用药: {summary['duplicate_count']} 种")
        print(f"  警告: {summary['warning_count']} 条")
        
        if report['recommendations']:
            print("\n💡 建议:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: 文件未找到 - {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"\n❌ 错误: JSON格式错误 - {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
