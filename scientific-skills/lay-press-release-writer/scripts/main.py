#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lay Press Release Writer
将学术论文转化为大学新闻中心风格的新闻通稿

Usage:
    python main.py --paper-text "论文内容..." [options]
"""

import argparse
import json
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional


def extract_key_findings(text: str) -> List[str]:
    """从论文中提取关键发现"""
    findings = []
    
    # 寻找结论部分
    conclusion_patterns = [
        r'(?:结论|conclusion|findings|results).*?(?:\n|$)(.*?)(?:\n\n|\Z)',
        r'(?:本文|我们|本研究).*?(?:发现|证明|表明|揭示)(.*?)(?:。|；)',
    ]
    
    for pattern in conclusion_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches[:3]:  # 限制最多3个发现
            finding = match.strip()
            if len(finding) > 20 and len(finding) < 500:
                findings.append(finding)
    
    return findings[:3]  # 返回前3个关键发现


def generate_headline(title: str, key_finding: str) -> str:
    """生成引人注目的标题"""
    # 简化标题，使其更具新闻性
    headline = title
    
    # 移除过于学术化的词汇
    academic_terms = ['研究', '分析', '探讨', '基于', '方法', '模型']
    for term in academic_terms:
        headline = headline.replace(term, '')
    
    # 添加新闻性词汇
    news_boosters = ['突破', '新发现', '首次', '创新', '重要进展']
    
    # 如果标题中没有这些词汇，适当添加
    if not any(word in headline for word in news_boosters):
        if '首次' in key_finding or '首次' in title:
            headline = f"重大突破：{headline}"
        elif len(headline) < 15:
            headline = f"研究揭示：{headline}"
    
    return headline.strip()


def generate_subheadline(key_findings: List[str], institution: str) -> str:
    """生成副标题"""
    if key_findings:
        finding = key_findings[0]
        # 简化到一句话
        finding = finding[:80] + '...' if len(finding) > 80 else finding
        return f"{institution}研究团队{finding}"
    return f"{institution}最新研究成果发布"


def generate_lead(title: str, authors: List[str], institution: str, 
                  venue: str, key_findings: List[str]) -> str:
    """生成导语（第一段）- 倒金字塔结构最重要部分"""
    author_str = '、'.join(authors[:3]) if authors else '研究团队'
    if len(authors) > 3:
        author_str += '等'
    
    lead = f"【地点】{institution}{author_str}"
    
    if venue:
        lead += f"在《{venue}》发表的最新研究"
    else:
        lead += "的最新研究"
    
    if key_findings:
        finding = key_findings[0]
        # 简化发现描述
        finding = re.sub(r'[（(].*?[)）]', '', finding)  # 移除括号内容
        finding = finding[:100] + '...' if len(finding) > 100 else finding
        lead += f"{finding}。"
    else:
        lead += "取得重要进展。"
    
    return lead


def generate_body(text: str, key_findings: List[str], target_audience: str) -> str:
    """生成正文内容"""
    paragraphs = []
    
    # 第一段：研究背景
    background = extract_background(text)
    if background:
        paragraphs.append(f"研究背景：{background}")
    
    # 第二段：核心发现
    if key_findings:
        findings_text = "该研究的主要发现包括："
        for i, finding in enumerate(key_findings, 1):
            simplified = simplify_language(finding)
            findings_text += f"{i}) {simplified}；"
        paragraphs.append(findings_text)
    
    # 第三段：意义和应用
    significance = extract_significance(text)
    if significance:
        paragraphs.append(f"研究意义：{significance}")
    
    return '\n\n'.join(paragraphs)


def generate_quotes(authors: List[str], text: str) -> List[str]:
    """生成研究人员引用语"""
    quotes = []
    
    if authors:
        first_author = authors[0]
        quotes.append(f"\"这项研究为我们理解该领域提供了新的视角，\"{first_author}表示，\"我们期待这一发现能为相关应用带来实际价值。\"")
    
    if len(authors) > 1:
        quotes.append(f"\"这是团队多年合作的成果，\"合作者补充道，\"未来我们将继续深入探索这一方向。\"")
    
    return quotes


def extract_background(text: str) -> str:
    """提取研究背景"""
    patterns = [
        r'(?:背景|background|introduction|引言).*?(?:\n|$)(.*?)(?:\n\n|\Z)',
        r'(?:随着|近年来|目前).*?(?:发展|进步|挑战|问题).*?(?:。；)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            bg = match.group(1).strip()
            # 简化背景描述
            bg = simplify_language(bg)
            return bg[:200] + '...' if len(bg) > 200 else bg
    
    return "该研究针对当前领域的重要问题展开深入探索。"


def extract_significance(text: str) -> str:
    """提取研究意义"""
    patterns = [
        r'(?:意义|significance|implications|impact).*?(?:\n|$)(.*?)(?:\n\n|\Z)',
        r'(?:本研究|该研究).*?(?:有助于|可以|能够|为).*?(?:。；)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sig = match.group(1).strip()
            sig = simplify_language(sig)
            return sig[:200] + '...' if len(sig) > 200 else sig
    
    return "该研究为相关领域的发展提供了重要的理论基础和实践指导。"


def simplify_language(text: str) -> str:
    """简化学术语言为通俗语言"""
    # 学术词汇到通俗词汇的映射
    replacements = {
        '本文': '该研究',
        '基于此': '在此基础上',
        '综上所述': '总的来说',
        '研究表明': '研究发现',
        '证明了': '发现',
        '揭示了': '展示了',
        '构建了': '开发了',
        '提出了': '提出了',
        '实现了': '达成了',
        '优化了': '改进了',
        '显著': '明显',
        ' methodology': '方法',
        ' algorithm': '算法',
        ' framework': '框架',
    }
    
    for academic, lay in replacements.items():
        text = text.replace(academic, lay)
    
    return text


def generate_boilerplate(institution: str) -> str:
    """生成机构简介"""
    templates = {
        '清华大学': '清华大学是中国著名高等学府，是中国高层次人才培养和科学技术研究的重要基地。',
        '北京大学': '北京大学是中国第一所国立综合性大学，是新文化运动的中心和五四运动的策源地。',
        '复旦大学': '复旦大学是中国人自主创办的第一所高等院校，是一所世界知名、国内顶尖的综合性研究型大学。',
        '上海交通大学': '上海交通大学是教育部直属并与上海市共建的全国重点大学，是一所\"综合性、研究型、国际化\"的国内一流、国际知名大学。',
    }
    
    return templates.get(institution, 
        f'{institution}是一所致力于教学与科研的高等学府，在多个学科领域具有重要影响力。')


def generate_media_contact(institution: str) -> Dict:
    """生成媒体联系信息"""
    return {
        "department": f"{institution}新闻中心",
        "email": f"media@{institution.lower().replace('大学', '').replace('学院', '')}.edu.cn",
        "phone": "请联系学校总机转新闻中心"
    }


def write_press_release(args) -> Dict:
    """主函数：生成新闻通稿"""
    
    # 解析参数
    paper_text = args.paper_text or ""
    paper_title = args.paper_title or "重要研究成果"
    authors = args.authors.split(',') if args.authors else []
    institution = args.institution or "本校"
    venue = args.publication_venue or ""
    target_audience = args.target_audience or "general"
    
    # 提取关键信息
    key_findings = extract_key_findings(paper_text)
    
    # 生成新闻稿各部分
    headline = generate_headline(paper_title, key_findings[0] if key_findings else "")
    subheadline = generate_subheadline(key_findings, institution)
    dateline = f"{institution}，{datetime.now().strftime('%Y年%m月%d日')}"
    lead = generate_lead(paper_title, authors, institution, venue, key_findings)
    body = generate_body(paper_text, key_findings, target_audience)
    quotes = generate_quotes(authors, paper_text)
    boilerplate = generate_boilerplate(institution)
    media_contact = generate_media_contact(institution)
    
    # 组装输出
    press_release = {
        "headline": headline,
        "subheadline": subheadline,
        "dateline": dateline,
        "lead": lead,
        "body": body,
        "quotes": quotes,
        "boilerplate": boilerplate,
        "media_contact": media_contact
    }
    
    return press_release


def main():
    parser = argparse.ArgumentParser(
        description='将学术论文转化为大学新闻中心风格的新闻通稿'
    )
    
    parser.add_argument('--paper-text', type=str, required=True,
                        help='论文全文或摘要文本')
    parser.add_argument('--paper-title', type=str, default='',
                        help='论文标题')
    parser.add_argument('--authors', type=str, default='',
                        help='作者列表，用逗号分隔')
    parser.add_argument('--institution', type=str, default='',
                        help='所属机构/大学名称')
    parser.add_argument('--publication-venue', type=str, default='',
                        help='发表期刊/会议名称')
    parser.add_argument('--target-audience', type=str, default='general',
                        choices=['general', 'alumni', 'media'],
                        help='目标受众')
    parser.add_argument('--tone', type=str, default='formal',
                        choices=['formal', 'friendly', 'inspiring'],
                        help='语气风格')
    parser.add_argument('--output', type=str, default='',
                        help='输出文件路径（JSON格式）')
    
    args = parser.parse_args()
    
    # 生成新闻稿
    result = write_press_release(args)
    
    # 格式化输出
    formatted_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        print(f"新闻稿已保存至: {args.output}")
    else:
        print(formatted_output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
