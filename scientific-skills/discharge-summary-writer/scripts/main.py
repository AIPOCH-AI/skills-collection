#!/usr/bin/env python3
"""
Discharge Summary Writer
Generates hospital discharge summaries from patient data.

Usage:
    python main.py --input patient_data.json --output discharge_summary.md
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def load_patient_data(input_path: str) -> Dict[str, Any]:
    """Load patient data from JSON file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_patient_data(data: Dict[str, Any]) -> List[str]:
    """Validate required fields in patient data."""
    errors = []
    required_sections = [
        'patient_info', 'admission_data', 'hospital_course',
        'discharge_status', 'medications', 'follow_up'
    ]
    
    for section in required_sections:
        if section not in data:
            errors.append(f"Missing required section: {section}")
    
    if 'patient_info' in data:
        required_info = ['name', 'gender', 'age', 'medical_record_number', 'department']
        for field in required_info:
            if field not in data['patient_info']:
                errors.append(f"Missing patient_info.{field}")
    
    return errors


def format_patient_info(info: Dict[str, Any]) -> str:
    """Format patient information section."""
    return f"""## 患者基本信息 / Patient Information

| 项目 / Item | 内容 / Value |
|------------|-------------|
| 姓名 / Name | {info.get('name', 'N/A')} |
| 性别 / Gender | {info.get('gender', 'N/A')} |
| 年龄 / Age | {info.get('age', 'N/A')} 岁 |
| 住院号 / MRN | {info.get('medical_record_number', 'N/A')} |
| 入院日期 / Admission Date | {info.get('admission_date', 'N/A')} |
| 出院日期 / Discharge Date | {info.get('discharge_date', 'N/A')} |
| 住院天数 / Length of Stay | {info.get('hospital_stay_days', 'N/A')} 天 |
| 科室 / Department | {info.get('department', 'N/A')} |
| 主管医师 / Attending Physician | {info.get('attending_physician', 'N/A')} |
"""


def format_admission_data(data: Dict[str, Any]) -> str:
    """Format admission information section."""
    diagnoses = data.get('admission_diagnosis', [])
    diagnosis_text = '\n'.join([f"- {d}" for d in diagnoses]) if diagnoses else '-'
    
    return f"""## 入院情况 / Admission Information

### 主诉 / Chief Complaint
{data.get('chief_complaint', 'N/A')}

### 现病史 / Present Illness History
{data.get('present_illness_history', 'N/A')}

### 既往史 / Past Medical History
{data.get('past_medical_history', 'N/A')}

### 入院查体 / Physical Examination
{data.get('physical_examination', 'N/A')}

### 入院诊断 / Admission Diagnosis
{diagnosis_text}
"""


def format_hospital_course(course: Dict[str, Any]) -> str:
    """Format hospital course section."""
    procedures = course.get('procedures_performed', [])
    procedures_text = '\n'.join([f"- {p}" for p in procedures]) if procedures else '-'
    
    complications = course.get('complications', [])
    complications_text = '\n'.join([f"- {c}" for c in complications]) if complications else '无 / None'
    
    consultations = course.get('consultations', [])
    consultations_text = '\n'.join([f"- {c}" for c in consultations]) if consultations else '-'
    
    return f"""## 住院诊疗经过 / Hospital Course

### 治疗经过 / Treatment Summary
{course.get('treatment_summary', 'N/A')}

### 重要检查结果 / Significant Findings
{course.get('significant_findings', 'N/A')}

### 实施手术/操作 / Procedures Performed
{procedures_text}

### 会诊记录 / Consultations
{consultations_text}

### 并发症 / Complications
{complications_text}
"""


def format_discharge_status(status: Dict[str, Any]) -> str:
    """Format discharge status section."""
    diagnoses = status.get('discharge_diagnosis', [])
    diagnosis_text = '\n'.join([f"- {d}" for d in diagnoses]) if diagnoses else '-'
    
    return f"""## 出院情况 / Discharge Status

### 出院诊断 / Discharge Diagnosis
{diagnosis_text}

### 出院时病情 / Discharge Condition
{status.get('discharge_condition', 'N/A')}
"""


def format_medications(meds: Dict[str, Any]) -> str:
    """Format discharge medications section."""
    medications = meds.get('discharge_medications', [])
    
    if not medications:
        return """## 出院带药 / Discharge Medications

无 / None
"""
    
    med_lines = []
    for i, med in enumerate(medications, 1):
        med_lines.append(
            f"{i}. **{med.get('name', 'N/A')}** | "
            f"剂量: {med.get('dosage', 'N/A')} | "
            f"频次: {med.get('frequency', 'N/A')} | "
            f"途径: {med.get('route', 'N/A')} | "
            f"疗程: {med.get('duration', 'N/A')}"
        )
    
    return f"""## 出院带药 / Discharge Medications

""" + '\n'.join(med_lines) + """

**重要提示**: 请遵医嘱按时服药，如有不适及时就诊。  
**Important**: Please take medications as prescribed. Seek medical attention if adverse effects occur.
"""


def format_follow_up(follow_up: Dict[str, Any]) -> str:
    """Format follow-up instructions section."""
    appointments = follow_up.get('follow_up_appointments', [])
    appointments_text = '\n'.join([f"- {a}" for a in appointments]) if appointments else '-'
    
    warning_signs = follow_up.get('warning_signs', [])
    warning_text = '\n'.join([f"- {w}" for w in warning_signs]) if warning_signs else '-'
    
    return f"""## 出院医嘱 / Discharge Instructions

### 随访安排 / Follow-up Appointments
{appointments_text}

### 注意事项 / Instructions
{follow_up.get('instructions', 'N/A')}

### 活动限制 / Activity Restrictions
{follow_up.get('activity_restrictions', 'N/A')}

### 饮食指导 / Diet Instructions
{follow_up.get('diet_instructions', 'N/A')}

### 警示症状（需立即就诊）/ Warning Signs (Seek Immediate Care)
{warning_text}
"""


def generate_summary(data: Dict[str, Any], language: str = 'zh') -> str:
    """Generate complete discharge summary."""
    patient_info = data.get('patient_info', {})
    admission_data = data.get('admission_data', {})
    hospital_course = data.get('hospital_course', {})
    discharge_status = data.get('discharge_status', {})
    medications = data.get('medications', {})
    follow_up = data.get('follow_up', {})
    
    # Calculate hospital stay if not provided
    if 'hospital_stay_days' not in patient_info and 'admission_date' in patient_info and 'discharge_date' in patient_info:
        try:
            admit = datetime.strptime(patient_info['admission_date'], '%Y-%m-%d')
            discharge = datetime.strptime(patient_info['discharge_date'], '%Y-%m-%d')
            patient_info['hospital_stay_days'] = (discharge - admit).days
        except (ValueError, TypeError):
            patient_info['hospital_stay_days'] = 'N/A'
    
    title = "出院小结 / DISCHARGE SUMMARY"
    disclaimer = """---

**⚠️ 重要声明 / IMPORTANT DISCLAIMER**

本文档由AI辅助系统生成，仅供参考。最终出院小结须经主管医师审核签字后方可生效。  
This document was generated by an AI-assisted system for reference only. The final discharge summary must be reviewed and signed by the attending physician before it becomes effective.

---
"""
    
    sections = [
        f"# {title}",
        disclaimer,
        format_patient_info(patient_info),
        format_admission_data(admission_data),
        format_hospital_course(hospital_course),
        format_discharge_status(discharge_status),
        format_medications(medications),
        format_follow_up(follow_up),
        """---

## 医师签字 / Physician Signature

| | |
|---|---|
| 主管医师 / Attending Physician | _________________________ |
| 签字日期 / Signature Date | _________________________ |
| 医师执照号 / License Number | _________________________ |

---

*本文档生成时间 / Document Generated: {timestamp}*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    
    return '\n\n'.join(sections)


def generate_structured_output(data: Dict[str, Any]) -> str:
    """Generate structured output format."""
    return generate_summary(data, 'zh')


def generate_json_output(data: Dict[str, Any]) -> str:
    """Generate JSON output format."""
    output = {
        "document_type": "discharge_summary",
        "generated_at": datetime.now().isoformat(),
        "requires_physician_review": True,
        "data": data
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Generate hospital discharge summaries from patient data'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to patient data JSON file'
    )
    parser.add_argument(
        '--output', '-o',
        default='discharge_summary.md',
        help='Output file path (default: discharge_summary.md)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['standard', 'structured', 'json'],
        default='standard',
        help='Output format (default: standard)'
    )
    parser.add_argument(
        '--language', '-l',
        choices=['zh', 'en'],
        default='zh',
        help='Output language (default: zh)'
    )
    
    args = parser.parse_args()
    
    # Load and validate data
    try:
        data = load_patient_data(args.input)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        return 1
    
    validation_errors = validate_patient_data(data)
    if validation_errors:
        print("Validation errors found:")
        for error in validation_errors:
            print(f"  - {error}")
        return 1
    
    # Generate output
    if args.format == 'json':
        output = generate_json_output(data)
    elif args.format == 'structured':
        output = generate_structured_output(data)
    else:
        output = generate_summary(data, args.language)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Discharge summary generated: {output_path.absolute()}")
    print("⚠️  WARNING: This document requires physician review before use.")
    
    return 0


if __name__ == '__main__':
    exit(main())
