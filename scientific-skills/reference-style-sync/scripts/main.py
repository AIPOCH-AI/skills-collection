#!/usr/bin/env python3
"""
Reference Style Sync - 一键统一 Zotero/EndNote 文献格式
自动修复抓取元数据时的错误
"""

import re
import json
import csv
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class Reference:
    """文献条目数据结构"""
    id: str = ""
    type: str = "journal"  # journal, book, conference, thesis, report, webpage
    authors: List[Dict[str, str]] = field(default_factory=list)
    title: str = ""
    journal: str = ""
    year: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    url: str = ""
    publisher: str = ""
    edition: str = ""
    city: str = ""
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetadataFixer:
    """元数据修复器"""
    
    # 常见期刊名称映射
    JOURNAL_ABBREVIATIONS = {
        'journal of the american medical association': 'JAMA',
        'jama': 'JAMA',
        'new england journal of medicine': 'N Engl J Med',
        'nature medicine': 'Nat Med',
        'nature': 'Nature',
        'science': 'Science',
        'cell': 'Cell',
        'lancet': 'Lancet',
        'british medical journal': 'BMJ',
        'bmj': 'BMJ',
        'annals of internal medicine': 'Ann Intern Med',
        'circulation': 'Circulation',
        'pediatrics': 'Pediatrics',
        'american journal of public health': 'Am J Public Health',
        'journal of clinical medicine': 'J Clin Med',
        'journal of clinical oncology': 'J Clin Oncol',
        'clinical cancer research': 'Clin Cancer Res',
        'cancer research': 'Cancer Res',
        'blood': 'Blood',
        'nature communications': 'Nat Commun',
        'scientific reports': 'Sci Rep',
        'plos one': 'PLoS One',
        'international journal of cancer': 'Int J Cancer',
        'cancer': 'Cancer',
        'journal of the national cancer institute': 'J Natl Cancer Inst',
    }
    
    # 常见的单词缩写规则 (ISO 4)
    WORD_ABBREVIATIONS = {
        'journal': 'J',
        'international': 'Int',
        'medicine': 'Med',
        'medical': 'Med',
        'clinical': 'Clin',
        'research': 'Res',
        'review': 'Rev',
        'annals': 'Ann',
        'annual': 'Annu',
        'bulletin': 'Bull',
        'cancer': 'Cancer',
        'disease': 'Dis',
        'diseases': 'Dis',
        'experimental': 'Exp',
        'national': 'Natl',
        'surgery': 'Surg',
        'surgical': 'Surg',
        'treatment': 'Treat',
        'university': 'Univ',
    }
    
    def fix_author_name(self, name: str) -> Dict[str, str]:
        """修复作者姓名格式"""
        name = name.strip()
        if not name:
            return {'last': '', 'first': '', 'middle': ''}
        
        # 处理 "Lastname, Firstname Middle" 格式
        if ',' in name:
            parts = name.split(',')
            last = parts[0].strip()
            rest = parts[1].strip()
            name_parts = rest.split()
            first = name_parts[0] if name_parts else ''
            middle = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        else:
            # 处理 "Firstname Middle Lastname" 格式
            parts = name.split()
            if len(parts) == 1:
                last = parts[0]
                first = ''
                middle = ''
            elif len(parts) == 2:
                first = parts[0]
                last = parts[1]
                middle = ''
            else:
                # 检查中间是否是缩写
                first = parts[0]
                last = parts[-1]
                middle = ' '.join(parts[1:-1])
        
        # 标准化首字母
        first = first.strip('.').strip()
        middle = middle.strip('.').strip()
        last = last.strip()
        
        return {'last': last, 'first': first, 'middle': middle}
    
    def format_author_ama(self, author: Dict[str, str]) -> str:
        """格式化为 AMA 作者格式: Lastname FM"""
        last = author.get('last', '')
        first = author.get('first', '')
        middle = author.get('middle', '')
        
        initials = ''
        if first:
            initials += first[0].upper()
        if middle:
            for part in middle.split():
                if part:
                    initials += part[0].upper()
        
        return f"{last} {initials}" if initials else last
    
    def fix_journal_name(self, journal: str, style: str = 'ama') -> str:
        """修复期刊名称"""
        if not journal:
            return ''
        
        journal_lower = journal.lower().strip()
        
        # 检查常见期刊映射
        for key, val in self.JOURNAL_ABBREVIATIONS.items():
            if key in journal_lower:
                return val
        
        if style == 'ama':
            # AMA 风格: 缩写期刊名
            words = journal_lower.split()
            abbreviated = []
            for word in words:
                clean_word = re.sub(r'[^\w]', '', word.lower())
                if clean_word in self.WORD_ABBREVIATIONS:
                    abbreviated.append(self.WORD_ABBREVIATIONS[clean_word])
                else:
                    abbreviated.append(word.capitalize())
            return ' '.join(abbreviated)
        else:
            # 其他风格: 标题格式
            return journal.title()
    
    def fix_doi(self, doi: str) -> str:
        """修复 DOI 格式"""
        if not doi:
            return ''
        
        doi = doi.strip()
        
        # 移除前缀 (支持 http/https/www)
        doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
        doi = re.sub(r'^www\.doi\.org/', '', doi)
        doi = re.sub(r'^(doi|DOI)[\s:]*', '', doi)
        
        # 确保格式正确
        if doi.startswith('10.'):
            return f"doi:{doi}"
        return doi
    
    def fix_pages(self, pages: str) -> str:
        """修复页码格式"""
        if not pages:
            return ''
        
        # 标准化分隔符
        pages = pages.replace('--', '-').replace('–', '-').replace('—', '-')
        pages = pages.replace(' ', '')
        
        # 处理 e123-e456 格式
        if re.match(r'^e?\d+-e?\d+$', pages):
            return pages
        
        # 处理单个页码
        if re.match(r'^\d+$', pages):
            return pages
        
        return pages
    
    def fix_year(self, year: str) -> str:
        """修复年份格式"""
        if not year:
            return ''
        
        # 提取4位年份
        match = re.search(r'\b(19|20)\d{2}\b', str(year))
        if match:
            return match.group(0)
        return year
    
    def fix_title_case(self, title: str, style: str = 'ama') -> str:
        """修复标题大小写"""
        if not title:
            return ''
        
        if style == 'ama':
            # AMA: 首字母大写，冒号后首字母大写
            words = title.split()
            result = []
            capitalize_next = True
            
            small_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 
                          'on', 'at', 'to', 'from', 'by', 'in', 'of', 'with'}
            
            for i, word in enumerate(words):
                if capitalize_next:
                    result.append(word.capitalize())
                    capitalize_next = False
                elif word.lower() in small_words and i > 0:
                    result.append(word.lower())
                else:
                    result.append(word.capitalize())
                
                if word.endswith(':') or word.endswith('?'):
                    capitalize_next = True
            
            return ' '.join(result)
        else:
            return title


class ReferenceParser:
    """文献解析器"""
    
    def __init__(self):
        self.fixer = MetadataFixer()
    
    def parse_bibtex(self, content: str) -> List[Reference]:
        """解析 BibTeX 格式"""
        references = []
        
        # 分割条目 - 使用更健壮的方式
        entry_pattern = r'@(\w+)\s*\{\s*([^,]+),(.*?)\n\s*\}'
        entries = re.findall(entry_pattern, content, re.DOTALL)
        
        for entry_type, entry_id, fields_text in entries:
            ref = Reference(id=entry_id.strip(), type=self._map_entry_type(entry_type))
            
            # 解析字段 - 处理多行值
            fields = re.findall(r'(\w+)\s*=\s*\{([^}]+)\}', fields_text, re.DOTALL)
            field_dict = {k.lower(): v.replace('\n', ' ').strip() for k, v in fields}
            
            # 解析作者
            if 'author' in field_dict:
                authors_str = field_dict['author']
                authors_str = authors_str.replace(' and ', '|')
                for author_str in authors_str.split('|'):
                    if author_str.strip() and author_str.strip().lower() != 'et al':
                        ref.authors.append(self.fixer.fix_author_name(author_str))
            
            ref.title = field_dict.get('title', '')
            ref.journal = field_dict.get('journal', '')
            ref.year = self.fixer.fix_year(field_dict.get('year', ''))
            ref.volume = field_dict.get('volume', '')
            ref.issue = field_dict.get('number', '')
            ref.pages = self.fixer.fix_pages(field_dict.get('pages', ''))
            ref.doi = field_dict.get('doi', '')
            ref.url = field_dict.get('url', '')
            ref.publisher = field_dict.get('publisher', '')
            ref.edition = field_dict.get('edition', '')
            
            references.append(ref)
        
        return references
    
    def parse_ris(self, content: str) -> List[Reference]:
        """解析 RIS 格式"""
        references = []
        entries = content.split('ER  -')
        
        for entry in entries:
            if not entry.strip():
                continue
            
            ref = Reference()
            lines = entry.strip().split('\n')
            
            for line in lines:
                if '  - ' in line:
                    tag, value = line.split('  - ', 1)
                    tag = tag.strip()
                    value = value.strip()
                    
                    if tag == 'TY':
                        ref.type = self._map_ris_type(value)
                    elif tag == 'ID':
                        ref.id = value
                    elif tag == 'AU' or tag == 'A1':
                        ref.authors.append(self.fixer.fix_author_name(value))
                    elif tag == 'TI' or tag == 'T1':
                        ref.title = value
                    elif tag == 'JO' or tag == 'JF' or tag == 'T2':
                        ref.journal = value
                    elif tag == 'PY' or tag == 'Y1':
                        ref.year = self.fixer.fix_year(value)
                    elif tag == 'VL':
                        ref.volume = value
                    elif tag == 'IS':
                        ref.issue = value
                    elif tag == 'SP':
                        ref.pages = value
                    elif tag == 'EP':
                        if ref.pages:
                            ref.pages = f"{ref.pages}-{value}"
                        else:
                            ref.pages = value
                    elif tag == 'DO':
                        ref.doi = value
                    elif tag == 'UR':
                        ref.url = value
                    elif tag == 'PB':
                        ref.publisher = value
            
            if ref.title or ref.authors:
                references.append(ref)
        
        return references
    
    def parse_json(self, content: str) -> List[Reference]:
        """解析 JSON/CSL JSON 格式"""
        data = json.loads(content)
        references = []
        
        # 处理数组或单个对象
        items = data if isinstance(data, list) else [data]
        if 'items' in data:
            items = data['items']
        
        for item in items:
            ref = Reference()
            ref.id = item.get('id', '')
            ref.type = item.get('type', 'journal')
            
            # 解析作者
            for author in item.get('author', []):
                ref.authors.append({
                    'last': author.get('family', ''),
                    'first': author.get('given', ''),
                    'middle': ''
                })
            
            ref.title = item.get('title', '')
            
            # 期刊名可能在 container-title
            container = item.get('container-title', [])
            if container:
                ref.journal = container[0] if isinstance(container, list) else container
            
            # 处理日期
            date_parts = item.get('issued', {}).get('date-parts', [[]])
            if date_parts and date_parts[0]:
                ref.year = str(date_parts[0][0])
            
            ref.volume = str(item.get('volume', ''))
            ref.issue = str(item.get('issue', ''))
            
            # 页码
            page = item.get('page', '')
            if page:
                ref.pages = self.fixer.fix_pages(page)
            
            ref.doi = item.get('DOI', '')
            ref.url = item.get('URL', '')
            ref.publisher = item.get('publisher', '')
            
            references.append(ref)
        
        return references
    
    def parse_csv(self, content: str) -> List[Reference]:
        """解析 CSV 格式"""
        references = []
        reader = csv.DictReader(content.splitlines())
        
        for row in reader:
            ref = Reference()
            ref.id = row.get('id', '')
            ref.title = row.get('title', '')
            ref.journal = row.get('journal', '')
            ref.year = self.fixer.fix_year(row.get('year', ''))
            ref.volume = row.get('volume', '')
            ref.issue = row.get('issue', '')
            ref.pages = self.fixer.fix_pages(row.get('pages', ''))
            ref.doi = row.get('doi', '')
            ref.url = row.get('url', '')
            
            # 解析作者
            authors_str = row.get('authors', '')
            if authors_str:
                for author in authors_str.split(';'):
                    ref.authors.append(self.fixer.fix_author_name(author))
            
            references.append(ref)
        
        return references
    
    def _map_entry_type(self, bibtex_type: str) -> str:
        """映射 BibTeX 类型"""
        type_map = {
            'article': 'journal',
            'book': 'book',
            'inbook': 'book',
            'incollection': 'book',
            'inproceedings': 'conference',
            'conference': 'conference',
            'proceedings': 'conference',
            'phdthesis': 'thesis',
            'mastersthesis': 'thesis',
            'techreport': 'report',
            'misc': 'webpage',
        }
        return type_map.get(bibtex_type.lower(), 'journal')
    
    def _map_ris_type(self, ris_type: str) -> str:
        """映射 RIS 类型"""
        type_map = {
            'JOUR': 'journal',
            'BOOK': 'book',
            'CHAP': 'book',
            'CONF': 'conference',
            'THES': 'thesis',
            'RPRT': 'report',
            'ELEC': 'webpage',
        }
        return type_map.get(ris_type.upper(), 'journal')


class ReferenceExporter:
    """文献导出器"""
    
    def __init__(self, style: str = 'ama'):
        self.style = style
        self.fixer = MetadataFixer()
    
    def export_bibtex(self, references: List[Reference]) -> str:
        """导出为 BibTeX 格式"""
        lines = []
        
        for ref in references:
            entry_type = 'article' if ref.type == 'journal' else ref.type
            lines.append(f"@{entry_type}{{{ref.id},")
            
            # 作者
            if ref.authors:
                authors_str = ' and '.join([
                    f"{a['last']}, {a['first']} {a['middle']}".strip()
                    for a in ref.authors
                ])
                lines.append(f"  author = {{{authors_str}}},")
            
            lines.append(f"  title = {{{ref.title}}},")
            
            if ref.journal:
                lines.append(f"  journal = {{{self.fixer.fix_journal_name(ref.journal, self.style)}}},")
            if ref.year:
                lines.append(f"  year = {{{ref.year}}},")
            if ref.volume:
                lines.append(f"  volume = {{{ref.volume}}},")
            if ref.issue:
                lines.append(f"  number = {{{ref.issue}}},")
            if ref.pages:
                lines.append(f"  pages = {{{ref.pages}}},")
            if ref.doi:
                lines.append(f"  doi = {{{self.fixer.fix_doi(ref.doi)}}},")
            if ref.url:
                lines.append(f"  url = {{{ref.url}}},")
            if ref.publisher:
                lines.append(f"  publisher = {{{ref.publisher}}},")
            
            lines.append('}\n')
        
        return '\n'.join(lines)
    
    def export_ris(self, references: List[Reference]) -> str:
        """导出为 RIS 格式"""
        lines = []
        
        type_map = {
            'journal': 'JOUR',
            'book': 'BOOK',
            'conference': 'CONF',
            'thesis': 'THES',
            'report': 'RPRT',
            'webpage': 'ELEC',
        }
        
        for ref in references:
            lines.append(f"TY  - {type_map.get(ref.type, 'JOUR')}")
            lines.append(f"ID  - {ref.id}")
            
            for author in ref.authors:
                name = f"{author['last']}, {author['first']} {author['middle']}".strip()
                lines.append(f"AU  - {name}")
            
            lines.append(f"TI  - {ref.title}")
            
            if ref.journal:
                lines.append(f"JO  - {self.fixer.fix_journal_name(ref.journal, self.style)}")
            if ref.year:
                lines.append(f"PY  - {ref.year}")
            if ref.volume:
                lines.append(f"VL  - {ref.volume}")
            if ref.issue:
                lines.append(f"IS  - {ref.issue}")
            if ref.pages:
                if '-' in ref.pages:
                    start, end = ref.pages.split('-', 1)
                    lines.append(f"SP  - {start}")
                    lines.append(f"EP  - {end}")
                else:
                    lines.append(f"SP  - {ref.pages}")
            if ref.doi:
                lines.append(f"DO  - {self.fixer.fix_doi(ref.doi)}")
            if ref.url:
                lines.append(f"UR  - {ref.url}")
            if ref.publisher:
                lines.append(f"PB  - {ref.publisher}")
            
            lines.append('ER  - \n')
        
        return '\n'.join(lines)
    
    def export_json(self, references: List[Reference]) -> str:
        """导出为 CSL JSON 格式"""
        items = []
        
        for ref in references:
            item = {
                'id': ref.id,
                'type': ref.type,
                'title': ref.title,
            }
            
            if ref.authors:
                item['author'] = [
                    {'family': a['last'], 'given': f"{a['first']} {a['middle']}".strip()}
                    for a in ref.authors
                ]
            
            if ref.journal:
                item['container-title'] = self.fixer.fix_journal_name(ref.journal, self.style)
            if ref.year:
                item['issued'] = {'date-parts': [[int(ref.year)]]}
            if ref.volume:
                item['volume'] = ref.volume
            if ref.issue:
                item['issue'] = ref.issue
            if ref.pages:
                item['page'] = ref.pages
            if ref.doi:
                item['DOI'] = ref.doi.replace('doi:', '')
            if ref.url:
                item['URL'] = ref.url
            if ref.publisher:
                item['publisher'] = ref.publisher
            
            items.append(item)
        
        return json.dumps({'items': items}, indent=2, ensure_ascii=False)
    
    def export_csv(self, references: List[Reference]) -> str:
        """导出为 CSV 格式"""
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(['id', 'type', 'authors', 'title', 'journal', 'year', 
                        'volume', 'issue', 'pages', 'doi', 'url'])
        
        for ref in references:
            authors_str = '; '.join([
                f"{a['last']}, {a['first']} {a['middle']}".strip()
                for a in ref.authors
            ])
            
            writer.writerow([
                ref.id,
                ref.type,
                authors_str,
                ref.title,
                self.fixer.fix_journal_name(ref.journal, self.style),
                ref.year,
                ref.volume,
                ref.issue,
                ref.pages,
                ref.doi,
                ref.url
            ])
        
        return output.getvalue()


class ReferenceSync:
    """文献同步主类"""
    
    def __init__(self):
        self.references: List[Reference] = []
        self.parser = ReferenceParser()
        self.fixer = MetadataFixer()
        self.errors: List[str] = []
    
    def load(self, filepath: str) -> 'ReferenceSync':
        """加载文献库文件"""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 根据扩展名判断格式
        ext = path.suffix.lower()
        
        if ext == '.bib':
            self.references = self.parser.parse_bibtex(content)
        elif ext == '.ris':
            self.references = self.parser.parse_ris(content)
        elif ext == '.json':
            self.references = self.parser.parse_json(content)
        elif ext == '.csv':
            self.references = self.parser.parse_csv(content)
        else:
            # 尝试自动检测
            if content.strip().startswith('@'):
                self.references = self.parser.parse_bibtex(content)
            elif 'TY  -' in content:
                self.references = self.parser.parse_ris(content)
            else:
                try:
                    self.references = self.parser.parse_json(content)
                except json.JSONDecodeError:
                    raise ValueError(f"无法识别的文件格式: {ext}")
        
        print(f"已加载 {len(self.references)} 条文献")
        return self
    
    def fix_metadata(self) -> 'ReferenceSync':
        """修复元数据"""
        fixed_count = 0
        
        for ref in self.references:
            changes = []
            
            # 修复 DOI (先去重需要用到)
            if ref.doi:
                old_doi = ref.doi
                ref.doi = self.fixer.fix_doi(ref.doi)
                if old_doi != ref.doi:
                    changes.append(f"DOI: {old_doi} -> {ref.doi}")
            
            # 修复作者
            if ref.authors:
                fixed_authors = []
                for author in ref.authors:
                    fixed = self.fixer.fix_author_name(
                        f"{author['last']}, {author['first']} {author['middle']}".strip()
                    )
                    fixed_authors.append(fixed)
                ref.authors = fixed_authors
            
            # 修复期刊名
            if ref.journal:
                old_journal = ref.journal
                ref.journal = self.fixer.fix_journal_name(ref.journal)
                if old_journal != ref.journal:
                    changes.append(f"期刊: {old_journal} -> {ref.journal}")
            
            # 修复页码
            if ref.pages:
                old_pages = ref.pages
                ref.pages = self.fixer.fix_pages(ref.pages)
                if old_pages != ref.pages:
                    changes.append(f"页码: {old_pages} -> {ref.pages}")
            
            # 修复年份
            if ref.year:
                old_year = ref.year
                ref.year = self.fixer.fix_year(ref.year)
                if old_year != ref.year:
                    changes.append(f"年份: {old_year} -> {ref.year}")
            
            # 修复标题
            if ref.title:
                ref.title = self.fixer.fix_title_case(ref.title)
            
            if changes:
                fixed_count += 1
        
        print(f"已修复 {fixed_count} 条文献的元数据")
        return self
    
    def deduplicate(self) -> 'ReferenceSync':
        """检测并去重"""
        seen = {}
        duplicates = []
        unique_refs = []
        
        for ref in self.references:
            # 生成唯一键 (基于 DOI 或标题+年份)
            key = ref.doi if ref.doi else f"{ref.title.lower()}_{ref.year}"
            
            if key in seen:
                duplicates.append(ref)
            else:
                seen[key] = ref
                unique_refs.append(ref)
        
        removed = len(self.references) - len(unique_refs)
        self.references = unique_refs
        
        print(f"发现 {removed} 条重复文献，已移除")
        return self
    
    def quality_check(self) -> Dict[str, Any]:
        """质量检查"""
        issues = {
            'missing_doi': [],
            'missing_pages': [],
            'missing_year': [],
            'missing_authors': [],
            'missing_journal': [],
            'invalid_doi': [],
            'total': len(self.references)
        }
        
        for ref in self.references:
            if not ref.doi:
                issues['missing_doi'].append(ref.id or ref.title[:50])
            elif not re.match(r'^doi:10\.\d{4,}/\S+$', ref.doi):
                issues['invalid_doi'].append(ref.id or ref.title[:50])
            
            if not ref.pages:
                issues['missing_pages'].append(ref.id or ref.title[:50])
            if not ref.year:
                issues['missing_year'].append(ref.id or ref.title[:50])
            if not ref.authors:
                issues['missing_authors'].append(ref.id or ref.title[:50])
            if not ref.journal and ref.type == 'journal':
                issues['missing_journal'].append(ref.id or ref.title[:50])
        
        return issues
    
    def export(self, filepath: str, style: str = 'ama') -> 'ReferenceSync':
        """导出文献库"""
        path = Path(filepath)
        exporter = ReferenceExporter(style)
        
        ext = path.suffix.lower()
        
        if ext == '.bib':
            content = exporter.export_bibtex(self.references)
        elif ext == '.ris':
            content = exporter.export_ris(self.references)
        elif ext == '.json':
            content = exporter.export_json(self.references)
        elif ext == '.csv':
            content = exporter.export_csv(self.references)
        else:
            # 默认 BibTeX
            content = exporter.export_bibtex(self.references)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已导出 {len(self.references)} 条文献到 {filepath}")
        return self


def main():
    parser = argparse.ArgumentParser(
        description='Reference Style Sync - 统一文献格式，修复元数据错误'
    )
    parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--style', '-s', default='ama',
                        choices=['apa', 'mla', 'ama', 'vancouver', 'chicago'],
                        help='目标引用格式 (默认: ama)')
    parser.add_argument('--fix-metadata', '-f', action='store_true',
                        help='启用元数据修复')
    parser.add_argument('--deduplicate', '-d', action='store_true',
                        help='检测并移除重复条目')
    parser.add_argument('--check-only', '-c', action='store_true',
                        help='仅执行质量检查')
    
    args = parser.parse_args()
    
    # 创建同步器
    sync = ReferenceSync()
    
    try:
        # 加载文件
        sync.load(args.input)
        
        # 仅检查模式
        if args.check_only:
            issues = sync.quality_check()
            print("\n=== 质量检查报告 ===")
            print(f"总文献数: {issues['total']}")
            print(f"缺少 DOI: {len(issues['missing_doi'])} 条")
            print(f"无效 DOI: {len(issues['invalid_doi'])} 条")
            print(f"缺少页码: {len(issues['missing_pages'])} 条")
            print(f"缺少年份: {len(issues['missing_year'])} 条")
            print(f"缺少作者: {len(issues['missing_authors'])} 条")
            print(f"缺少期刊: {len(issues['missing_journal'])} 条")
            return
        
        # 修复元数据
        if args.fix_metadata:
            sync.fix_metadata()
        
        # 去重
        if args.deduplicate:
            sync.deduplicate()
        
        # 导出
        if args.output:
            sync.export(args.output, args.style)
        else:
            # 默认输出到控制台
            exporter = ReferenceExporter(args.style)
            print("\n=== 处理结果 ===")
            print(exporter.export_bibtex(sync.references))
    
    except Exception as e:
        print(f"错误: {e}")
        raise


if __name__ == '__main__':
    main()
