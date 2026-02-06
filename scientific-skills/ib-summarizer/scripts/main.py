#!/usr/bin/env python3
"""
IB Summarizer - 研究者手册核心安全信息提取工具

功能：从Investigator's Brochure文档中提取核心安全信息(CSI)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class DrugInfo:
    """药物基本信息"""
    name: str = ""
    version: str = ""
    date: str = ""
    sponsor: str = ""


@dataclass
class AdverseReaction:
    """不良反应"""
    system_organ_class: str = ""  # 系统器官分类
    reaction: str = ""  # 反应名称
    frequency: str = ""  # 发生率
    severity: str = ""  # 严重程度


@dataclass
class SafetyUpdate:
    """安全更新记录"""
    version: str = ""
    date: str = ""
    content: str = ""


@dataclass
class CoreSafetyInfo:
    """核心安全信息"""
    adverse_reactions: List[AdverseReaction]
    contraindications: List[str]
    warnings: List[str]
    precautions: List[str]
    drug_interactions: List[str]
    special_populations: Dict[str, str]
    overdose: Dict[str, str]
    safety_updates: List[SafetyUpdate]


class TextExtractor:
    """文本提取器"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """从PDF提取文本"""
        try:
            import pdfplumber
        except ImportError:
            try:
                import PyPDF2
            except ImportError:
                raise ImportError("请安装 pdfplumber 或 PyPDF2: pip install pdfplumber")
            
            # 使用 PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        
        # 使用 pdfplumber (更精确)
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
        return text
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """从Word提取文本"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")
        
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """从TXT提取文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @classmethod
    def extract(cls, file_path: str) -> str:
        """根据文件类型自动提取文本"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return cls.extract_from_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            return cls.extract_from_docx(file_path)
        elif suffix in ['.txt', '.md']:
            return cls.extract_from_txt(file_path)
        else:
            # 尝试作为文本读取
            try:
                return cls.extract_from_txt(file_path)
            except:
                raise ValueError(f"不支持的文件格式: {suffix}")


class IBSummarizer:
    """IB文档安全信息提取器"""
    
    # 安全相关关键词模式
    KEYWORDS = {
        'adverse_reactions': [
            r'adverse\s+reaction',
            r'不良反应',
            r'adverse\s+event',
            r'不良事件',
            r'safety\s+data',
            r'safety\s+profile',
        ],
        'contraindications': [
            r'contraindication',
            r'禁忌症',
            r'禁忌',
        ],
        'warnings': [
            r'warning',
            r'警告',
        ],
        'precautions': [
            r'precaution',
            r'注意事项',
        ],
        'drug_interactions': [
            r'drug\s+interaction',
            r'药物相互作用',
            r'interaction',
        ],
        'special_populations': [
            r'special\s+population',
            r'特殊人群',
            r'pregnancy|pregnant',
            r'妊娠|孕妇',
            r'lactation|breastfeeding',
            r'哺乳',
            r'pediatric|children',
            r'儿童',
            r'elderly|geriatric',
            r'老年',
            r'hepatic',
            r'肝',
            r'renal',
            r'肾',
        ],
        'overdose': [
            r'overdose',
            r'过量',
            r'中毒',
        ],
    }
    
    def __init__(self, text: str):
        self.text = text
        self.lines = text.split('\n')
    
    def _find_section(self, keywords: List[str], context_lines: int = 50) -> str:
        """查找包含关键词的章节"""
        patterns = [re.compile(kw, re.IGNORECASE) for kw in keywords]
        
        for i, line in enumerate(self.lines):
            for pattern in patterns:
                if pattern.search(line):
                    # 提取上下文
                    start = max(0, i)
                    end = min(len(self.lines), i + context_lines)
                    return '\n'.join(self.lines[start:end])
        
        return ""
    
    def _extract_drug_info(self) -> DrugInfo:
        """提取药物基本信息"""
        info = DrugInfo()
        
        # 尝试匹配药物名称
        name_patterns = [
            r'(?:Drug\s+Name|Investigational\s+Product|药物名称)[\s:：]+([^\n]+)',
            r'(?:Title|标题)[\s:：]+([^\n]+)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                info.name = match.group(1).strip()
                break
        
        # 版本号
        version_patterns = [
            r'(?:Version|版本)[\s:：]*(\d+[.\d]*)',
            r'Edition[\s:：]*(\d+[.\d]*)',
        ]
        for pattern in version_patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                info.version = match.group(1).strip()
                break
        
        # 日期
        date_patterns = [
            r'(?:Date|日期)[\s:：]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, self.text)
            if match:
                info.date = match.group(1).strip()
                break
        
        return info
    
    def _extract_adverse_reactions(self) -> List[AdverseReaction]:
        """提取不良反应信息"""
        section = self._find_section(self.KEYWORDS['adverse_reactions'], 100)
        reactions = []
        
        if not section:
            return reactions
        
        # 简单的表格行匹配
        lines = section.split('\n')
        for line in lines[1:]:  # 跳过标题行
            # 尝试匹配：系统器官 | 反应 | 频率 | 严重程度
            parts = re.split(r'[\|，,；;\t]', line)
            if len(parts) >= 2:
                reactions.append(AdverseReaction(
                    system_organ_class=parts[0].strip() if len(parts) > 0 else "",
                    reaction=parts[1].strip() if len(parts) > 1 else "",
                    frequency=parts[2].strip() if len(parts) > 2 else "",
                    severity=parts[3].strip() if len(parts) > 3 else ""
                ))
        
        return reactions
    
    def _extract_list_items(self, keywords: List[str]) -> List[str]:
        """提取列表项"""
        section = self._find_section(keywords, 30)
        if not section:
            return []
        
        items = []
        for line in section.split('\n'):
            # 匹配列表项 (•, -, *, 数字. 等)
            match = re.match(r'^[\s]*(?:[•\-\*•]|\d+[.．）)])[\s]*(.+)', line)
            if match:
                items.append(match.group(1).strip())
        
        return items
    
    def _extract_special_populations(self) -> Dict[str, str]:
        """提取特殊人群信息"""
        section = self._find_section(self.KEYWORDS['special_populations'], 80)
        populations = {}
        
        if not section:
            return populations
        
        # 常见特殊人群
        pop_patterns = {
            'pregnancy': r'(?:Pregnancy|妊娠|孕妇)[\s\S]{0,500}?',
            'lactation': r'(?:Lactation|Breastfeeding|哺乳)[\s\S]{0,500}?',
            'pediatric': r'(?:Pediatric|Children|儿童)[\s\S]{0,500}?',
            'elderly': r'(?:Elderly|Geriatric|老年)[\s\S]{0,500}?',
            'hepatic': r'(?:Hepatic|肝)[\s\S]{0,500}?',
            'renal': r'(?:Renal|肾)[\s\S]{0,500}?',
        }
        
        for key, pattern in pop_patterns.items():
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                populations[key] = match.group(0).strip()
        
        return populations
    
    def _extract_overdose(self) -> Dict[str, str]:
        """提取用药过量信息"""
        section = self._find_section(self.KEYWORDS['overdose'], 50)
        if not section:
            return {}
        
        overdose = {}
        
        # 症状
        symptoms_match = re.search(r'(?:Symptoms|症状)[：:]([^\n]+)', section, re.IGNORECASE)
        if symptoms_match:
            overdose['symptoms'] = symptoms_match.group(1).strip()
        
        # 处理
        management_match = re.search(r'(?:Management|Treatment|处理|治疗)[：:]([^\n]+)', section, re.IGNORECASE)
        if management_match:
            overdose['management'] = management_match.group(1).strip()
        
        return overdose
    
    def _extract_safety_updates(self) -> List[SafetyUpdate]:
        """提取安全更新历史"""
        # 通常在文档末尾的版本历史部分
        updates = []
        
        # 查找版本历史表格
        version_pattern = r'(\d+[.\d]*)\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+([^\n]+)'
        matches = re.findall(version_pattern, self.text)
        
        for match in matches[:10]:  # 最多10条
            updates.append(SafetyUpdate(
                version=match[0],
                date=match[1],
                content=match[2].strip()
            ))
        
        return updates
    
    def summarize(self) -> Dict[str, Any]:
        """执行完整的安全信息提取"""
        drug_info = self._extract_drug_info()
        
        core_safety = CoreSafetyInfo(
            adverse_reactions=self._extract_adverse_reactions(),
            contraindications=self._extract_list_items(self.KEYWORDS['contraindications']),
            warnings=self._extract_list_items(self.KEYWORDS['warnings']),
            precautions=self._extract_list_items(self.KEYWORDS['precautions']),
            drug_interactions=self._extract_list_items(self.KEYWORDS['drug_interactions']),
            special_populations=self._extract_special_populations(),
            overdose=self._extract_overdose(),
            safety_updates=self._extract_safety_updates()
        )
        
        return {
            'drug_info': asdict(drug_info),
            'core_safety_info': {
                'adverse_reactions': [asdict(r) for r in core_safety.adverse_reactions],
                'contraindications': core_safety.contraindications,
                'warnings': core_safety.warnings,
                'precautions': core_safety.precautions,
                'drug_interactions': core_safety.drug_interactions,
                'special_populations': core_safety.special_populations,
                'overdose': core_safety.overdose,
                'safety_updates': [asdict(u) for u in core_safety.safety_updates]
            }
        }


class OutputFormatter:
    """输出格式化器"""
    
    @staticmethod
    def to_json(data: Dict[str, Any]) -> str:
        """格式化为JSON"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def to_markdown(data: Dict[str, Any], language: str = 'zh') -> str:
        """格式化为Markdown"""
        drug = data['drug_info']
        safety = data['core_safety_info']
        
        md = f"""# IB安全信息摘要

## 药物基本信息
- **药物名称**: {drug['name'] or 'N/A'}
- **版本号**: {drug['version'] or 'N/A'}
- **日期**: {drug['date'] or 'N/A'}
- **申办方**: {drug['sponsor'] or 'N/A'}

## 核心安全信息

### 已知不良反应
"""
        
        if safety['adverse_reactions']:
            md += "| 系统器官分类 | 不良反应 | 发生率 | 严重程度 |\n"
            md += "|-------------|---------|--------|---------|\n"
            for ar in safety['adverse_reactions']:
                md += f"| {ar['system_organ_class'] or '-'} | {ar['reaction'] or '-'} | {ar['frequency'] or '-'} | {ar['severity'] or '-'} |\n"
        else:
            md += "_未检测到不良反应数据_\n"
        
        md += "\n### 禁忌症\n"
        if safety['contraindications']:
            for item in safety['contraindications']:
                md += f"- {item}\n"
        else:
            md += "_未检测到禁忌症数据_\n"
        
        md += "\n### 警告与注意事项\n"
        if safety['warnings']:
            md += "#### 警告\n"
            for item in safety['warnings']:
                md += f"- {item}\n"
        
        if safety['precautions']:
            md += "#### 注意事项\n"
            for item in safety['precautions']:
                md += f"- {item}\n"
        
        if not safety['warnings'] and not safety['precautions']:
            md += "_未检测到警告/注意事项数据_\n"
        
        md += "\n### 药物相互作用\n"
        if safety['drug_interactions']:
            for item in safety['drug_interactions']:
                md += f"- {item}\n"
        else:
            md += "_未检测到药物相互作用数据_\n"
        
        md += "\n### 特殊人群用药注意事项\n"
        if safety['special_populations']:
            for pop, note in safety['special_populations'].items():
                md += f"**{pop.capitalize()}**: {note[:200]}...\n\n"
        else:
            md += "_未检测到特殊人群数据_\n"
        
        md += "\n### 用药过量\n"
        if safety['overdose']:
            if 'symptoms' in safety['overdose']:
                md += f"- **症状**: {safety['overdose']['symptoms']}\n"
            if 'management' in safety['overdose']:
                md += f"- **处理**: {safety['overdose']['management']}\n"
        else:
            md += "_未检测到过量的相关数据_\n"
        
        md += "\n### 安全更新历史\n"
        if safety['safety_updates']:
            md += "| 版本 | 日期 | 更新内容 |\n"
            md += "|-----|------|---------|\n"
            for update in safety['safety_updates']:
                md += f"| {update['version']} | {update['date']} | {update['content'][:100]}... |\n"
        else:
            md += "_未检测到安全更新历史_\n"
        
        md += "\n---\n*本摘要由IB Summarizer自动生成，仅供参考*\n"
        
        return md
    
    @staticmethod
    def to_text(data: Dict[str, Any]) -> str:
        """格式化为纯文本"""
        md = OutputFormatter.to_markdown(data)
        # 移除Markdown标记
        text = re.sub(r'#+\s*', '', md)
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'\|', ' | ', text)
        return text


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='IB Summarizer - 研究者手册核心安全信息提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py /path/to/IB.pdf
  python main.py /path/to/IB.docx -o summary.json -f json
  python main.py /path/to/IB.pdf -l en -o summary.md
        """
    )
    
    parser.add_argument('input_file', help='输入的IB文档路径(PDF/Word/TXT)')
    parser.add_argument('-o', '--output', help='输出文件路径(默认输出到stdout)')
    parser.add_argument('-f', '--format', choices=['json', 'markdown', 'text'], 
                        default='markdown', help='输出格式(默认: markdown)')
    parser.add_argument('-l', '--language', choices=['zh', 'en'], 
                        default='zh', help='输出语言(默认: zh)')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not Path(args.input_file).exists():
        print(f"错误: 文件不存在: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 提取文本
        print(f"正在提取: {args.input_file}...", file=sys.stderr)
        text = TextExtractor.extract(args.input_file)
        
        # 提取安全信息
        print("正在分析安全信息...", file=sys.stderr)
        summarizer = IBSummarizer(text)
        data = summarizer.summarize()
        
        # 格式化输出
        formatter = OutputFormatter()
        if args.format == 'json':
            output = formatter.to_json(data)
        elif args.format == 'text':
            output = formatter.to_text(data)
        else:
            output = formatter.to_markdown(data, args.language)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"摘要已保存至: {args.output}", file=sys.stderr)
        else:
            print(output)
            
    except ImportError as e:
        print(f"依赖错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
