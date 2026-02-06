#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Twin Discharge Drafter (ID: 214)
自动生成标准出院小结的AI Skill

功能: 模仿人类医生逻辑，自动生成包含"入院情况、诊疗经过、出院医嘱"的标准出院小结
"""

import argparse
import json
import re
from datetime import datetime, date
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path
from dateutil import parser as date_parser


@dataclass
class PatientInfo:
    """患者基本信息"""
    name: str = ""
    gender: str = ""  # 男/女
    age: int = 0
    age_unit: str = "岁"
    admission_date: str = ""
    discharge_date: str = ""
    department: str = ""
    bed_number: str = ""
    medical_record_no: str = ""
    
    @property
    def hospital_days(self) -> int:
        """计算住院天数"""
        try:
            admit = date_parser.parse(self.admission_date).date()
            discharge = date_parser.parse(self.discharge_date).date()
            return (discharge - admit).days + 1
        except:
            return 0


@dataclass
class DischargeSummary:
    """出院小结数据结构"""
    patient_info: PatientInfo = field(default_factory=PatientInfo)
    admission_status: str = ""      # 入院情况
    treatment_course: str = ""      # 诊疗经过
    discharge_orders: str = ""      # 出院医嘱
    discharge_diagnosis: str = ""   # 出院诊断
    admission_diagnosis: str = ""   # 入院诊断
    
    def to_markdown(self) -> str:
        """生成标准格式的出院小结Markdown"""
        template = f"""# 出院小结

## 基本信息
| 项目 | 内容 |
|------|------|
| 姓名 | {self.patient_info.name} |
| 性别 | {self.patient_info.gender} |
| 年龄 | {self.patient_info.age}{self.patient_info.age_unit} |
| 入院日期 | {self.patient_info.admission_date} |
| 出院日期 | {self.patient_info.discharge_date} |
| 住院天数 | {self.patient_info.hospital_days} 天 |
| 科室 | {self.patient_info.department} |
| 床号 | {self.patient_info.bed_number} |
| 住院号 | {self.patient_info.medical_record_no} |

## 入院诊断
{self.admission_diagnosis or "待补充"}

## 出院诊断
{self.discharge_diagnosis or "待补充"}

## 入院情况
{self.admission_status or "待补充"}

## 诊疗经过
{self.treatment_course or "待补充"}

## 出院情况
患者一般情况良好，生命体征平稳，准予出院。

## 出院医嘱
{self.discharge_orders or "待补充"}

---
*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}*  
*生成系统: Digital Twin Discharge Drafter v1.0.0*  
**审核状态: ⏳ 待医师审核 (PENDING PHYSICIAN AUDIT)**
"""
        return template
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "patient_info": asdict(self.patient_info),
            "admission_diagnosis": self.admission_diagnosis,
            "discharge_diagnosis": self.discharge_diagnosis,
            "admission_status": self.admission_status,
            "treatment_course": self.treatment_course,
            "discharge_orders": self.discharge_orders,
        }


class MedicalInfoExtractor:
    """医疗信息提取器 - 从原始文本中提取关键信息"""
    
    # 常见症状关键词
    SYMPTOMS = [
        "发热", "咳嗽", "咳痰", "胸痛", "胸闷", "气促", "呼吸困难",
        "腹痛", "腹胀", "恶心", "呕吐", "腹泻", "便秘", "便血",
        "头痛", "头晕", "意识障碍", "肢体无力", "麻木",
        "腰痛", "血尿", "尿频", "尿急", "尿痛"
    ]
    
    # 常见检查结果关键词
    EXAM_INDICATORS = {
        "血压": r"血压[：:]\s*(\d+/\d+)\s*mmHg",
        "心率": r"心率[：:]\s*(\d+)\s*次?/分",
        "体温": r"体温[：:]\s*(\d+\.?\d*)\s*[°℃]",
        "呼吸": r"呼吸[：:]\s*(\d+)\s*次?/分",
    }
    
    def __init__(self):
        self.vital_signs = {}
        self.symptoms_found = []
        self.diagnoses = []
    
    def extract_vital_signs(self, text: str) -> Dict[str, str]:
        """提取生命体征"""
        vitals = {}
        for key, pattern in self.EXAM_INDICATORS.items():
            matches = re.findall(pattern, text)
            if matches:
                vitals[key] = matches[0]
        return vitals
    
    def extract_symptoms(self, text: str) -> List[str]:
        """提取症状描述"""
        found = []
        for symptom in self.SYMPTOMS:
            if symptom in text:
                found.append(symptom)
        return found
    
    def extract_diagnosis(self, text: str) -> List[str]:
        """提取诊断信息"""
        patterns = [
            r"诊断[：:]\s*([^。\n]+)",
            r"考虑(.+?)[。；]",
            r"(.+?)可能性大",
        ]
        diagnoses = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            diagnoses.extend(matches)
        return [d.strip() for d in diagnoses if len(d.strip()) > 2]
    
    def extract_treatments(self, text: str) -> List[str]:
        """提取治疗措施"""
        treatments = []
        # 匹配治疗方案
        patterns = [
            r"给予(.+?)[治疗处理]",
            r"予(.+?)[治疗用药]",
            r"行(.+?术)",
            r"使用(.+?)[药物]",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            treatments.extend(matches)
        return [t.strip() for t in treatments if len(t.strip()) > 1]


class DischargeDrafter:
    """出院小结起草器主类"""
    
    def __init__(self, template_path: Optional[str] = None):
        self.extractor = MedicalInfoExtractor()
        self.template_path = template_path
        self._load_medical_terms()
    
    def _load_medical_terms(self):
        """加载医学术语库"""
        self.medical_terms = {
            "departments": ["内科", "外科", "急诊科", "心内科", "呼吸科", "消化科"],
            "common_meds": ["阿司匹林", "氯吡格雷", "他汀", "降压药", "胰岛素"],
            "followup_items": ["门诊随访", "定期复查", "不适随诊"],
        }
    
    def generate_admission_status(self, admission_text: str, exam_text: str) -> str:
        """
        生成入院情况部分
        模仿医生思路：主诉 + 现病史 + 查体 + 辅助检查
        """
        # 提取关键信息
        vitals = self.extractor.extract_vital_signs(admission_text + exam_text)
        symptoms = self.extractor.extract_symptoms(admission_text)
        
        lines = []
        
        # 1. 主诉提取 (第一句通常是主诉)
        sentences = re.split(r'[。！？\n]', admission_text)
        if sentences:
            chief_complaint = sentences[0].strip()
            if len(chief_complaint) > 5:
                lines.append(f"**主诉**: {chief_complaint}。")
        
        # 2. 现病史
        lines.append("\n**现病史**: ")
        if symptoms:
            lines.append(f"患者因{ '、'.join(symptoms[:3]) }就诊。")
        
        # 3. 入院查体
        lines.append("\n**入院查体**: ")
        vital_strs = []
        for k, v in vitals.items():
            vital_strs.append(f"{k}{v}")
        if vital_strs:
            lines.append(f"生命体征: {', '.join(vital_strs)}。")
        else:
            lines.append("生命体征平稳。")
        
        # 4. 入院辅助检查
        lines.append("\n**入院辅助检查**: ")
        # 提取关键检查结果
        key_findings = self._extract_key_findings(exam_text)
        if key_findings:
            lines.append(key_findings)
        else:
            lines.append("入院后完善相关检查。")
        
        return "\n".join(lines)
    
    def generate_treatment_course(self, progress_text: str, exam_text: str) -> str:
        """
        生成诊疗经过部分
        模仿医生思路：诊断过程 + 治疗方案 + 病情演变
        """
        lines = []
        
        # 1. 诊断经过
        lines.append("**诊断经过**: ")
        diagnoses = self.extractor.extract_diagnosis(progress_text)
        if diagnoses:
            lines.append(f"结合临床表现及辅助检查，考虑{diagnoses[0]}。")
        else:
            lines.append("结合患者病史、体征及辅助检查，明确诊断。")
        
        # 2. 治疗过程
        lines.append("\n**治疗过程**: ")
        treatments = self.extractor.extract_treatments(progress_text)
        if treatments:
            unique_treatments = list(set(treatments))[:5]  # 去重，最多5个
            lines.append(f"入院后予{ '、'.join(unique_treatments) }。")
        else:
            lines.append("入院后给予对症支持治疗，治疗方案根据病情调整。")
        
        # 3. 病情演变
        lines.append("\n**病情演变**: ")
        lines.append("经治疗后，患者症状较前缓解，一般情况改善。复查相关指标好转。")
        
        return "\n".join(lines)
    
    def generate_discharge_orders(self, diagnosis: str, treatments: List[str]) -> str:
        """
        生成出院医嘱部分
        模仿医生思路：用药 + 复查 + 生活方式 + 随诊
        """
        lines = []
        
        # 1. 出院带药
        lines.append("**1. 出院带药**: ")
        lines.append("- 请按医嘱规律服用药物，不可擅自停药或更改剂量")
        lines.append("- 如有药物不良反应，请及时就诊")
        
        # 2. 饮食与活动
        lines.append("\n**2. 饮食与活动**: ")
        lines.append("- 低盐低脂饮食，避免油腻、辛辣食物")
        lines.append("- 适当活动，避免剧烈运动")
        lines.append("- 保证充足睡眠，避免过度劳累")
        
        # 3. 复查建议
        lines.append("\n**3. 复查建议**: ")
        lines.append("- 出院后1-2周门诊复查血常规、肝肾功能")
        lines.append("- 定期复查，监测病情变化")
        
        # 4. 随诊指导
        lines.append("\n**4. 随诊指导**: ")
        lines.append("- 如有不适，及时就诊")
        lines.append("- 建议定期专科门诊随访")
        
        # 5. 紧急情况
        lines.append("\n**5. 紧急情况**: ")
        lines.append("如出现以下情况请立即就诊:")
        lines.append("- 症状加重或复发")
        lines.append("- 出现新的不适症状")
        lines.append("- 药物严重不良反应")
        
        return "\n".join(lines)
    
    def _extract_key_findings(self, exam_text: str) -> str:
        """提取关键检查结果"""
        findings = []
        
        # 常见检查项目匹配
        patterns = {
            "血常规": r"血常规[：:]?(.+?)(?=\n|。|$)",
            "生化": r"生化[：:]?(.+?)(?=\n|。|$)",
            "心电图": r"心电图[：:]?(.+?)(?=\n|。|$)",
            "影像学": r"(CT|MRI|X线|超声)[：:]?(.+?)(?=\n|。|$)",
        }
        
        for exam_type, pattern in patterns.items():
            matches = re.findall(pattern, exam_text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    findings.append(f"{exam_type}: {matches[0][-1].strip()}")
                else:
                    findings.append(f"{exam_type}: {matches[0].strip()}")
        
        return "; ".join(findings) if findings else ""
    
    def generate(
        self,
        admission_record: str,
        progress_notes: str,
        exam_results: str,
        patient_info: Dict[str, Any]
    ) -> DischargeSummary:
        """
        主生成函数 - 生成完整出院小结
        
        Args:
            admission_record: 入院记录文本
            progress_notes: 病程记录文本
            exam_results: 检查结果文本
            patient_info: 患者信息字典
        
        Returns:
            DischargeSummary对象
        """
        # 构建患者信息对象
        info = PatientInfo(**patient_info)
        
        # 提取诊断信息
        diagnoses = self.extractor.extract_diagnosis(admission_record + progress_notes)
        admission_dx = diagnoses[0] if diagnoses else ""
        discharge_dx = diagnoses[-1] if len(diagnoses) > 1 else admission_dx
        
        # 生成各部分
        admission_status = self.generate_admission_status(admission_record, exam_results)
        treatment_course = self.generate_treatment_course(progress_notes, exam_results)
        discharge_orders = self.generate_discharge_orders(discharge_dx, [])
        
        return DischargeSummary(
            patient_info=info,
            admission_status=admission_status,
            treatment_course=treatment_course,
            discharge_orders=discharge_orders,
            admission_diagnosis=admission_dx,
            discharge_diagnosis=discharge_dx,
        )


def interactive_mode():
    """交互式模式"""
    print("=" * 50)
    print("Digital Twin Discharge Drafter - 交互式模式")
    print("=" * 50)
    
    # 收集患者信息
    print("\n【患者基本信息】")
    patient_info = {
        "name": input("患者姓名: ").strip(),
        "gender": input("性别 (男/女): ").strip(),
        "age": int(input("年龄: ").strip() or 0),
        "admission_date": input("入院日期 (YYYY-MM-DD): ").strip(),
        "discharge_date": input("出院日期 (YYYY-MM-DD): ").strip(),
        "department": input("科室: ").strip(),
        "medical_record_no": input("住院号: ").strip(),
    }
    
    print("\n【入院记录】 (输入空行结束)")
    admission_lines = []
    while True:
        line = input()
        if not line:
            break
        admission_lines.append(line)
    
    print("\n【病程记录】 (输入空行结束)")
    progress_lines = []
    while True:
        line = input()
        if not line:
            break
        progress_lines.append(line)
    
    print("\n【检查结果】 (输入空行结束)")
    exam_lines = []
    while True:
        line = input()
        if not line:
            break
        exam_lines.append(line)
    
    # 生成
    drafter = DischargeDrafter()
    summary = drafter.generate(
        admission_record="\n".join(admission_lines),
        progress_notes="\n".join(progress_lines),
        exam_results="\n".join(exam_lines),
        patient_info=patient_info
    )
    
    print("\n" + "=" * 50)
    print("【生成的出院小结】")
    print("=" * 50)
    print(summary.to_markdown())
    
    return summary


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="Digital Twin Discharge Drafter - 自动生成出院小结",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --interactive                    # 交互式模式
  %(prog)s -a admission.txt -p progress.txt -e exams.txt -o output.md
  %(prog)s --json-input patient.json -o output.md
        """
    )
    
    parser.add_argument("-a", "--admission", help="入院记录文件路径")
    parser.add_argument("-p", "--progress", help="病程记录文件路径")
    parser.add_argument("-e", "--exams", help="检查结果文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--json-input", help="JSON格式输入文件路径")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--template", help="自定义模板路径")
    
    args = parser.parse_args()
    
    if args.interactive:
        summary = interactive_mode()
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(summary.to_markdown())
            print(f"\n✅ 已保存到: {args.output}")
        return
    
    if args.json_input:
        # JSON输入模式
        with open(args.json_input, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        drafter = DischargeDrafter(template_path=args.template)
        summary = drafter.generate(
            admission_record=data.get("admission_record", ""),
            progress_notes=data.get("progress_notes", ""),
            exam_results=data.get("exam_results", ""),
            patient_info=data.get("patient_info", {})
        )
    
    elif args.admission and args.progress and args.exams:
        # 文件输入模式
        with open(args.admission, "r", encoding="utf-8") as f:
            admission_text = f.read()
        with open(args.progress, "r", encoding="utf-8") as f:
            progress_text = f.read()
        with open(args.exams, "r", encoding="utf-8") as f:
            exam_text = f.read()
        
        # 从文件名或默认配置读取患者信息
        patient_info = {
            "name": "患者",
            "gender": "未知",
            "age": 0,
            "admission_date": date.today().isoformat(),
            "discharge_date": date.today().isoformat(),
        }
        
        drafter = DischargeDrafter(template_path=args.template)
        summary = drafter.generate(
            admission_record=admission_text,
            progress_notes=progress_text,
            exam_results=exam_text,
            patient_info=patient_info
        )
    
    else:
        parser.print_help()
        return
    
    # 输出结果
    output = summary.to_markdown()
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 出院小结已生成: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
