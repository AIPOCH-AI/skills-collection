#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patent Claim Mapper - 专利权利要求侵权风险分析工具

功能：
1. 解析专利权利要求文本
2. 提取技术特征
3. 与产品特征进行比对分析
4. 生成侵权风险评估报告

Author: OpenClaw Skills Team
Version: 1.0.0
"""

import re
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime


@dataclass
class ClaimElement:
    """权利要求中的技术要素"""
    text: str
    element_type: str  # 'apparatus', 'method', 'feature', 'limitation'
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PatentClaim:
    """专利权利要求"""
    number: int
    is_independent: bool
    parent_claim: Optional[int]  # 从属权利要求引用
    text: str
    elements: List[ClaimElement] = field(default_factory=list)
    preamble: str = ""  # 前序部分
    body: str = ""      # 特征部分
    
    def to_dict(self) -> Dict:
        return {
            'number': self.number,
            'is_independent': self.is_independent,
            'parent_claim': self.parent_claim,
            'text': self.text,
            'preamble': self.preamble,
            'body': self.body,
            'elements': [e.to_dict() for e in self.elements]
        }


@dataclass
class RiskAssessment:
    """风险评估结果"""
    claim_number: int
    risk_level: str  # 'high', 'medium', 'low'
    match_score: float  # 0-1
    matched_features: List[str] = field(default_factory=list)
    unmatched_features: List[str] = field(default_factory=list)
    analysis_notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ClaimParser:
    """权利要求解析器"""
    
    # 权利要求编号模式
    CLAIM_NUMBER_PATTERN = re.compile(r'^(\d+)\.\s*')
    
    # 从属权利要求引用模式
    DEPENDENT_PATTERN = re.compile(
        r'根据|如|依据.*?权利要求\s*(\d+)|引用.*?权利要求\s*(\d+)',
        re.IGNORECASE | re.UNICODE
    )
    
    # 前序部分和特征部分分隔
    PREAMBLE_SEPARATORS = ['其特征在于', '其特征在于，', '特征是', '特征是，', 
                          'characterized in that', 'wherein', 'comprising:']
    
    def parse(self, text: str) -> List[PatentClaim]:
        """
        解析权利要求文本
        
        Args:
            text: 权利要求书全文
            
        Returns:
            PatentClaim对象列表
        """
        claims = []
        claim_texts = self._split_claims(text)
        
        for claim_text in claim_texts:
            claim = self._parse_single_claim(claim_text)
            if claim:
                claims.append(claim)
        
        # 解析各权利要求的技术要素
        for claim in claims:
            claim.elements = self._extract_elements(claim)
        
        return claims
    
    def _split_claims(self, text: str) -> List[str]:
        """将权利要求书文本分割为单个权利要求"""
        # 按数字编号分割（如 "1." "2."）
        pattern = re.compile(r'\n\s*(\d+)\.\s+', re.MULTILINE)
        parts = pattern.split(text)
        
        claims = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                claim_num = parts[i]
                claim_content = parts[i + 1].strip()
                claims.append(f"{claim_num}. {claim_content}")
        
        return claims
    
    def _parse_single_claim(self, text: str) -> Optional[PatentClaim]:
        """解析单个权利要求"""
        # 提取权利要求编号
        match = self.CLAIM_NUMBER_PATTERN.match(text)
        if not match:
            return None
        
        number = int(match.group(1))
        content = text[match.end():].strip()
        
        # 判断是否为独立权利要求
        parent_claim = self._extract_parent_claim(content)
        is_independent = parent_claim is None
        
        # 分割前序部分和特征部分
        preamble, body = self._split_preamble_body(content)
        
        return PatentClaim(
            number=number,
            is_independent=is_independent,
            parent_claim=parent_claim,
            text=content,
            preamble=preamble,
            body=body
        )
    
    def _extract_parent_claim(self, text: str) -> Optional[int]:
        """提取从属权利要求引用的父权利要求编号"""
        match = self.DEPENDENT_PATTERN.search(text)
        if match:
            # 返回第一个非空的匹配组
            for group in match.groups():
                if group:
                    return int(group)
        return None
    
    def _split_preamble_body(self, text: str) -> Tuple[str, str]:
        """分割前序部分和特征部分"""
        for separator in self.PREAMBLE_SEPARATORS:
            if separator in text:
                parts = text.split(separator, 1)
                return parts[0].strip(), parts[1].strip()
        
        # 默认返回全文作为前序部分
        return text, ""
    
    def _extract_elements(self, claim: PatentClaim) -> List[ClaimElement]:
        """提取权利要求中的技术要素"""
        elements = []
        
        # 分割特征（通常以分号、逗号+以及、逗号+并且分隔）
        text_to_analyze = claim.body if claim.body else claim.text
        
        # 特征分隔符
        separators = r'；|；|；|\.|,\s*以及|,\s*并且|,\s*and|,\s*wherein|;'
        parts = re.split(separators, text_to_analyze)
        
        for part in parts:
            part = part.strip()
            if len(part) > 5:  # 过滤过短的片段
                keywords = self._extract_keywords(part)
                element = ClaimElement(
                    text=part,
                    element_type=self._classify_element(part),
                    keywords=keywords
                )
                elements.append(element)
        
        return elements
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取：名词性词组
        # 这里使用启发式规则，实际可接入NLP模型
        keywords = []
        
        # 提取引号内的术语
        quoted = re.findall(r'[""'']([^""'']+)[""'']', text)
        keywords.extend(quoted)
        
        # 提取大写术语（英文）
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        keywords.extend(capitalized)
        
        # 提取技术术语（包含特定技术词的短语）
        tech_patterns = [
            r'\w+器', r'\w+装置', r'\w+系统', r'\w+方法',
            r'\w+模块', r'\w+单元', r'\w+组件',
            r'\w+device', r'\w+system', r'\w+method', r'\w+apparatus'
        ]
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches)
        
        return list(set(keywords))
    
    def _classify_element(self, text: str) -> str:
        """分类技术要素类型"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['装置', '设备', '系统', 'apparatus', 'device', 'system']):
            return 'apparatus'
        elif any(kw in text_lower for kw in ['方法', '步骤', '流程', 'method', 'process', 'step']):
            return 'method'
        elif any(kw in text_lower for kw in ['包括', '包含', 'comprising', 'comprises', 'having']):
            return 'feature'
        else:
            return 'limitation'


class InfringementAnalyzer:
    """侵权分析器"""
    
    def __init__(self, risk_threshold: float = 0.7):
        self.risk_threshold = risk_threshold
    
    def analyze(self, claims: List[PatentClaim], 
                product_features: List[str]) -> List[RiskAssessment]:
        """
        分析侵权风险
        
        Args:
            claims: 专利权利要求列表
            product_features: 产品特征描述列表
            
        Returns:
            风险评估结果列表
        """
        assessments = []
        
        for claim in claims:
            assessment = self._analyze_single_claim(claim, product_features)
            assessments.append(assessment)
        
        return assessments
    
    def _analyze_single_claim(self, claim: PatentClaim, 
                              product_features: List[str]) -> RiskAssessment:
        """分析单个权利要求的侵权风险"""
        matched = []
        unmatched = []
        notes = []
        
        # 提取权利要求的所有技术特征文本
        claim_features = [e.text for e in claim.elements]
        
        for claim_feature in claim_features:
            best_match = self._find_best_match(claim_feature, product_features)
            
            if best_match['score'] >= 0.6:
                matched.append({
                    'claim_feature': claim_feature,
                    'product_feature': best_match['feature'],
                    'similarity': best_match['score']
                })
            else:
                unmatched.append(claim_feature)
        
        # 计算整体匹配度
        if claim_features:
            match_score = len(matched) / len(claim_features)
        else:
            match_score = 0.0
        
        # 确定风险等级
        risk_level = self._determine_risk_level(match_score, matched, unmatched)
        
        # 生成分析说明
        notes = self._generate_analysis_notes(claim, matched, unmatched, match_score)
        
        return RiskAssessment(
            claim_number=claim.number,
            risk_level=risk_level,
            match_score=round(match_score, 2),
            matched_features=[m['claim_feature'] for m in matched],
            unmatched_features=unmatched,
            analysis_notes=notes
        )
    
    def _find_best_match(self, claim_feature: str, 
                         product_features: List[str]) -> Dict:
        """找到与权利要求特征最匹配的产品特征"""
        best_score = 0.0
        best_feature = ""
        
        claim_keywords = set(self._extract_words(claim_feature))
        
        for product_feature in product_features:
            score = self._calculate_similarity(claim_feature, product_feature, claim_keywords)
            if score > best_score:
                best_score = score
                best_feature = product_feature
        
        return {'feature': best_feature, 'score': best_score}
    
    def _calculate_similarity(self, claim_feature: str, product_feature: str,
                              claim_keywords: set) -> float:
        """计算两个特征的相似度（0-1）"""
        product_keywords = set(self._extract_words(product_feature))
        
        if not claim_keywords or not product_keywords:
            return 0.0
        
        # Jaccard相似度
        intersection = len(claim_keywords & product_keywords)
        union = len(claim_keywords | product_keywords)
        
        jaccard = intersection / union if union > 0 else 0.0
        
        # 包含关系加分
        containment_bonus = 0.0
        if claim_feature.lower() in product_feature.lower():
            containment_bonus = 0.3
        elif product_feature.lower() in claim_feature.lower():
            containment_bonus = 0.2
        
        return min(1.0, jaccard + containment_bonus)
    
    def _extract_words(self, text: str) -> List[str]:
        """提取文本中的关键词"""
        # 去除标点，分词
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.lower().split()
        
        # 过滤停用词
        stopwords = {'的', '是', '在', '和', '了', '与', '或', 'the', 'a', 'an', 
                     'is', 'are', 'was', 'were', 'of', 'to', 'in', 'and', 'or'}
        
        return [w for w in words if w not in stopwords and len(w) > 1]
    
    def _determine_risk_level(self, match_score: float, matched: List, 
                              unmatched: List) -> str:
        """确定风险等级"""
        if match_score >= self.risk_threshold:
            return 'high'
        elif match_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_analysis_notes(self, claim: PatentClaim, matched: List, 
                                  unmatched: List, score: float) -> List[str]:
        """生成分析说明"""
        notes = []
        
        if score >= self.risk_threshold:
            notes.append(f"权利要求{claim.number}与产品特征高度匹配，存在实质性侵权风险")
        elif score >= 0.4:
            notes.append(f"权利要求{claim.number}与产品特征部分匹配，建议进一步评估")
        else:
            notes.append(f"权利要求{claim.number}与产品特征匹配度较低")
        
        if claim.is_independent:
            notes.append("该权利要求为独立权利要求，保护范围最广，需重点关注")
        else:
            notes.append(f"该权利要求为从属权利要求，引用权利要求{claim.parent_claim}")
        
        if matched:
            notes.append(f"已匹配{len(matched)}项技术特征")
        if unmatched:
            notes.append(f"未匹配{len(unmatched)}项技术特征，可能为规避设计点")
        
        return notes


class ReportGenerator:
    """报告生成器"""
    
    RISK_ICONS = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }
    
    RISK_LABELS = {
        'high': '高风险',
        'medium': '中风险',
        'low': '低风险'
    }
    
    def generate(self, assessments: List[RiskAssessment], 
                 patent_info: Dict, product_name: str) -> str:
        """生成风险评估报告"""
        report = []
        
        # 报告标题
        report.append("# 专利侵权风险分析报告")
        report.append("")
        
        # 基本信息
        report.append("## 基本信息")
        report.append(f"- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"- **目标产品**: {product_name}")
        if patent_info.get('patent_number'):
            report.append(f"- **专利号**: {patent_info['patent_number']}")
        if patent_info.get('patent_title'):
            report.append(f"- **专利名称**: {patent_info['patent_title']}")
        report.append("")
        
        # 风险概览
        report.append("## 风险概览")
        report.append("")
        report.append("| 权利要求 | 类型 | 风险等级 | 匹配度 |")
        report.append("|---------|------|---------|-------|")
        
        for assessment in assessments:
            claim_type = "独立" if assessment.claim_number == 1 or not assessment.claim_number else "从属"
            icon = self.RISK_ICONS.get(assessment.risk_level, '⚪')
            label = self.RISK_LABELS.get(assessment.risk_level, '未知')
            report.append(
                f"| 权利要求{assessment.claim_number} | {claim_type} | "
                f"{icon} {label} | {assessment.match_score * 100:.0f}% |"
            )
        report.append("")
        
        # 详细分析
        report.append("## 详细分析")
        report.append("")
        
        for assessment in assessments:
            report.extend(self._generate_claim_analysis(assessment))
            report.append("")
        
        # 结论与建议
        report.append("## 结论与建议")
        report.append("")
        
        high_risks = [a for a in assessments if a.risk_level == 'high']
        medium_risks = [a for a in assessments if a.risk_level == 'medium']
        
        if high_risks:
            report.append("### ⚠️ 高风险警告")
            report.append(f"发现{len(high_risks)}项权利要求存在高风险：")
            for risk in high_risks:
                report.append(f"- 权利要求{risk.claim_number}（匹配度{risk.match_score * 100:.0f}%）")
            report.append("")
            report.append("**建议措施**:")
            report.append("1. 立即进行详细的FTO分析")
            report.append("2. 考虑设计规避方案")
            report.append("3. 咨询专业专利律师")
            report.append("")
        
        if medium_risks:
            report.append("### 🔍 中等风险提示")
            report.append(f"发现{len(medium_risks)}项权利要求需要关注")
            report.append("")
        
        report.append("### 规避设计建议")
        report.append("针对未匹配的技术特征，可考虑以下规避方向：")
        
        for assessment in assessments:
            if assessment.unmatched_features:
                report.append(f"\n**权利要求{assessment.claim_number}**:")
                for feature in assessment.unmatched_features[:3]:  # 最多显示3个
                    report.append(f"- 考虑修改或移除: {feature[:50]}...")
        
        report.append("")
        report.append("---")
        report.append("*免责声明：本报告基于文本相似度算法自动生成，仅供技术参考，不构成法律意见。最终侵权判定请咨询专业专利律师。*")
        
        return "\n".join(report)
    
    def _generate_claim_analysis(self, assessment: RiskAssessment) -> List[str]:
        """生成单个权利要求的分析"""
        lines = []
        
        icon = self.RISK_ICONS.get(assessment.risk_level, '⚪')
        lines.append(f"### 权利要求{assessment.claim_number} {icon}")
        lines.append("")
        
        lines.append(f"**风险等级**: {self.RISK_LABELS.get(assessment.risk_level, '未知')}")
        lines.append(f"**匹配度**: {assessment.match_score * 100:.0f}%")
        lines.append("")
        
        if assessment.analysis_notes:
            lines.append("**分析说明**:")
            for note in assessment.analysis_notes:
                lines.append(f"- {note}")
            lines.append("")
        
        if assessment.matched_features:
            lines.append("**已匹配技术特征**:")
            for feature in assessment.matched_features[:5]:  # 最多显示5个
                lines.append(f"- ✅ {feature[:80]}...")
            lines.append("")
        
        if assessment.unmatched_features:
            lines.append("**未匹配技术特征（潜在规避点）**:")
            for feature in assessment.unmatched_features[:5]:
                lines.append(f"- ⚠️ {feature[:80]}...")
            lines.append("")
        
        return lines
    
    def generate_json(self, assessments: List[RiskAssessment], 
                      patent_info: Dict, product_name: str) -> str:
        """生成JSON格式报告"""
        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'product_name': product_name,
                'patent_info': patent_info
            },
            'summary': {
                'total_claims': len(assessments),
                'high_risk': len([a for a in assessments if a.risk_level == 'high']),
                'medium_risk': len([a for a in assessments if a.risk_level == 'medium']),
                'low_risk': len([a for a in assessments if a.risk_level == 'low'])
            },
            'assessments': [a.to_dict() for a in assessments]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


class PatentClaimMapper:
    """专利权利要求映射分析主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.parser = ClaimParser()
        self.analyzer = InfringementAnalyzer(
            risk_threshold=self.config.get('risk_threshold', 0.7)
        )
        self.report_generator = ReportGenerator()
    
    def load_claims(self, file_path: str) -> List[PatentClaim]:
        """
        从文件加载权利要求
        
        Args:
            file_path: 权利要求书文件路径
            
        Returns:
            PatentClaim对象列表
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"权利要求文件不存在: {file_path}")
        
        text = path.read_text(encoding='utf-8')
        return self.parser.parse(text)
    
    def load_claims_from_text(self, text: str) -> List[PatentClaim]:
        """从文本直接加载权利要求"""
        return self.parser.parse(text)
    
    def analyze_infringement(self, claims: List[PatentClaim],
                            product_features: List[str]) -> List[RiskAssessment]:
        """
        分析侵权风险
        
        Args:
            claims: 专利权利要求列表
            product_features: 产品特征列表
            
        Returns:
            风险评估结果列表
        """
        return self.analyzer.analyze(claims, product_features)
    
    def generate_report(self, assessments: List[RiskAssessment],
                       patent_info: Dict = None,
                       product_name: str = "未命名产品") -> str:
        """
        生成分析报告
        
        Args:
            assessments: 风险评估结果
            patent_info: 专利信息字典
            product_name: 产品名称
            
        Returns:
            报告文本（Markdown格式）
        """
        patent_info = patent_info or {}
        return self.report_generator.generate(assessments, patent_info, product_name)
    
    def generate_json_report(self, assessments: List[RiskAssessment],
                            patent_info: Dict = None,
                            product_name: str = "未命名产品") -> str:
        """生成JSON格式报告"""
        patent_info = patent_info or {}
        return self.report_generator.generate_json(assessments, patent_info, product_name)
    
    def run_full_analysis(self, patent_file: str, product_file: str,
                         output_file: str = None) -> str:
        """
        运行完整的分析流程
        
        Args:
            patent_file: 专利权利要求书文件路径
            product_file: 产品特征描述文件路径
            output_file: 输出报告文件路径（可选）
            
        Returns:
            分析报告文本
        """
        # 加载权利要求
        claims = self.load_claims(patent_file)
        print(f"✅ 已解析 {len(claims)} 项权利要求")
        
        # 加载产品特征
        product_text = Path(product_file).read_text(encoding='utf-8')
        product_features = self._extract_product_features(product_text)
        print(f"✅ 已提取 {len(product_features)} 项产品特征")
        
        # 分析侵权风险
        assessments = self.analyze_infringement(claims, product_features)
        
        # 生成报告
        patent_info = {'patent_number': Path(patent_file).stem}
        product_name = Path(product_file).stem
        report = self.generate_report(assessments, patent_info, product_name)
        
        # 保存报告
        if output_file:
            Path(output_file).write_text(report, encoding='utf-8')
            print(f"✅ 报告已保存至: {output_file}")
        
        return report
    
    def _extract_product_features(self, text: str) -> List[str]:
        """从文本提取产品特征"""
        features = []
        
        # 按行分割
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 去除列表标记
            for prefix in ['-', '*', '•', '1.', '2.', '3.', '4.', '5.']:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
            
            if len(line) > 5:
                features.append(line)
        
        # 如果行数太少，尝试按句子分割
        if len(features) < 3:
            sentences = re.split(r'[。\.\n]+', text)
            features = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return features


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='Patent Claim Mapper - 专利权利要求侵权风险分析工具'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析侵权风险')
    analyze_parser.add_argument('--patent', '-p', required=True,
                               help='专利权利要求书文件路径')
    analyze_parser.add_argument('--product', '-pr', required=True,
                               help='产品特征描述文件路径')
    analyze_parser.add_argument('--output', '-o',
                               help='输出报告文件路径')
    analyze_parser.add_argument('--format', '-f', choices=['markdown', 'json'],
                               default='markdown', help='输出格式')
    
    # parse 命令
    parse_parser = subparsers.add_parser('parse', help='仅解析权利要求结构')
    parse_parser.add_argument('--patent', '-p', required=True,
                             help='专利权利要求书文件路径')
    parse_parser.add_argument('--output', '-o',
                             help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        mapper = PatentClaimMapper()
        
        try:
            report = mapper.run_full_analysis(
                args.patent,
                args.product,
                args.output
            )
            if not args.output:
                print("\n" + "=" * 60)
                print(report)
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return 1
    
    elif args.command == 'parse':
        mapper = PatentClaimMapper()
        
        try:
            claims = mapper.load_claims(args.patent)
            print(f"✅ 成功解析 {len(claims)} 项权利要求")
            
            # 打印权利要求结构
            for claim in claims:
                print(f"\n{'=' * 40}")
                print(f"权利要求 {claim.number}")
                print(f"类型: {'独立' if claim.is_independent else '从属'}")
                if claim.parent_claim:
                    print(f"引用: 权利要求 {claim.parent_claim}")
                print(f"前序部分: {claim.preamble[:100]}...")
                print(f"特征部分: {claim.body[:100]}...")
                print(f"技术要素数量: {len(claim.elements)}")
            
            if args.output:
                data = {'claims': [c.to_dict() for c in claims]}
                Path(args.output).write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )
                print(f"\n✅ 已保存至: {args.output}")
        
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return 1
    
    else:
        parser.print_help()
    
    return 0


if __name__ == '__main__':
    exit(main())
