#!/usr/bin/env python3
"""
Vector Text Fixer - 修复PDF/SVG矢量图中的乱码文字
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class TextBlock:
    """文本块数据结构"""
    id: str
    bbox: List[float]  # [x0, y0, x1, y1]
    original_text: str
    page_num: int = 1
    font_info: Dict[str, Any] = None
    confidence: float = 1.0
    suggested_fix: str = ""
    is_garbled: bool = False


class GarbledTextDetector:
    """乱码文本检测器"""
    
    # 常见的乱码/替换字符
    REPLACEMENT_CHARS = {
        '\ufffd',  # � 替换字符
        '\u25a1',  # □ 方框
        '\u25a0',  # ■ 实心方框
        '\u25af',  # ▯ 空心方框
        '\u2588',  # █ 全块
        '\ufffe',  # � 非字符
        '\uffff',  # � 非字符
        '?',       # 问号替代
    }
    
    # 常见乱码模式
    GARBLED_PATTERNS = [
        r'[\u0000-\u0008\u000b-\u000c\u000e-\u001f]',  # 控制字符
        r'[\ufffd\u25a1\u25a0\u25af\u2588\ufffe\uffff]',  # 替换字符
        r'[�]{2,}',  # 连续替换字符
        r'(?:\\x[0-9a-fA-F]{2}){2,}',  # 转义序列
        r'[\x80-\x9f]',  # C1控制字符
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p) for p in self.GARBLED_PATTERNS]
    
    def is_garbled(self, text: str) -> Tuple[bool, float]:
        """
        检测文本是否为乱码
        返回: (是否乱码, 乱码置信度 0-1)
        """
        if not text or not isinstance(text, str):
            return False, 1.0
        
        text_len = len(text)
        if text_len == 0:
            return False, 1.0
        
        garbled_score = 0.0
        
        # 1. 检查替换字符
        replacement_count = sum(1 for c in text if c in self.REPLACEMENT_CHARS)
        garbled_score += (replacement_count / text_len) * 0.5
        
        # 2. 检查乱码模式
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                garbled_score += len(matches) / text_len * 0.3
        
        # 3. 检查字符分布异常
        if self._has_abnormal_distribution(text):
            garbled_score += 0.2
        
        # 4. 检查混合编码迹象
        if self._has_encoding_mixed(text):
            garbled_score += 0.15
        
        is_garbled = garbled_score > 0.15 or replacement_count > 0
        confidence = max(0.0, 1.0 - min(garbled_score, 1.0))
        
        return is_garbled, confidence
    
    def _has_abnormal_distribution(self, text: str) -> bool:
        """检查字符分布是否异常"""
        if len(text) < 3:
            return False
        
        # 统计不可打印字符比例
        unprintable = sum(1 for c in text if ord(c) < 32 and c not in '\t\n\r')
        ratio = unprintable / len(text)
        return ratio > 0.3
    
    def _has_encoding_mixed(self, text: str) -> bool:
        """检测是否存在混合编码迹象"""
        # 检测UTF-8多字节字符被错误解析的迹象
        # 如：Ã© 应该是 é (UTF-8字节被当作Latin-1解析)
        mixed_patterns = [
            r'Ã[\xa0-\xbf]',  # UTF-8被误解析为Latin-1
            r'Â[\x80-\xbf]',
            r'Ã¢',
            r'Ã£',
        ]
        for pattern in mixed_patterns:
            if re.search(pattern, text):
                return True
        return False


class PDFFixer:
    """PDF文本修复器"""
    
    def __init__(self, detector: GarbledTextDetector):
        self.detector = detector
        self.text_blocks: List[TextBlock] = []
    
    def fix(self, input_path: str, output_path: str, 
            repair_level: str = "standard") -> Dict[str, Any]:
        """
        修复PDF文件中的乱码文字
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            return {
                "success": False,
                "error": "PyMuPDF (fitz) is required. Install: pip install PyMuPDF"
            }
        
        try:
            doc = fitz.open(input_path)
        except Exception as e:
            return {"success": False, "error": f"Cannot open PDF: {str(e)}"}
        
        self.text_blocks = []
        repair_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = self._extract_text_blocks(page, page_num + 1)
            
            for block in blocks:
                is_garbled, confidence = self.detector.is_garbled(block.original_text)
                
                if is_garbled:
                    block.is_garbled = True
                    block.confidence = confidence
                    block.suggested_fix = self._suggest_fix(
                        block.original_text, 
                        repair_level
                    )
                    repair_count += 1
                
                self.text_blocks.append(block)
        
        # 生成修复报告
        result = {
            "success": True,
            "file_type": "pdf",
            "pages": len(doc),
            "total_blocks": len(self.text_blocks),
            "garbled_blocks": repair_count,
            "text_blocks": [asdict(b) for b in self.text_blocks],
            "output_path": output_path
        }
        
        doc.close()
        return result
    
    def _extract_text_blocks(self, page, page_num: int) -> List[TextBlock]:
        """从PDF页面提取文本块"""
        blocks = []
        
        try:
            import fitz
            
            # 获取页面上的文本块
            text_dict = page.get_text("dict")
            
            block_id = 0
            for block in text_dict.get("blocks", []):
                if "lines" in block:  # 文本块
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if text.strip():
                                bbox = span.get("bbox", [0, 0, 0, 0])
                                font_info = {
                                    "font": span.get("font", "Unknown"),
                                    "size": span.get("size", 0),
                                    "flags": span.get("flags", 0),
                                    "color": span.get("color", 0)
                                }
                                
                                tb = TextBlock(
                                    id=f"p{page_num}_b{block_id}",
                                    bbox=list(bbox),
                                    original_text=text,
                                    page_num=page_num,
                                    font_info=font_info
                                )
                                blocks.append(tb)
                                block_id += 1
        except Exception as e:
            print(f"Warning: Error extracting text: {e}")
        
        return blocks
    
    def _suggest_fix(self, garbled_text: str, repair_level: str) -> str:
        """根据乱码内容建议修复文本"""
        # 这里可以实现更复杂的修复逻辑
        # 目前返回占位符，提示用户手动输入
        
        if repair_level == "minimal":
            # 最小修复：只移除替换字符
            return garbled_text.replace('\ufffd', '').strip()
        
        elif repair_level == "aggressive":
            # 深度修复：尝试解码常见的编码错误
            return self._try_decode_fixes(garbled_text)
        
        else:  # standard
            # 标准修复：标记需要用户确认
            if all(c in GarbledTextDetector.REPLACEMENT_CHARS for c in garbled_text):
                return f"[需手动输入 - 原文: {len(garbled_text)}个乱码字符]"
            else:
                return garbled_text.replace('\ufffd', '[?]').strip()
    
    def _try_decode_fixes(self, text: str) -> str:
        """尝试多种编码修复"""
        # 常见的编码错误模式修复
        fixes = []
        
        # UTF-8被当作Latin-1解析
        try:
            fixed = text.encode('latin-1').decode('utf-8')
            fixes.append(fixed)
        except:
            pass
        
        # GBK/GB2312问题
        try:
            fixed = text.encode('latin-1').decode('gbk', errors='ignore')
            fixes.append(fixed)
        except:
            pass
        
        # 返回第一个看起来合理的修复
        for fix in fixes:
            if not self.detector.is_garbled(fix)[0]:
                return fix
        
        return f"[需手动输入]"


class SVGFixer:
    """SVG文本修复器"""
    
    def __init__(self, detector: GarbledTextDetector):
        self.detector = detector
        self.text_elements: List[TextBlock] = []
    
    def fix(self, input_path: str, output_path: str,
            repair_level: str = "standard") -> Dict[str, Any]:
        """
        修复SVG文件中的乱码文字
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return {
                "success": False,
                "error": "BeautifulSoup4 is required. Install: pip install beautifulsoup4"
            }
        
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {"success": False, "error": f"Cannot read SVG: {str(e)}"}
        
        soup = BeautifulSoup(content, 'xml')
        
        # 提取所有文本元素
        self.text_elements = []
        repair_count = 0
        
        text_tags = soup.find_all(['text', 'tspan', 'textPath'])
        
        for idx, tag in enumerate(text_tags):
            text_content = tag.get_text()
            if not text_content.strip():
                continue
            
            is_garbled, confidence = self.detector.is_garbled(text_content)
            
            # 获取位置和字体信息
            x = tag.get('x', '0')
            y = tag.get('y', '0')
            font_family = tag.get('font-family', 'default')
            font_size = tag.get('font-size', '12')
            
            tb = TextBlock(
                id=f"text_{idx}",
                bbox=[float(x) if x else 0, float(y) if y else 0, 0, 0],
                original_text=text_content,
                font_info={
                    "font_family": font_family,
                    "font_size": font_size
                },
                page_num=1
            )
            
            if is_garbled:
                tb.is_garbled = True
                tb.confidence = confidence
                tb.suggested_fix = self._suggest_fix(text_content, repair_level)
                repair_count += 1
            
            self.text_elements.append(tb)
        
        # 获取SVG基本信息
        svg_tag = soup.find('svg')
        svg_info = {
            "width": svg_tag.get('width', 'unknown') if svg_tag else 'unknown',
            "height": svg_tag.get('height', 'unknown') if svg_tag else 'unknown',
            "viewBox": svg_tag.get('viewBox', '') if svg_tag else ''
        }
        
        result = {
            "success": True,
            "file_type": "svg",
            "svg_info": svg_info,
            "total_elements": len(self.text_elements),
            "garbled_elements": repair_count,
            "text_elements": [asdict(t) for t in self.text_elements],
            "output_path": output_path
        }
        
        return result
    
    def _suggest_fix(self, garbled_text: str, repair_level: str) -> str:
        """建议SVG文本修复"""
        if repair_level == "minimal":
            return garbled_text.replace('\ufffd', '').strip()
        elif repair_level == "aggressive":
            return self._try_xml_entity_fix(garbled_text)
        else:
            if '\ufffd' in garbled_text:
                return f"[需手动输入 - 原文: {len(garbled_text)}个乱码字符]"
            return garbled_text
    
    def _try_xml_entity_fix(self, text: str) -> str:
        """尝试修复XML实体编码问题"""
        import html
        # 解码HTML实体
        decoded = html.unescape(text)
        if not self.detector.is_garbled(decoded)[0]:
            return decoded
        return f"[需手动输入]"


class VectorTextFixer:
    """矢量文本修复器主类"""
    
    def __init__(self):
        self.detector = GarbledTextDetector()
        self.pdf_fixer = PDFFixer(self.detector)
        self.svg_fixer = SVGFixer(self.detector)
    
    def fix_file(self, input_path: str, output_path: str,
                 repair_level: str = "standard") -> Dict[str, Any]:
        """
        根据文件类型自动选择修复方法
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            return {"success": False, "error": f"File not found: {input_path}"}
        
        suffix = input_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.pdf_fixer.fix(str(input_path), output_path, repair_level)
        elif suffix == '.svg':
            return self.svg_fixer.fix(str(input_path), output_path, repair_level)
        else:
            return {"success": False, "error": f"Unsupported file format: {suffix}"}
    
    def batch_fix(self, input_folder: str, output_folder: str,
                  repair_level: str = "standard") -> List[Dict[str, Any]]:
        """
        批量修复文件夹中的PDF/SVG文件
        """
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for file_path in input_folder.iterdir():
            if file_path.suffix.lower() in ['.pdf', '.svg']:
                output_path = output_folder / f"fixed_{file_path.name}"
                result = self.fix_file(str(file_path), str(output_path), repair_level)
                results.append(result)
        
        return results
    
    def export_editable_json(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        导出可编辑的JSON格式，用于AI工具中手动修复
        """
        result = self.fix_file(input_path, "", repair_level="standard")
        
        if not result.get("success"):
            return result
        
        # 添加可编辑标记
        editable_data = {
            "file_info": {
                "original_path": input_path,
                "exported_at": self._get_timestamp(),
                "tool": "Vector Text Fixer v1.0.0"
            },
            "repair_data": result
        }
        
        # 添加用户可编辑字段
        if result["file_type"] == "pdf":
            for block in editable_data["repair_data"]["text_blocks"]:
                block["user_editable"] = block.get("suggested_fix", "")
        elif result["file_type"] == "svg":
            for elem in editable_data["repair_data"]["text_elements"]:
                elem["user_editable"] = elem.get("suggested_fix", "")
        
        # 保存JSON
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(editable_data, f, ensure_ascii=False, indent=2)
            editable_data["export_success"] = True
        except Exception as e:
            editable_data["export_success"] = False
            editable_data["export_error"] = str(e)
        
        return editable_data
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='Vector Text Fixer - 修复PDF/SVG矢量图中的乱码文字'
    )
    
    # 输入选项
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', '-i', help='输入文件路径 (PDF或SVG)')
    input_group.add_argument('--batch', '-b', help='批量处理输入文件夹')
    
    # 输出选项
    parser.add_argument('--output', '-o', help='输出文件/文件夹路径')
    parser.add_argument('--export-json', '-j', help='导出可编辑JSON格式')
    
    # 修复选项
    parser.add_argument('--repair-level', '-r', 
                       choices=['minimal', 'standard', 'aggressive'],
                       default='standard',
                       help='修复级别 (默认: standard)')
    parser.add_argument('--interactive', action='store_true',
                       help='启用交互式修复模式')
    
    args = parser.parse_args()
    
    # 创建修复器实例
    fixer = VectorTextFixer()
    
    # 导出JSON模式
    if args.export_json:
        if not args.input:
            print("错误: --export-json 需要指定 --input")
            sys.exit(1)
        
        result = fixer.export_editable_json(args.input, args.export_json)
        
        if result.get("export_success"):
            print(f"✓ JSON导出成功: {args.export_json}")
            print(f"  文件类型: {result['repair_data'].get('file_type')}")
            print(f"  检测到的文本块: {result['repair_data'].get('total_blocks') or result['repair_data'].get('total_elements')}")
            print(f"  乱码文本块: {result['repair_data'].get('garbled_blocks') or result['repair_data'].get('garbled_elements')}")
        else:
            print(f"✗ 导出失败: {result.get('export_error', 'Unknown error')}")
            sys.exit(1)
        return
    
    # 批量处理模式
    if args.batch:
        if not args.output:
            print("错误: 批量处理需要指定 --output")
            sys.exit(1)
        
        print(f"开始批量处理: {args.batch}")
        results = fixer.batch_fix(args.batch, args.output, args.repair_level)
        
        success_count = sum(1 for r in results if r.get("success"))
        total_count = len(results)
        
        print(f"\n处理完成: {success_count}/{total_count} 文件成功")
        for r in results:
            if r.get("success"):
                garbled = r.get("garbled_blocks") or r.get("garbled_elements", 0)
                print(f"  ✓ {r.get('output_path')} (乱码: {garbled})")
            else:
                print(f"  ✗ {r.get('error', 'Unknown error')}")
        return
    
    # 单文件处理模式
    if args.input:
        print(f"处理文件: {args.input}")
        
        result = fixer.fix_file(args.input, args.output or "", args.repair_level)
        
        if result.get("success"):
            print(f"✓ 分析完成")
            print(f"  文件类型: {result.get('file_type')}")
            
            if result.get('file_type') == 'pdf':
                print(f"  页数: {result.get('pages')}")
                print(f"  文本块: {result.get('total_blocks')}")
                print(f"  乱码块: {result.get('garbled_blocks')}")
            else:
                print(f"  文本元素: {result.get('total_elements')}")
                print(f"  乱码元素: {result.get('garbled_elements')}")
            
            # 显示乱码文本详情
            blocks = result.get('text_blocks') or result.get('text_elements', [])
            garbled_blocks = [b for b in blocks if b.get('is_garbled')]
            
            if garbled_blocks:
                print(f"\n检测到的乱码文本:")
                for i, block in enumerate(garbled_blocks[:5], 1):
                    orig = block.get('original_text', '')[:50]
                    sugg = block.get('suggested_fix', '')[:50]
                    print(f"  {i}. ID: {block.get('id')}")
                    print(f"     原文: {orig}")
                    print(f"     建议: {sugg}")
                    print(f"     置信度: {block.get('confidence', 0):.2f}")
                
                if len(garbled_blocks) > 5:
                    print(f"  ... 还有 {len(garbled_blocks) - 5} 个乱码文本")
            
            if args.output:
                print(f"\n输出路径: {args.output}")
                print("提示: 使用 --export-json 导出可编辑格式进行手动修复")
        else:
            print(f"✗ 处理失败: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
