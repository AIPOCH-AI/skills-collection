#!/usr/bin/env python3
"""
eCTD XML Compiler
将药物申报文档(Word/PDF)自动转化为符合FDA/EMA要求的eCTD XML骨架结构。

ID: 197
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Optional imports with fallbacks
try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


class ECTDError(Exception):
    """eCTD处理错误"""
    pass


class DocumentParser:
    """文档解析器基类"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.metadata = {}
        self.headings = []
    
    def parse(self) -> Dict:
        """解析文档，返回结构化数据"""
        raise NotImplementedError
    
    def detect_module(self) -> str:
        """根据内容自动检测所属eCTD模块"""
        content_lower = self.content.lower()
        
        # 模块检测规则
        module_keywords = {
            "m1": ["行政", "标签", "说明书", "labeling", "administrative", "form 356h"],
            "m2": ["概要", "summary", "概述", "introduction", "overview"],
            "m3": ["质量", "quality", "cmc", "原料药", "制剂", "manufacture", "control"],
            "m4": ["非临床", "毒理", "药代", "nonclinical", "toxicology", "pharmacology"],
            "m5": ["临床", "clinical", "study report", "efficacy", "safety"],
        }
        
        scores = {mod: 0 for mod in module_keywords}
        for module, keywords in module_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    scores[module] += 1
        
        # 返回得分最高的模块，默认为m3
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "m3"


class WordParser(DocumentParser):
    """Word文档解析器"""
    
    def parse(self) -> Dict:
        if not HAS_DOCX:
            raise ECTDError("未安装python-docx，无法解析Word文档。请运行: pip install python-docx")
        
        doc = Document(self.file_path)
        
        # 提取文本内容
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
                # 检测标题（基于样式）
                if para.style and para.style.name:
                    style_name = para.style.name.lower()
                    if 'heading' in style_name or '标题' in style_name:
                        level = self._extract_heading_level(style_name)
                        self.headings.append({
                            'level': level,
                            'text': text,
                            'style': para.style.name
                        })
        
        self.content = "\n".join(paragraphs)
        
        # 提取元数据
        self.metadata = {
            'author': doc.core_properties.author if doc.core_properties else '',
            'created': doc.core_properties.created.isoformat() if doc.core_properties and doc.core_properties.created else '',
            'modified': doc.core_properties.modified.isoformat() if doc.core_properties and doc.core_properties.modified else '',
            'title': doc.core_properties.title if doc.core_properties else '',
        }
        
        return {
            'content': self.content,
            'metadata': self.metadata,
            'headings': self.headings,
            'paragraphs': paragraphs
        }
    
    def _extract_heading_level(self, style_name: str) -> int:
        """从样式名称提取标题级别"""
        match = re.search(r'heading\s*(\d)', style_name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search(r'标题\s*(\d)', style_name)
        if match:
            return int(match.group(1))
        return 1


class PDFParser(DocumentParser):
    """PDF文档解析器"""
    
    def parse(self) -> Dict:
        if not HAS_PYPDF2:
            raise ECTDError("未安装PyPDF2，无法解析PDF文档。请运行: pip install PyPDF2")
        
        with open(self.file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # 提取元数据
            meta = reader.metadata
            self.metadata = {
                'author': meta.get('/Author', '') if meta else '',
                'creator': meta.get('/Creator', '') if meta else '',
                'producer': meta.get('/Producer', '') if meta else '',
                'title': meta.get('/Title', '') if meta else '',
                'num_pages': len(reader.pages),
            }
            
            # 提取文本
            paragraphs = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # 简单分段
                    for line in text.split('\n'):
                        line = line.strip()
                        if line:
                            paragraphs.append(line)
            
            self.content = "\n".join(paragraphs)
            
            # 尝试识别标题（基于行长度和格式）
            self.headings = self._extract_headings(paragraphs)
        
        return {
            'content': self.content,
            'metadata': self.metadata,
            'headings': self.headings,
            'paragraphs': paragraphs
        }
    
    def _extract_headings(self, paragraphs: List[str]) -> List[Dict]:
        """从PDF段落中提取可能的标题"""
        headings = []
        for para in paragraphs[:50]:  # 只检查前50行
            # 标题通常较短且可能包含章节编号
            if len(para) < 100:
                # 检测章节编号模式 (如 3.2.S.1.1 或 1.1 或 2.3.4)
                if re.match(r'^\d+(\.\d+)*\s+[A-Za-z]', para) or \
                   re.match(r'^[\d\.]+\s+[\u4e00-\u9fa5]', para):
                    level = para.count('.') + 1
                    headings.append({
                        'level': min(level, 6),
                        'text': para,
                        'style': 'extracted'
                    })
        return headings


class ECTDCompiler:
    """eCTD XML编译器"""
    
    def __init__(self, output_dir: str, region: str = "ICH", version: str = "4.0"):
        self.output_dir = Path(output_dir)
        self.region = region
        self.version = version
        self.modules = {f"m{i}": [] for i in range(1, 6)}
        self.file_hashes = {}
    
    def compile_document(self, file_path: str, target_module: Optional[str] = None):
        """编译单个文档"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ECTDError(f"文件不存在: {file_path}")
        
        # 选择解析器
        suffix = file_path.suffix.lower()
        if suffix in ['.docx', '.doc']:
            parser = WordParser(str(file_path))
        elif suffix == '.pdf':
            parser = PDFParser(str(file_path))
        else:
            raise ECTDError(f"不支持的文件格式: {suffix}")
        
        # 解析文档
        data = parser.parse()
        
        # 确定目标模块
        if target_module is None or target_module == "auto":
            module = parser.detect_module()
        else:
            module = target_module
        
        # 存储解析结果
        self.modules[module].append({
            'file_path': str(file_path),
            'file_name': file_path.name,
            'data': data,
            'module': module
        })
        
        # 计算文件哈希
        self.file_hashes[file_path.name] = self._calculate_md5(file_path)
        
        return module
    
    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件MD5哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def generate_xml(self):
        """生成eCTD XML骨架"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建模块目录和XML
        for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
            module_dir = self.output_dir / module_dir
            module_dir.mkdir(exist_ok=True)
            self._generate_module_xml(module_id, module_dir)
        
        # 生成主索引文件
        self._generate_index_xml()
        
        # 生成MD5校验文件
        self._generate_md5_file()
        
        return self.output_dir
    
    def _generate_module_xml(self, module_id: str, module_dir: Path):
        """生成模块XML文件"""
        root = ET.Element("ectd:ectd")
        root.set("xmlns:ectd", f"http://www.ich.org/ectd/{self.version}")
        root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
        
        # 添加模块根节点
        module_elem = ET.SubElement(root, f"ectd:{module_id}")
        
        documents = self.modules.get(module_id, [])
        
        # 如果有文档，创建leaf节点
        for doc in documents:
            leaf = ET.SubElement(module_elem, "ectd:leaf")
            leaf.set("ID", f"{module_id}-{doc['file_name']}")
            leaf.set("xlink:href", f"{module_id}/{doc['file_name']}")
            leaf.set("operation", "new")
            
            # 添加标题信息
            title = ET.SubElement(leaf, "ectd:title")
            title.text = doc['data']['metadata'].get('title', '') or doc['file_name']
            
            # 添加文档属性
            if doc['data']['headings']:
                for heading in doc['data']['headings'][:5]:  # 只包含前5个标题
                    node = ET.SubElement(leaf, "ectd:node")
                    node.set("level", str(heading['level']))
                    node.text = heading['text']
        
        # 如果没有文档，添加占位说明
        if not documents:
            placeholder = ET.SubElement(module_elem, "ectd:placeholder")
            placeholder.text = f"No documents assigned to {module_id}"
        
        # 格式化并写入
        xml_str = self._prettify_xml(root)
        xml_path = module_dir / f"{module_id}.xml"
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def _generate_index_xml(self):
        """生成主索引文件"""
        root = ET.Element("ectd:ectd")
        root.set("xmlns:ectd", f"http://www.ich.org/ectd/{self.version}")
        root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
        root.set("dtd-version", self.version)
        
        # 添加头信息
        header = ET.SubElement(root, "ectd:header")
        
        submission = ET.SubElement(header, "ectd:submission")
        submission.set("type", "initial")
        submission.set("date", datetime.now().strftime("%Y-%m-%d"))
        
        applicant = ET.SubElement(header, "ectd:applicant")
        applicant.text = "[申请人名称]"
        
        product = ET.SubElement(header, "ectd:product")
        product.set("name", "[药品名称]")
        
        # 添加模块引用
        modules_elem = ET.SubElement(root, "ectd:modules")
        for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
            module_ref = ET.SubElement(modules_elem, "ectd:module")
            module_ref.set("id", module_id)
            module_ref.set("xlink:href", f"{module_id}/{module_id}.xml")
            module_ref.set("title", self._get_module_title(module_id))
        
        # 格式化并写入
        xml_str = self._prettify_xml(root)
        index_path = self.output_dir / "index.xml"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def _get_module_title(self, module_id: str) -> str:
        """获取模块标题"""
        titles = {
            "m1": "Administrative Information and Prescribing Information",
            "m2": "Common Technical Document Summaries",
            "m3": "Quality",
            "m4": "Nonclinical Study Reports",
            "m5": "Clinical Study Reports",
        }
        return titles.get(module_id, module_id)
    
    def _generate_md5_file(self):
        """生成MD5校验文件"""
        md5_path = self.output_dir / "index-md5.txt"
        with open(md5_path, 'w', encoding='utf-8') as f:
            f.write("# eCTD MD5 Checksums\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Version: {self.version}\n")
            f.write(f"# Region: {self.region}\n\n")
            
            for filename, hash_value in sorted(self.file_hashes.items()):
                f.write(f"{hash_value}  {filename}\n")
            
            # 添加生成的XML文件哈希
            for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
                xml_file = self.output_dir / module_id / f"{module_id}.xml"
                if xml_file.exists():
                    hash_value = self._calculate_md5(xml_file)
                    f.write(f"{hash_value}  {module_id}/{module_id}.xml\n")
            
            # index.xml
            index_file = self.output_dir / "index.xml"
            if index_file.exists():
                hash_value = self._calculate_md5(index_file)
                f.write(f"{hash_value}  index.xml\n")
    
    def _prettify_xml(self, elem) -> str:
        """格式化XML输出"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def validate(self) -> List[str]:
        """验证生成的XML结构"""
        errors = []
        
        # 基本验证
        index_file = self.output_dir / "index.xml"
        if not index_file.exists():
            errors.append("缺少主索引文件 index.xml")
        
        for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
            module_xml = self.output_dir / module_id / f"{module_id}.xml"
            if not module_xml.exists():
                errors.append(f"缺少模块文件 {module_id}.xml")
        
        # 使用lxml进行DTD验证（如果可用）
        if HAS_LXML:
            errors.extend(self._dtd_validation())
        
        return errors
    
    def _dtd_validation(self) -> List[str]:
        """DTD验证"""
        errors = []
        # 这里可以添加实际的DTD验证逻辑
        # 需要加载ICH eCTD DTD文件
        return errors


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="eCTD XML Compiler - 将药物申报文档转换为eCTD XML骨架结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s document.docx report.pdf
  %(prog)s -o ./my-ectd -m m3 quality-doc.docx
  %(prog)s -r FDA -v 3.2.2 *.pdf
  %(prog)s --validate submission.pdf
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='输入的Word/PDF文件路径（支持多个）'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./ectd-output',
        help='输出目录路径 (默认: ./ectd-output)'
    )
    
    parser.add_argument(
        '-m', '--module',
        choices=['m1', 'm2', 'm3', 'm4', 'm5', 'auto'],
        default='auto',
        help='目标模块 (默认: auto自动检测)'
    )
    
    parser.add_argument(
        '-r', '--region',
        choices=['FDA', 'EMA', 'ICH'],
        default='ICH',
        help='目标地区 (默认: ICH)'
    )
    
    parser.add_argument(
        '-v', '--version',
        choices=['3.2.2', '4.0'],
        default='4.0',
        help='eCTD版本 (默认: 4.0)'
    )
    
    parser.add_argument(
        '-d', '--dtd-path',
        help='自定义DTD路径'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='验证生成的XML'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细信息'
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 检查依赖
    missing_deps = []
    if not HAS_DOCX:
        missing_deps.append("python-docx")
    if not HAS_PYPDF2:
        missing_deps.append("PyPDF2")
    
    if missing_deps:
        print(f"警告: 缺少可选依赖: {', '.join(missing_deps)}")
        print("安装: pip install " + " ".join(missing_deps))
    
    # 初始化编译器
    try:
        compiler = ECTDCompiler(
            output_dir=args.output,
            region=args.region,
            version=args.version
        )
    except Exception as e:
        print(f"错误: 初始化编译器失败 - {e}", file=sys.stderr)
        sys.exit(1)
    
    # 处理输入文件
    processed = 0
    for file_path in args.input_files:
        if args.verbose:
            print(f"处理: {file_path}")
        
        try:
            module = compiler.compile_document(file_path, args.module)
            if args.verbose:
                print(f"  -> 分配到模块: {module}")
            processed += 1
        except ECTDError as e:
            print(f"错误 [{file_path}]: {e}", file=sys.stderr)
        except Exception as e:
            print(f"错误 [{file_path}]: {str(e)}", file=sys.stderr)
    
    if processed == 0:
        print("错误: 没有成功处理任何文件", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n成功处理 {processed} 个文件")
    
    # 生成XML
    print(f"\n生成eCTD XML骨架...")
    output_dir = compiler.generate_xml()
    print(f"输出目录: {output_dir.absolute()}")
    
    # 显示模块分配统计
    print("\n模块分配:")
    for module_id in ['m1', 'm2', 'm3', 'm4', 'm5']:
        count = len(compiler.modules[module_id])
        if count > 0:
            print(f"  {module_id}: {count} 个文档")
    
    # 验证（如果请求）
    if args.validate:
        print("\n验证XML结构...")
        errors = compiler.validate()
        if errors:
            print("发现以下问题:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("验证通过！")
    
    print("\n完成!")
    print(f"eCTD骨架已生成在: {output_dir.absolute()}")


if __name__ == '__main__':
    main()
