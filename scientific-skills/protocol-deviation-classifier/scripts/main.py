#!/usr/bin/env python3
"""
Protocol Deviation Classifier
临床试验方案偏离分类工具

基于GCP/ICH E6指导原则，自动判定偏差属于"重大偏差"还是"微小偏差"。
Technical: Risk-based quality management, GCP compliance assessment, deviation classification
"""

import argparse
import json
import sys
import re
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class Classification(Enum):
    """偏差分类枚举"""
    MAJOR = "major"
    MINOR = "minor"
    CRITICAL = "critical"
    
    def __str__(self):
        mapping = {
            Classification.MAJOR: "重大偏差",
            Classification.MINOR: "微小偏差",
            Classification.CRITICAL: "关键偏差"
        }
        return mapping.get(self, self.value)
    
    @property
    def en_name(self):
        mapping = {
            Classification.MAJOR: "Major Deviation",
            Classification.MINOR: "Minor Deviation",
            Classification.CRITICAL: "Critical Deviation"
        }
        return mapping.get(self, self.value.title())


class RiskLevel(Enum):
    """风险等级枚举"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    def __str__(self):
        mapping = {
            RiskLevel.NONE: "无",
            RiskLevel.LOW: "低",
            RiskLevel.MEDIUM: "中等",
            RiskLevel.HIGH: "高"
        }
        return mapping.get(self, self.value)
    
    @property
    def score(self):
        """返回风险分数用于计算"""
        scores = {
            RiskLevel.NONE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3
        }
        return scores.get(self, 0)


@dataclass
class DeviationEvent:
    """方案偏离事件数据类"""
    id: str = ""
    description: str = ""
    deviation_type: str = ""
    occurrence_date: Optional[str] = None
    site_id: Optional[str] = None
    subject_id: Optional[str] = None
    safety_impact: RiskLevel = RiskLevel.NONE
    data_impact: RiskLevel = RiskLevel.NONE
    scientific_impact: RiskLevel = RiskLevel.NONE
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviationEvent':
        """从字典创建事件"""
        def parse_risk(value):
            if isinstance(value, str):
                try:
                    return RiskLevel(value.lower())
                except ValueError:
                    return RiskLevel.NONE
            return RiskLevel.NONE
        
        factors = data.get('severity_factors', {})
        return cls(
            id=data.get('id', ''),
            description=data.get('description', ''),
            deviation_type=data.get('type', data.get('deviation_type', '')),
            occurrence_date=data.get('occurrence_date'),
            site_id=data.get('site_id'),
            subject_id=data.get('subject_id'),
            safety_impact=parse_risk(factors.get('safety_impact', 'none')),
            data_impact=parse_risk(factors.get('data_impact', 'none')),
            scientific_impact=parse_risk(factors.get('scientific_impact', 'none'))
        )


@dataclass
class ClassificationResult:
    """分类结果数据类"""
    id: str
    classification: Classification
    confidence: float
    rationale: str
    safety_risk: RiskLevel
    data_integrity_risk: RiskLevel
    scientific_validity_risk: RiskLevel
    risk_score: int
    regulatory_basis: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    key_indicators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "classification": str(self.classification),
            "classification_en": self.classification.en_name,
            "confidence": round(self.confidence, 2),
            "rationale": self.rationale,
            "risk_factors": {
                "safety_risk": str(self.safety_risk),
                "data_integrity_risk": str(self.data_integrity_risk),
                "scientific_validity_risk": str(self.scientific_validity_risk)
            },
            "risk_score": self.risk_score,
            "regulatory_basis": self.regulatory_basis,
            "recommended_actions": self.recommended_actions,
            "key_indicators": self.key_indicators
        }


class DeviationClassifier:
    """
    方案偏离分类器
    
    基于GCP/ICH E6指导原则，自动判定临床试验偏差的严重程度。
    """
    
    # 重大偏差关键词模式（中英文）
    MAJOR_INDICATORS = {
        'informed_consent': [
            r'知情同意', r'未获得.*同意', r'同意书', r'informed consent',
            r'未签署', r'consent', r'signed.*consent'
        ],
        'eligibility': [
            r'入选标准', r'排除标准', r'不符合.*入组', r'eligibility',
            r'inclusion.*criteria', r'exclusion.*criteria', r'ineligible'
        ],
        'dosing': [
            r'超剂量', r'双倍剂量', r'overdose', r'过量', r'错误.*剂量',
            r'wrong dose', r'double dose', r'dosing error'
        ],
        'concomitant': [
            r'合并用药', r'禁忌.*用药', r'concomitant', r'prohibited medication',
            r'forbidden drug'
        ],
        'randomization': [
            r'随机化.*错误', r'错.*随机', r'randomization error',
            r'wrong randomization'
        ],
        'safety_reporting': [
            r'SAE', r'SUSAR', r'安全性.*报告', r'漏报', r'延迟报告',
            r'serious adverse event', r'safety reporting'
        ],
        'blinding': [
            r'破盲', r'unblind', r'破盲.*未', r'未授权.*破盲'
        ],
        'data_integrity': [
            r'伪造', r'篡改', r'数据.*虚假', r'falsified',
            r'fabricated', r'数据造假'
        ],
        'critical_procedures': [
            r'关键.*未执行', r'未.*关键', r'遗漏.*主要终点',
            r'primary endpoint.*missed', r'critical procedure'
        ]
    }
    
    # 微小偏差关键词模式
    MINOR_INDICATORS = {
        'visit_window': [
            r'访视.*延迟', r'访视.*提前', r'visit.*window',
            r'访视.*[12].*天', r'visit.*[12].*day'
        ],
        'sample_collection': [
            r'样本.*延迟', r'采样.*时间', r'sample.*delay',
            r'非关键.*样本', r'non-critical sample'
        ],
        'questionnaire': [
            r'问卷', r'日记卡', r'questionnaire', r'diary card',
            r'QOL', r'生活质量'
        ],
        'documentation': [
            r'签名.*延迟', r'文档.*缺失', r'document.*missing',
            r'signature.*delay', r'记录.*延迟'
        ],
        'non_critical': [
            r'非关键', r'次要', r'轻微', r'non-critical',
            r'minor', r'slight'
        ]
    }
    
    # 法规依据
    REGULATORY_BASIS = {
        'major': [
            "ICH E6(R2) Section 4.5 - Subject Safety",
            "ICH E6(R2) Section 4.9 - Informed Consent",
            "GCP Section 6.2 - Subject Rights",
            "FDA 21 CFR Part 312.60 - General Investigator Obligations"
        ],
        'minor': [
            "ICH E6(R2) Section 4.6 - Investigational Product",
            "ICH E6(R2) Section 5.1 - Trial Management",
            "GCP Section 6.4.4 - Protocol Compliance"
        ],
        'critical': [
            "ICH E6(R2) Section 2.13 - Data Integrity",
            "ICH E6(R2) Section 4.1.5 - Fraud Prevention",
            "FDA 21 CFR Part 312.70 - Disqualification of Investigators"
        ]
    }
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.major_patterns = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self.MAJOR_INDICATORS.items()
        }
        self.minor_patterns = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self.MINOR_INDICATORS.items()
        }
    
    def classify(
        self,
        description: str,
        deviation_type: str = "",
        event_id: str = "",
        safety_impact: Optional[RiskLevel] = None,
        data_impact: Optional[RiskLevel] = None,
        scientific_impact: Optional[RiskLevel] = None
    ) -> ClassificationResult:
        """
        分类单个偏差事件
        
        Args:
            description: 偏差描述
            deviation_type: 偏差类型
            event_id: 事件ID
            safety_impact: 安全影响级别（如已知）
            data_impact: 数据完整性影响级别（如已知）
            scientific_impact: 科学性影响级别（如已知）
        
        Returns:
            ClassificationResult: 分类结果
        """
        # 如果没有提供影响级别，则基于描述自动判断
        if safety_impact is None:
            safety_impact = self._assess_safety_impact(description, deviation_type)
        if data_impact is None:
            data_impact = self._assess_data_impact(description, deviation_type)
        if scientific_impact is None:
            scientific_impact = self._assess_scientific_impact(description, deviation_type)
        
        # 计算风险分数
        risk_score = (
            safety_impact.score * 3 +
            data_impact.score * 2 +
            scientific_impact.score * 2
        )
        
        # 应用分类规则
        classification, confidence = self._apply_classification_rules(
            safety_impact, data_impact, scientific_impact, risk_score, description
        )
        
        # 生成分类理由
        rationale = self._generate_rationale(
            classification, safety_impact, data_impact, scientific_impact, description
        )
        
        # 获取关键指标
        key_indicators = self._extract_key_indicators(description, deviation_type)
        
        # 获取法规依据
        regulatory_basis = self._get_regulatory_basis(classification, description)
        
        # 生成建议措施
        recommended_actions = self._get_recommended_actions(classification)
        
        return ClassificationResult(
            id=event_id or self._generate_event_id(),
            classification=classification,
            confidence=confidence,
            rationale=rationale,
            safety_risk=safety_impact,
            data_integrity_risk=data_impact,
            scientific_validity_risk=scientific_impact,
            risk_score=risk_score,
            regulatory_basis=regulatory_basis,
            recommended_actions=recommended_actions,
            key_indicators=key_indicators
        )
    
    def classify_batch(self, events: List[Dict]) -> List[ClassificationResult]:
        """
        批量分类偏差事件
        
        Args:
            events: 偏差事件字典列表
        
        Returns:
            List[ClassificationResult]: 分类结果列表
        """
        results = []
        for event_data in events:
            event = DeviationEvent.from_dict(event_data)
            result = self.classify(
                description=event.description,
                deviation_type=event.deviation_type,
                event_id=event.id,
                safety_impact=event.safety_impact,
                data_impact=event.data_impact,
                scientific_impact=event.scientific_impact
            )
            results.append(result)
        return results
    
    def _assess_safety_impact(self, description: str, deviation_type: str) -> RiskLevel:
        """评估对受试者安全的影响"""
        text = f"{description} {deviation_type}".lower()
        
        # 高安全影响关键词
        high_risk = [
            r'overdose', r'超剂量', r'双倍剂量', r'禁忌用药', r'过敏反应',
            r'严重不良事件', r'sae', r'死亡', r'危及生命', r'住院',
            r'death', r'life-threatening', r'hospitalization'
        ]
        
        # 中等安全影响关键词
        medium_risk = [
            r'不良反应', r'副作用', r'adverse event', r'合并用药',
            r'concomitant', r'药物相互作用', r'drug interaction',
            r'剂量调整', r'dose adjustment'
        ]
        
        for pattern in high_risk:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.HIGH
        
        for pattern in medium_risk:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.MEDIUM
        
        # 如果涉及知情同意但未涉及具体伤害
        if re.search(r'知情同意|consent', text, re.IGNORECASE):
            return RiskLevel.HIGH
        
        return RiskLevel.NONE
    
    def _assess_data_impact(self, description: str, deviation_type: str) -> RiskLevel:
        """评估对数据完整性的影响"""
        text = f"{description} {deviation_type}".lower()
        
        # 高数据影响
        high_patterns = [
            r'伪造|篡改|虚假|falsif|fabricat',
            r'数据.*丢失|data.*lost',
            r'关键.*数据.*缺失|critical.*data.*missing'
        ]
        
        # 中等数据影响
        medium_patterns = [
            r'主要终点|primary endpoint',
            r'关键访视|critical visit',
            r'未.*评估|not.*assess'
        ]
        
        for pattern in high_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.HIGH
        
        for pattern in medium_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _assess_scientific_impact(self, description: str, deviation_type: str) -> RiskLevel:
        """评估对试验科学性的影响"""
        text = f"{description} {deviation_type}".lower()
        
        # 检查是否影响主要终点或随机化
        high_patterns = [
            r'随机化.*错误|错.*随机|randomiz',
            r'主要终点|primary endpoint',
            r'入组.*错误|错.*入组|不符合.*入组|ineligible'
        ]
        
        # 中等影响
        medium_patterns = [
            r'访视.*缺失|missed visit',
            r'疗效.*评估|efficacy assessment',
            r'破盲|unblind'
        ]
        
        for pattern in high_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.HIGH
        
        for pattern in medium_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return RiskLevel.MEDIUM
        
        return RiskLevel.NONE
    
    def _apply_classification_rules(
        self,
        safety_impact: RiskLevel,
        data_impact: RiskLevel,
        scientific_impact: RiskLevel,
        risk_score: int,
        description: str
    ) -> Tuple[Classification, float]:
        """
        应用分类规则
        
        分类规则:
        - 任一维度为 High → 重大偏差
        - 安全维度为 Medium 且数据/科学任一 Medium+ → 重大偏差
        - 涉及知情同意问题 → 重大偏差
        - 涉及数据伪造 → 关键偏差
        - 其他情况 → 微小偏差
        """
        text = description.lower()
        
        # 检查是否为关键偏差（数据造假）
        if re.search(r'伪造|篡改|虚假|falsif|fabricat', text):
            return Classification.CRITICAL, 0.98
        
        # 检查是否为重大偏差
        if safety_impact == RiskLevel.HIGH:
            return Classification.MAJOR, 0.95
        
        if data_impact == RiskLevel.HIGH or scientific_impact == RiskLevel.HIGH:
            return Classification.MAJOR, 0.90
        
        if safety_impact == RiskLevel.MEDIUM and (
            data_impact.score >= 2 or scientific_impact.score >= 2
        ):
            return Classification.MAJOR, 0.85
        
        # 检查知情同意相关问题
        if re.search(r'知情同意|未获得.*同意|consent', text, re.IGNORECASE):
            if not re.search(r'非关键|轻微|延迟|delay', text, re.IGNORECASE):
                return Classification.MAJOR, 0.92
        
        # 其他情况为微小偏差
        if risk_score <= 4:
            confidence = 0.90 - (risk_score * 0.05)
        else:
            confidence = 0.70
        
        return Classification.MINOR, max(0.65, confidence)
    
    def _generate_rationale(
        self,
        classification: Classification,
        safety_impact: RiskLevel,
        data_impact: RiskLevel,
        scientific_impact: RiskLevel,
        description: str
    ) -> str:
        """生成分类理由"""
        reasons = []
        
        if classification == Classification.CRITICAL:
            reasons.append("涉及数据伪造或篡改，严重影响试验数据的可信性。")
        elif classification == Classification.MAJOR:
            reasons.append("该偏差具有以下高风险特征：")
            if safety_impact == RiskLevel.HIGH:
                reasons.append("- 严重影响受试者安全")
            if data_impact == RiskLevel.HIGH:
                reasons.append("- 严重损害数据完整性")
            if scientific_impact == RiskLevel.HIGH:
                reasons.append("- 严重损害试验科学性")
            if safety_impact == RiskLevel.MEDIUM:
                reasons.append("- 对受试者安全有中等影响")
            
            # 检查知情同意
            if re.search(r'知情同意|consent', description, re.IGNORECASE):
                reasons.append("- 涉及知情同意程序违规")
        else:
            reasons.append("该偏差具有以下特征：")
            if safety_impact == RiskLevel.NONE:
                reasons.append("- 不影响受试者安全")
            if data_impact == RiskLevel.LOW:
                reasons.append("- 对数据完整性影响轻微")
            if scientific_impact == RiskLevel.NONE:
                reasons.append("- 不影响试验科学性")
            
            # 检查是否为轻微时间延迟
            if re.search(r'延迟|delay|推后|postpone', description, re.IGNORECASE):
                reasons.append("- 仅为程序性延迟，不影响试验核心要素")
        
        return "\n".join(reasons)
    
    def _extract_key_indicators(self, description: str, deviation_type: str) -> List[str]:
        """提取关键指标"""
        indicators = []
        text = f"{description} {deviation_type}".lower()
        
        # 检查重大偏差指标
        for category, patterns in self.major_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    indicator_map = {
                        'informed_consent': '知情同意问题',
                        'eligibility': '入选/排除标准违规',
                        'dosing': '给药/剂量问题',
                        'concomitant': '合并用药违规',
                        'randomization': '随机化问题',
                        'safety_reporting': '安全性报告问题',
                        'blinding': '盲法违规',
                        'data_integrity': '数据完整性问题',
                        'critical_procedures': '关键程序遗漏'
                    }
                    ind = indicator_map.get(category, category)
                    if ind not in indicators:
                        indicators.append(ind)
                    break
        
        # 检查微小偏差指标
        for category, patterns in self.minor_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    indicator_map = {
                        'visit_window': '访视时间窗偏差',
                        'sample_collection': '样本采集偏差',
                        'questionnaire': '问卷/日记卡偏差',
                        'documentation': '文档/签名延迟',
                        'non_critical': '非关键程序偏差'
                    }
                    ind = indicator_map.get(category, category)
                    if ind not in indicators:
                        indicators.append(ind)
                    break
        
        return indicators[:5]  # 最多返回5个指标
    
    def _get_regulatory_basis(self, classification: Classification, description: str) -> List[str]:
        """获取法规依据"""
        basis = []
        text = description.lower()
        
        if classification == Classification.CRITICAL:
            basis = self.REGULATORY_BASIS['critical'].copy()
        elif classification == Classification.MAJOR:
            basis = self.REGULATORY_BASIS['major'].copy()
            
            # 根据描述添加特定法规
            if re.search(r'知情同意|consent', text, re.IGNORECASE):
                basis.append("ICH E6(R2) Section 4.8 - Informed Consent Requirements")
            if re.search(r'随机化|randomiz', text, re.IGNORECASE):
                basis.append("ICH E9 - Statistical Principles for Clinical Trials")
        else:
            basis = self.REGULATORY_BASIS['minor'].copy()
        
        return basis
    
    def _get_recommended_actions(self, classification: Classification) -> List[str]:
        """获取建议措施"""
        if classification == Classification.CRITICAL:
            return [
                "立即通知申办方和伦理委员会",
                "启动根本原因调查",
                "实施纠正和预防措施(CAPA)",
                "考虑将研究者列入黑名单",
                "评估对试验整体数据的影响"
            ]
        elif classification == Classification.MAJOR:
            return [
                "记录在偏差日志中",
                "24小时内报告申办方",
                "报告伦理委员会（如方案要求）",
                "评估是否需要采取补救措施",
                "跟踪趋势，评估是否为系统性问题"
            ]
        else:
            return [
                "记录在偏差日志中",
                "跟踪趋势",
                "在研究中心层面解决",
                "定期汇总报告（如季度）"
            ]
    
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"DEV-{timestamp}"
    
    def generate_report(self, results: List[ClassificationResult]) -> Dict:
        """
        生成偏差分类报告
        
        Args:
            results: 分类结果列表
        
        Returns:
            Dict: 报告字典
        """
        if not results:
            return {"error": "No results to report"}
        
        total = len(results)
        major_count = sum(1 for r in results if r.classification == Classification.MAJOR)
        minor_count = sum(1 for r in results if r.classification == Classification.MINOR)
        critical_count = sum(1 for r in results if r.classification == Classification.CRITICAL)
        
        # 汇总各类型偏差
        by_category = {}
        for result in results:
            for indicator in result.key_indicators:
                by_category[indicator] = by_category.get(indicator, 0) + 1
        
        return {
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_deviations": total,
                "critical_count": critical_count,
                "major_count": major_count,
                "minor_count": minor_count,
                "major_rate": round(major_count / total * 100, 1) if total > 0 else 0,
                "minor_rate": round(minor_count / total * 100, 1) if total > 0 else 0
            },
            "category_breakdown": by_category,
            "critical_deviations": [
                r.to_dict() for r in results 
                if r.classification == Classification.CRITICAL
            ],
            "major_deviations": [
                r.to_dict() for r in results 
                if r.classification == Classification.MAJOR
            ],
            "minor_deviations": [
                r.to_dict() for r in results 
                if r.classification == Classification.MINOR
            ],
            "recommendations": self._generate_summary_recommendations(results)
        }
    
    def _generate_summary_recommendations(self, results: List[ClassificationResult]) -> List[str]:
        """生成汇总建议"""
        recommendations = []
        
        critical_count = sum(1 for r in results if r.classification == Classification.CRITICAL)
        major_count = sum(1 for r in results if r.classification == Classification.MAJOR)
        total = len(results)
        
        if critical_count > 0:
            recommendations.append(
                f"⚠️ 发现{critical_count}起关键偏差，建议立即进行根本原因分析"
            )
        
        if total > 0:
            major_rate = major_count / total * 100
            if major_rate > 20:
                recommendations.append(
                    f"重大偏差率({major_rate:.1f}%)偏高，建议加强研究中心培训"
                )
            elif major_rate > 10:
                recommendations.append(
                    f"重大偏差率({major_rate:.1f}%)中等，建议密切关注"
                )
        
        # 检查趋势
        safety_issues = sum(
            1 for r in results 
            if r.safety_risk in [RiskLevel.HIGH, RiskLevel.MEDIUM]
        )
        if safety_issues > 3:
            recommendations.append(
                f"发现{safety_issues}起涉及安全问题的偏差，建议评估受试者保护措施"
            )
        
        if not recommendations:
            recommendations.append("偏差控制总体良好，建议继续保持")
        
        return recommendations


def main():
    """CLI入口点"""
    parser = argparse.ArgumentParser(
        description="Protocol Deviation Classifier - 临床试验方案偏离分类工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分类单个偏差
  python scripts/main.py classify -d "受试者访视延迟2天"
  
  # 从文件批量分类
  python scripts/main.py batch -i deviations.json -o report.json
  
  # 交互式分类
  python scripts/main.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # classify 命令
    classify_parser = subparsers.add_parser("classify", help="分类单个偏差")
    classify_parser.add_argument("-d", "--description", required=True, help="偏差描述")
    classify_parser.add_argument("-t", "--type", default="", help="偏差类型")
    classify_parser.add_argument("--id", default="", help="事件ID")
    classify_parser.add_argument("--safety-impact", 
                                 choices=["none", "low", "medium", "high"],
                                 default="none", help="安全影响级别")
    classify_parser.add_argument("--data-impact",
                                 choices=["none", "low", "medium", "high"],
                                 default="low", help="数据完整性影响级别")
    classify_parser.add_argument("--scientific-impact",
                                 choices=["none", "low", "medium", "high"],
                                 default="none", help="科学性影响级别")
    classify_parser.add_argument("-o", "--output", choices=["json", "table"], 
                                 default="table", help="输出格式")
    
    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量分类")
    batch_parser.add_argument("-i", "--input", required=True, help="输入JSON文件路径")
    batch_parser.add_argument("-o", "--output", default="", help="输出文件路径")
    batch_parser.add_argument("--format", choices=["json", "report"],
                              default="json", help="输出格式")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成汇总报告")
    report_parser.add_argument("-i", "--input", required=True, help="分类结果JSON文件")
    
    # interactive 命令
    subparsers.add_parser("interactive", help="交互式分类")
    
    # demo 命令
    subparsers.add_parser("demo", help="运行示例分类")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    classifier = DeviationClassifier()
    
    try:
        if args.command == "classify":
            # 解析影响级别
            safety = RiskLevel(args.safety_impact)
            data = RiskLevel(args.data_impact)
            scientific = RiskLevel(args.scientific_impact)
            
            result = classifier.classify(
                description=args.description,
                deviation_type=args.type,
                event_id=args.id,
                safety_impact=safety,
                data_impact=data,
                scientific_impact=scientific
            )
            
            if args.output == "json":
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                _print_table_result(result)
        
        elif args.command == "batch":
            # 读取输入文件
            with open(args.input, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            results = classifier.classify_batch(events)
            
            if args.format == "report":
                report = classifier.generate_report(results)
                output = report
            else:
                output = [r.to_dict() for r in results]
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(output, f, ensure_ascii=False, indent=2)
                print(f"结果已保存至: {args.output}")
            else:
                print(json.dumps(output, ensure_ascii=False, indent=2))
        
        elif args.command == "report":
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 假设输入是分类结果列表
            if isinstance(data, list):
                # 转换为ClassificationResult对象
                results = []
                for item in data:
                    result = ClassificationResult(
                        id=item.get('id', ''),
                        classification=Classification(item.get('classification_en', '').lower().split()[0]),
                        confidence=item.get('confidence', 0),
                        rationale=item.get('rationale', ''),
                        safety_risk=RiskLevel.NONE,
                        data_integrity_risk=RiskLevel.NONE,
                        scientific_validity_risk=RiskLevel.NONE,
                        risk_score=item.get('risk_score', 0),
                        regulatory_basis=item.get('regulatory_basis', []),
                        recommended_actions=item.get('recommended_actions', []),
                        key_indicators=item.get('key_indicators', [])
                    )
                    results.append(result)
                
                report = classifier.generate_report(results)
                print(json.dumps(report, ensure_ascii=False, indent=2))
        
        elif args.command == "interactive":
            _run_interactive(classifier)
        
        elif args.command == "demo":
            _run_demo(classifier)
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


def _print_table_result(result: ClassificationResult):
    """打印表格格式的结果"""
    print("\n" + "=" * 60)
    print("方案偏离分类结果")
    print("=" * 60)
    print(f"{'事件ID:':<20} {result.id}")
    print(f"{'分类结果:':<20} {result.classification} ({result.classification.en_name})")
    print(f"{'置信度:':<20} {result.confidence*100:.1f}%")
    print(f"{'风险分数:':<20} {result.risk_score}")
    print("-" * 60)
    print("风险评估:")
    print(f"  - 受试者安全: {result.safety_risk}")
    print(f"  - 数据完整性: {result.data_integrity_risk}")
    print(f"  - 试验科学性: {result.scientific_validity_risk}")
    print("-" * 60)
    print("分类理由:")
    print(result.rationale)
    if result.key_indicators:
        print("-" * 60)
        print("关键指标:")
        for indicator in result.key_indicators:
            print(f"  • {indicator}")
    print("-" * 60)
    print("建议措施:")
    for action in result.recommended_actions:
        print(f"  • {action}")
    print("=" * 60)


def _run_interactive(classifier: DeviationClassifier):
    """运行交互式分类"""
    print("\n" + "=" * 60)
    print("方案偏离分类器 - 交互模式")
    print("=" * 60)
    print("输入 'quit' 或 'q' 退出\n")
    
    while True:
        print("\n" + "-" * 40)
        description = input("请输入偏差描述: ").strip()
        
        if description.lower() in ['quit', 'q', 'exit']:
            print("再见!")
            break
        
        if not description:
            print("描述不能为空，请重新输入。")
            continue
        
        deviation_type = input("请输入偏差类型 (可选): ").strip()
        
        print("\n正在分析...")
        result = classifier.classify(
            description=description,
            deviation_type=deviation_type
        )
        
        _print_table_result(result)


def _run_demo(classifier: DeviationClassifier):
    """运行示例分类"""
    demo_cases = [
        {
            "id": "DEV-001",
            "description": "受试者访视延迟2天进行",
            "type": "访视窗口"
        },
        {
            "id": "DEV-002",
            "description": "未获得知情同意即采集血样",
            "type": "知情同意"
        },
        {
            "id": "DEV-003",
            "description": "受试者误服双倍剂量研究药物",
            "type": "给药错误"
        },
        {
            "id": "DEV-004",
            "description": "生活质量问卷延迟3天提交",
            "type": "数据收集"
        },
        {
            "id": "DEV-005",
            "description": "不符合入选标准的受试者被入组（年龄超限）",
            "type": "入选标准"
        }
    ]
    
    print("\n" + "=" * 60)
    print("方案偏离分类器 - 示例运行")
    print("=" * 60)
    
    results = []
    for case in demo_cases:
        print(f"\n【案例 {case['id']}】")
        print(f"描述: {case['description']}")
        print(f"类型: {case['type']}")
        
        result = classifier.classify(
            description=case['description'],
            deviation_type=case['type'],
            event_id=case['id']
        )
        results.append(result)
        
        print(f"→ 分类结果: {result.classification} (置信度: {result.confidence*100:.0f}%)")
        print(f"   风险分数: {result.risk_score}")
    
    # 生成汇总报告
    print("\n" + "=" * 60)
    print("汇总报告")
    print("=" * 60)
    
    report = classifier.generate_report(results)
    summary = report['summary']
    
    print(f"总偏差数: {summary['total_deviations']}")
    print(f"关键偏差: {summary['critical_count']}")
    print(f"重大偏差: {summary['major_count']} ({summary['major_rate']}%)")
    print(f"微小偏差: {summary['minor_count']} ({summary['minor_rate']}%)")
    
    print("\n建议:")
    for rec in report['recommendations']:
        print(f"  • {rec}")


if __name__ == "__main__":
    main()
