#!/usr/bin/env python3
"""
Shift Handover Summarizer (ID: 168)
基于电子病历更新，生成交班摘要，强调本班次发生的关键事件
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class EventPriority(Enum):
    """事件优先级"""
    HIGH = "high"       # 🔴 高风险/紧急
    MEDIUM = "medium"   # 🟡 中等/需要注意
    LOW = "low"         # 🟢 低/常规


class RecordType(Enum):
    """病历记录类型"""
    VITAL_SIGNS = "vital_signs"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    EVENT = "event"
    NOTE = "note"


@dataclass
class VitalSigns:
    """生命体征数据"""
    heart_rate: Optional[int] = None
    blood_pressure: Optional[str] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    spo2: Optional[int] = None
    timestamp: Optional[str] = None


@dataclass
class KeyEvent:
    """关键事件"""
    timestamp: str
    type: str
    description: str
    severity: EventPriority
    action_taken: Optional[str] = None


@dataclass
class PatientSummary:
    """单个患者摘要"""
    patient_id: str
    patient_name: str
    bed_number: str
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    priority: EventPriority = EventPriority.LOW
    key_events: List[KeyEvent] = field(default_factory=list)
    vitals_summary: Dict[str, Any] = field(default_factory=dict)
    medication_summary: List[Dict] = field(default_factory=list)
    procedure_summary: List[Dict] = field(default_factory=list)
    pending_tasks: List[str] = field(default_factory=list)


@dataclass
class ShiftSummary:
    """班次摘要"""
    shift_period: Dict[str, str]
    generated_at: str
    total_patients: int
    critical_patients: int
    department: Optional[str] = None
    summary_text: str = ""
    patients: List[PatientSummary] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self)
        # 转换枚举值
        for patient in result.get('patients', []):
            if isinstance(patient.get('priority'), EventPriority):
                patient['priority'] = patient['priority'].value
            for event in patient.get('key_events', []):
                if isinstance(event.get('severity'), EventPriority):
                    event['severity'] = event['severity'].value
        return result

    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class ShiftHandoverSummarizer:
    """交班摘要生成器"""

    # 默认阈值配置
    DEFAULT_THRESHOLDS = {
        "high_heart_rate": 120,
        "low_heart_rate": 50,
        "high_systolic_bp": 180,
        "low_systolic_bp": 90,
        "high_temperature": 38.5,
        "low_spo2": 90
    }

    # 关键事件关键词
    EVENT_KEYWORDS = {
        EventPriority.HIGH: ["抢救", "心跳骤停", "呼吸困难", "大出血", "昏迷", "休克", "窒息"],
        EventPriority.MEDIUM: ["胸痛", "头晕", "恶心", "发热", "血压波动", "呕吐", "心悸"]
    }

    def __init__(
        self,
        shift_start: str,
        shift_end: str,
        department: Optional[str] = None,
        thresholds: Optional[Dict] = None,
        include_vitals: bool = True,
        include_medications: bool = True,
        include_procedures: bool = True,
        language: str = "zh-CN"
    ):
        self.shift_start = shift_start
        self.shift_end = shift_end
        self.department = department
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self.include_vitals = include_vitals
        self.include_medications = include_medications
        self.include_procedures = include_procedures
        self.language = language

    def generate_summary(self, patient_records: List[Dict]) -> ShiftSummary:
        """生成交班摘要"""
        patient_summaries = []
        critical_count = 0

        for record in patient_records:
            patient_summary = self._analyze_patient(record)
            patient_summaries.append(patient_summary)
            if patient_summary.priority == EventPriority.HIGH:
                critical_count += 1

        # 按优先级排序
        patient_summaries.sort(key=lambda x: (
            0 if x.priority == EventPriority.HIGH else
            1 if x.priority == EventPriority.MEDIUM else 2
        ))

        # 生成统计信息
        statistics = self._generate_statistics(patient_summaries)

        # 生成文本摘要
        summary_text = self._generate_summary_text(patient_summaries, statistics)

        return ShiftSummary(
            shift_period={
                "start": self.shift_start,
                "end": self.shift_end
            },
            generated_at=datetime.now().isoformat(),
            total_patients=len(patient_summaries),
            critical_patients=critical_count,
            department=self.department,
            summary_text=summary_text,
            patients=patient_summaries,
            statistics=statistics
        )

    def _analyze_patient(self, record: Dict) -> PatientSummary:
        """分析单个患者记录"""
        patient_id = record.get("patient_id", "")
        patient_name = record.get("patient_name", "")
        bed_number = record.get("bed_number", "")
        
        summary = PatientSummary(
            patient_id=patient_id,
            patient_name=patient_name,
            bed_number=bed_number,
            age=record.get("age"),
            gender=record.get("gender"),
            diagnosis=record.get("diagnosis", "")
        )

        records = record.get("records", [])
        key_events = []
        max_priority = EventPriority.LOW

        for rec in records:
            event = self._analyze_record(rec)
            if event:
                key_events.append(event)
                if self._priority_value(event.severity) > self._priority_value(max_priority):
                    max_priority = event.severity

            # 收集各类摘要信息
            rec_type = rec.get("type", "")
            if rec_type == RecordType.VITAL_SIGNS.value and self.include_vitals:
                self._collect_vitals(summary, rec)
            elif rec_type == RecordType.MEDICATION.value and self.include_medications:
                self._collect_medication(summary, rec)
            elif rec_type == RecordType.PROCEDURE.value and self.include_procedures:
                self._collect_procedure(summary, rec)

        summary.key_events = key_events
        summary.priority = max_priority
        summary.pending_tasks = self._generate_pending_tasks(summary)

        return summary

    def _analyze_record(self, record: Dict) -> Optional[KeyEvent]:
        """分析单条记录，提取关键事件"""
        rec_type = record.get("type", "")
        timestamp = record.get("timestamp", "")
        data = record.get("data", {})
        severity = record.get("severity", "")

        # 根据类型分析
        if rec_type == RecordType.EVENT.value:
            return self._analyze_event_record(record)
        elif rec_type == RecordType.VITAL_SIGNS.value:
            return self._analyze_vitals_record(record)
        elif rec_type == RecordType.PROCEDURE.value:
            return self._analyze_procedure_record(record)
        elif rec_type == RecordType.MEDICATION.value:
            return self._analyze_medication_record(record)

        return None

    def _analyze_event_record(self, record: Dict) -> Optional[KeyEvent]:
        """分析事件记录"""
        data = record.get("data", {})
        description = data.get("description", "")
        severity_str = record.get("severity", "medium")
        
        severity = EventPriority(severity_str) if severity_str in ["high", "medium", "low"] else EventPriority.MEDIUM
        
        # 根据关键词调整优先级
        if any(kw in description for kw in self.EVENT_KEYWORDS[EventPriority.HIGH]):
            severity = EventPriority.HIGH

        return KeyEvent(
            timestamp=record.get("timestamp", ""),
            type="事件",
            description=description,
            severity=severity,
            action_taken=data.get("action_taken", "")
        )

    def _analyze_vitals_record(self, record: Dict) -> Optional[KeyEvent]:
        """分析生命体征记录，检测异常"""
        data = record.get("data", {})
        abnormalities = []
        severity = EventPriority.LOW

        # 检查心率
        hr = data.get("heart_rate")
        if hr:
            if hr > self.thresholds["high_heart_rate"]:
                abnormalities.append(f"心率过快 ({hr} bpm)")
                severity = EventPriority.MEDIUM
            elif hr < self.thresholds["low_heart_rate"]:
                abnormalities.append(f"心率过慢 ({hr} bpm)")
                severity = EventPriority.MEDIUM

        # 检查血压
        bp = data.get("blood_pressure")
        if bp:
            try:
                systolic = int(bp.split("/")[0])
                if systolic > self.thresholds["high_systolic_bp"]:
                    abnormalities.append(f"血压偏高 ({bp})")
                    severity = EventPriority.MEDIUM
                elif systolic < self.thresholds["low_systolic_bp"]:
                    abnormalities.append(f"血压偏低 ({bp})")
                    severity = EventPriority.MEDIUM
            except:
                pass

        # 检查体温
        temp = data.get("temperature")
        if temp and temp > self.thresholds["high_temperature"]:
            abnormalities.append(f"发热 ({temp}°C)")
            severity = EventPriority.MEDIUM

        # 检查血氧
        spo2 = data.get("spo2")
        if spo2 and spo2 < self.thresholds["low_spo2"]:
            abnormalities.append(f"血氧偏低 ({spo2}%)")
            severity = EventPriority.HIGH

        if abnormalities:
            return KeyEvent(
                timestamp=record.get("timestamp", ""),
                type="生命体征异常",
                description="; ".join(abnormalities),
                severity=severity
            )
        return None

    def _analyze_procedure_record(self, record: Dict) -> Optional[KeyEvent]:
        """分析操作/检查记录"""
        data = record.get("data", {})
        procedure_name = data.get("procedure_name", "")
        result = data.get("result", "")

        # 检查是否有异常结果关键词
        if result and any(kw in result for kw in ["异常", "阳性", "危急", "严重"]):
            return KeyEvent(
                timestamp=record.get("timestamp", ""),
                type="检查结果异常",
                description=f"{procedure_name}: {result}",
                severity=EventPriority.MEDIUM
            )
        return None

    def _analyze_medication_record(self, record: Dict) -> Optional[KeyEvent]:
        """分析用药记录"""
        # 目前仅记录用药信息，不作为关键事件
        return None

    def _collect_vitals(self, summary: PatientSummary, record: Dict):
        """收集生命体征信息"""
        data = record.get("data", {})
        timestamp = record.get("timestamp", "")
        
        if "latest_vitals" not in summary.vitals_summary:
            summary.vitals_summary["latest_vitals"] = {}
            summary.vitals_summary["latest_timestamp"] = timestamp

        summary.vitals_summary["latest_vitals"].update(data)

    def _collect_medication(self, summary: PatientSummary, record: Dict):
        """收集用药信息"""
        data = record.get("data", {})
        summary.medication_summary.append({
            "timestamp": record.get("timestamp", ""),
            **data
        })

    def _collect_procedure(self, summary: PatientSummary, record: Dict):
        """收集操作信息"""
        data = record.get("data", {})
        summary.procedure_summary.append({
            "timestamp": record.get("timestamp", ""),
            **data
        })

    def _generate_pending_tasks(self, summary: PatientSummary) -> List[str]:
        """生成待办事项建议"""
        tasks = []
        
        # 根据关键事件生成待办
        for event in summary.key_events:
            if event.severity == EventPriority.HIGH:
                tasks.append(f"持续监测: {event.description}")
        
        # 根据生命体征生成待办
        vitals = summary.vitals_summary.get("latest_vitals", {})
        if vitals.get("spo2", 100) < self.thresholds["low_spo2"]:
            tasks.append("加强氧疗监测")
        
        # 常规待办
        if summary.diagnosis:
            tasks.append(f"观察{summary.diagnosis}相关症状")
        
        if not tasks:
            tasks.append("常规监护")
        
        return tasks

    def _generate_statistics(self, summaries: List[PatientSummary]) -> Dict:
        """生成统计信息"""
        stats = {
            "new_admissions": 0,
            "transfers_out": 0,
            "resuscitations": 0,
            "surgeries": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0
        }

        for summary in summaries:
            if summary.priority == EventPriority.HIGH:
                stats["high_priority"] += 1
            elif summary.priority == EventPriority.MEDIUM:
                stats["medium_priority"] += 1
            else:
                stats["low_priority"] += 1

            # 统计抢救事件
            for event in summary.key_events:
                if "抢救" in event.description or "心跳骤停" in event.description:
                    stats["resuscitations"] += 1

        return stats

    def _generate_summary_text(self, summaries: List[PatientSummary], stats: Dict) -> str:
        """生成文本格式摘要"""
        lines = []
        
        # 标题
        dept_str = f"【{self.department}】" if self.department else ""
        lines.append(f"{dept_str}交班摘要 {self.shift_start[:10]} {self.shift_start[11:16]} - {self.shift_end[11:16]}")
        lines.append("")

        # 重点关注患者
        high_priority = [s for s in summaries if s.priority == EventPriority.HIGH]
        medium_priority = [s for s in summaries if s.priority == EventPriority.MEDIUM]
        low_priority = [s for s in summaries if s.priority == EventPriority.LOW]

        if high_priority:
            lines.append("【重点关注患者】")
            for s in high_priority:
                lines.extend(self._format_patient_summary(s, "🔴"))
            lines.append("")

        if medium_priority:
            lines.append("【需注意患者】")
            for s in medium_priority:
                lines.extend(self._format_patient_summary(s, "🟡"))
            lines.append("")

        if low_priority:
            bed_numbers = [s.bed_number for s in low_priority]
            lines.append(f"【病情平稳患者】")
            lines.append(f"{', '.join(bed_numbers)}床: 病情平稳，常规治疗进行中")
            lines.append("")

        # 统计信息
        lines.append("【本班次总览】")
        lines.append(f"- 患者总数: {len(summaries)}人")
        lines.append(f"- 重点关注: {stats['high_priority']}人")
        lines.append(f"- 抢救次数: {stats['resuscitations']}次")
        lines.append(f"- 手术台数: {stats['surgeries']}台")

        return "\n".join(lines)

    def _format_patient_summary(self, summary: PatientSummary, icon: str) -> List[str]:
        """格式化单个患者摘要"""
        lines = []
        
        # 基本信息
        info_parts = [f"{summary.bed_number}床", summary.patient_name]
        if summary.gender:
            info_parts.append(f"({summary.gender}")
            if summary.age:
                info_parts[-1] += f", {summary.age}岁"
            info_parts[-1] += ")"
        if summary.diagnosis:
            info_parts.append(f"- {summary.diagnosis}")
        
        lines.append(f"{icon} {' '.join(info_parts)}")

        # 关键事件
        for event in summary.key_events:
            time_str = event.timestamp[11:16] if len(event.timestamp) > 16 else ""
            event_icon = "⚠️" if event.severity == EventPriority.HIGH else "⚡"
            lines.append(f"   {event_icon} {time_str} {event.type}: {event.description}")
            if event.action_taken:
                lines.append(f"      → 处理: {event.action_taken}")

        # 生命体征摘要
        if self.include_vitals and summary.vitals_summary.get("latest_vitals"):
            vitals = summary.vitals_summary["latest_vitals"]
            vital_strs = []
            if vitals.get("blood_pressure"):
                vital_strs.append(f"BP {vitals['blood_pressure']}")
            if vitals.get("heart_rate"):
                vital_strs.append(f"HR {vitals['heart_rate']}")
            if vitals.get("spo2"):
                vital_strs.append(f"SpO₂ {vitals['spo2']}%")
            if vital_strs:
                lines.append(f"   💓 生命体征: {', '.join(vital_strs)}")

        # 待办事项
        if summary.pending_tasks:
            lines.append(f"   📋 待办: {'; '.join(summary.pending_tasks[:2])}")

        return lines

    @staticmethod
    def _priority_value(priority: EventPriority) -> int:
        """获取优先级数值"""
        return {"high": 3, "medium": 2, "low": 1}.get(priority.value, 0)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="Shift Handover Summarizer")
    parser.add_argument("--records", "-r", required=True, help="病历记录 JSON 文件路径")
    parser.add_argument("--shift-start", "-s", required=True, help="班次开始时间 (ISO 8601)")
    parser.add_argument("--shift-end", "-e", required=True, help="班次结束时间 (ISO 8601)")
    parser.add_argument("--department", "-d", help="科室名称")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--no-vitals", action="store_true", help="不包含生命体征")
    parser.add_argument("--no-medications", action="store_true", help="不包含用药信息")
    parser.add_argument("--no-procedures", action="store_true", help="不包含操作信息")

    args = parser.parse_args()

    # 读取病历记录
    with open(args.records, "r", encoding="utf-8") as f:
        patient_records = json.load(f)

    # 创建生成器
    summarizer = ShiftHandoverSummarizer(
        shift_start=args.shift_start,
        shift_end=args.shift_end,
        department=args.department,
        include_vitals=not args.no_vitals,
        include_medications=not args.no_medications,
        include_procedures=not args.no_procedures
    )

    # 生成摘要
    summary = summarizer.generate_summary(patient_records)

    # 输出结果
    output = {
        "success": True,
        "shift_summary": summary.to_dict()
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"摘要已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
