#!/usr/bin/env python3
"""
Authorship CRediT Generator
根据CRediT标准生成规范的作者贡献声明

ID: 160
"""

import argparse
import json
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


# CRediT 14角色标准定义
CREDIT_ROLES = {
    "C1": {
        "en": "Conceptualization",
        "zh": "概念化",
        "desc": "提出思路、构思研究目标"
    },
    "C2": {
        "en": "Data curation",
        "zh": "数据整理",
        "desc": "管理数据、注释、清洗、维护"
    },
    "C3": {
        "en": "Formal analysis",
        "zh": "形式分析",
        "desc": "应用统计、数学或计算技术"
    },
    "C4": {
        "en": "Funding acquisition",
        "zh": "资金获取",
        "desc": "获得研究资金支持"
    },
    "C5": {
        "en": "Investigation",
        "zh": "调查研究",
        "desc": "执行实验、收集数据"
    },
    "C6": {
        "en": "Methodology",
        "zh": "方法论",
        "desc": "开发或设计方法/流程"
    },
    "C7": {
        "en": "Project administration",
        "zh": "项目管理",
        "desc": "协调项目计划执行"
    },
    "C8": {
        "en": "Resources",
        "zh": "资源提供",
        "desc": "提供研究材料、试剂、样本等"
    },
    "C9": {
        "en": "Software",
        "zh": "软件",
        "desc": "编程、软件开发"
    },
    "C10": {
        "en": "Supervision",
        "zh": "监督指导",
        "desc": "指导研究活动、导师职责"
    },
    "C11": {
        "en": "Validation",
        "zh": "验证",
        "desc": "验证结果、复制实验"
    },
    "C12": {
        "en": "Visualization",
        "zh": "可视化",
        "desc": "准备图表、数据展示"
    },
    "C13": {
        "en": "Writing – original draft",
        "zh": "写作-原稿",
        "desc": "撰写初稿"
    },
    "C14": {
        "en": "Writing – review & editing",
        "zh": "写作-审阅与编辑",
        "desc": "关键性审阅与修改"
    }
}


@dataclass
class Author:
    """作者信息类"""
    name: str
    roles: List[str]
    affiliation: str = ""
    
    def validate_roles(self) -> List[str]:
        """验证角色代码是否有效"""
        invalid = [r for r in self.roles if r not in CREDIT_ROLES]
        return invalid
    
    def get_role_names(self, lang: str = "zh") -> List[str]:
        """获取角色名称列表"""
        return [CREDIT_ROLES[r][lang] for r in self.roles if r in CREDIT_ROLES]


@dataclass
class Contribution:
    """贡献声明类"""
    authors: List[Author]
    equal_contribution: List[str] = None
    corresponding: List[str] = None
    language: str = "zh"
    
    def __post_init__(self):
        if self.equal_contribution is None:
            self.equal_contribution = []
        if self.corresponding is None:
            self.corresponding = []


class CRediTGenerator:
    """CRediT贡献声明生成器"""
    
    def __init__(self, contribution: Contribution):
        self.contribution = contribution
        self._validate()
    
    def _validate(self):
        """验证输入数据"""
        for author in self.contribution.authors:
            invalid = author.validate_roles()
            if invalid:
                raise ValueError(f"作者 '{author.name}' 包含无效角色代码: {', '.join(invalid)}")
    
    def generate_text(self) -> str:
        """生成文本格式的贡献声明"""
        lines = []
        lang = self.contribution.language
        
        # 标题
        if lang == "zh":
            lines.append("作者贡献声明")
            lines.append("=" * 20)
        else:
            lines.append("Author Contributions")
            lines.append("=" * 20)
        
        lines.append("")
        
        # 作者贡献列表
        for author in self.contribution.authors:
            role_names = author.get_role_names(lang)
            if author.affiliation:
                if lang == "zh":
                    lines.append(f"{author.name}（{author.affiliation}）：{', '.join(role_names)}")
                else:
                    lines.append(f"{author.name} ({author.affiliation}): {', '.join(role_names)}")
            else:
                if lang == "zh":
                    lines.append(f"{author.name}：{', '.join(role_names)}")
                else:
                    lines.append(f"{author.name}: {', '.join(role_names)}")
        
        lines.append("")
        
        # 共同第一作者标注
        if self.contribution.equal_contribution:
            names = "、".join(self.contribution.equal_contribution) if lang == "zh" else ", ".join(self.contribution.equal_contribution)
            if lang == "zh":
                lines.append(f"*{names}对本文贡献相同")
            else:
                lines.append(f"*{names} contributed equally to this work")
            lines.append("")
        
        # 通讯作者标注
        if self.contribution.corresponding:
            names = "、".join(self.contribution.corresponding) if lang == "zh" else ", ".join(self.contribution.corresponding)
            if lang == "zh":
                lines.append(f"通讯作者: {names}")
            else:
                lines.append(f"Corresponding author(s): {names}")
        
        return "\n".join(lines)
    
    def generate_bilingual(self) -> str:
        """生成中英双语的贡献声明"""
        lines = []
        lines.append("作者贡献声明 / Author Contributions")
        lines.append("=" * 40)
        lines.append("")
        
        for author in self.contribution.authors:
            zh_roles = author.get_role_names("zh")
            en_roles = author.get_role_names("en")
            
            if author.affiliation:
                lines.append(f"{author.name}（{author.affiliation}）:")
            else:
                lines.append(f"{author.name}:")
            
            lines.append(f"  中文: {', '.join(zh_roles)}")
            lines.append(f"  EN:   {', '.join(en_roles)}")
            lines.append("")
        
        # 共同第一作者
        if self.contribution.equal_contribution:
            names = ", ".join(self.contribution.equal_contribution)
            lines.append(f"*共同第一作者 / Equal contribution: {names}")
            lines.append("")
        
        # 通讯作者
        if self.contribution.corresponding:
            names = ", ".join(self.contribution.corresponding)
            lines.append(f"通讯作者 / Corresponding: {names}")
        
        return "\n".join(lines)
    
    def generate_json(self) -> str:
        """生成JSON格式的贡献声明"""
        data = {
            "authors": [
                {
                    "name": a.name,
                    "affiliation": a.affiliation,
                    "roles": [
                        {
                            "code": r,
                            "name_zh": CREDIT_ROLES[r]["zh"],
                            "name_en": CREDIT_ROLES[r]["en"]
                        }
                        for r in a.roles
                    ]
                }
                for a in self.contribution.authors
            ],
            "equal_contribution": self.contribution.equal_contribution,
            "corresponding_authors": self.contribution.corresponding
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def generate_xml(self) -> str:
        """生成CRediT XML格式的贡献声明"""
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<contrib-group>')
        
        for author in self.contribution.authors:
            lines.append('  <contrib contrib-type="author">')
            lines.append(f'    <name>{author.name}</name>')
            if author.affiliation:
                lines.append(f'    <aff>{author.affiliation}</aff>')
            
            for role_code in author.roles:
                role = CREDIT_ROLES[role_code]
                lines.append(f'    <role vocab="credit" vocab-identifier="http://credit.niso.org/">')
                lines.append(f'      {role["en"]}')
                lines.append(f'    </role>')
            
            # 通讯作者标注
            if author.name in self.contribution.corresponding:
                lines.append('    <email>Corresponding Author</email>')
            
            # 共同第一作者标注
            if author.name in self.contribution.equal_contribution:
                lines.append('    <xref ref-type="equal"/>')
            
            lines.append('  </contrib>')
        
        lines.append('</contrib-group>')
        return "\n".join(lines)
    
    def generate(self, format_type: str = "text") -> str:
        """根据格式类型生成输出"""
        if format_type == "json":
            return self.generate_json()
        elif format_type == "xml":
            return self.generate_xml()
        elif format_type == "bilingual":
            return self.generate_bilingual()
        else:
            return self.generate_text()


def parse_short_format(text: str) -> List[Author]:
    """解析简写格式的作者信息"""
    # 格式: 姓名1:角色1,角色2,...|姓名2:角色3,角色4,...
    authors = []
    parts = text.split("|")
    
    for part in parts:
        if ":" not in part:
            continue
        name, roles_str = part.split(":", 1)
        roles = [r.strip() for r in roles_str.split(",")]
        authors.append(Author(name=name.strip(), roles=roles))
    
    return authors


def interactive_mode():
    """交互式模式"""
    print("=" * 50)
    print("CRediT 作者贡献声明生成器")
    print("=" * 50)
    print()
    
    # 显示角色列表
    print("CRediT 14角色标准:")
    print("-" * 30)
    for code, info in CREDIT_ROLES.items():
        print(f"  {code}: {info['zh']} ({info['en']})")
    print()
    
    # 输入作者数量
    num_authors = int(input("请输入作者数量: "))
    
    authors = []
    for i in range(num_authors):
        print(f"\n--- 作者 {i+1} ---")
        name = input("姓名: ")
        affiliation = input("机构 (可选): ")
        print("角色代码 (用逗号分隔, 如 C1,C5,C13):")
        roles_input = input("角色: ")
        roles = [r.strip() for r in roles_input.split(",")]
        
        authors.append(Author(name=name, roles=roles, affiliation=affiliation))
    
    # 共同第一作者
    print("\n--- 共同第一作者 ---")
    equal_input = input("共同第一作者姓名 (用逗号分隔, 无则留空): ")
    equal_contribution = [n.strip() for n in equal_input.split(",")] if equal_input else []
    
    # 通讯作者
    print("\n--- 通讯作者 ---")
    corres_input = input("通讯作者姓名 (用逗号分隔): ")
    corresponding = [n.strip() for n in corres_input.split(",")] if corres_input else []
    
    # 语言选择
    print("\n--- 输出格式 ---")
    print("1. 中文")
    print("2. English")
    print("3. 双语")
    lang_choice = input("选择 (1-3): ")
    
    language_map = {"1": "zh", "2": "en", "3": "bilingual"}
    language = language_map.get(lang_choice, "zh")
    
    # 格式选择
    print("\n--- 输出类型 ---")
    print("1. 文本")
    print("2. JSON")
    print("3. XML")
    format_choice = input("选择 (1-3): ")
    
    format_map = {"1": "text", "2": "json", "3": "xml"}
    format_type = format_map.get(format_choice, "text")
    
    # 生成输出
    contribution = Contribution(
        authors=authors,
        equal_contribution=equal_contribution,
        corresponding=corresponding,
        language="zh" if language == "bilingual" else language
    )
    
    generator = CRediTGenerator(contribution)
    
    if language == "bilingual":
        output = generator.generate_bilingual()
    else:
        output = generator.generate(format_type)
    
    print("\n" + "=" * 50)
    print("生成的贡献声明:")
    print("=" * 50)
    print(output)
    
    # 保存选项
    save = input("\n是否保存到文件? (y/n): ")
    if save.lower() == 'y':
        filename = input("文件名: ")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已保存到: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='CRediT 作者贡献声明生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --interactive
  %(prog)s --authors "张三:C1,C5,C13|李四:C2,C6,C9,C14"
  %(prog)s --input team.json --format json
        """
    )
    
    parser.add_argument('--authors', type=str, 
                       help='作者角色简写 (格式: 姓名1:角色1,角色2,...|姓名2:...)')
    parser.add_argument('--input', '-i', type=str,
                       help='输入JSON文件路径')
    parser.add_argument('--output', '-o', type=str,
                       help='输出文件路径 (默认输出到控制台)')
    parser.add_argument('--format', '-f', type=str, 
                       choices=['text', 'json', 'xml', 'bilingual'],
                       default='text',
                       help='输出格式 (默认: text)')
    parser.add_argument('--language', '-l', type=str,
                       choices=['zh', 'en'],
                       default='zh',
                       help='输出语言 (默认: zh)')
    parser.add_argument('--interactive', action='store_true',
                       help='交互式模式')
    parser.add_argument('--corresponding', type=str,
                       help='通讯作者姓名 (逗号分隔)')
    parser.add_argument('--equal', type=str,
                       help='共同第一作者姓名 (逗号分隔)')
    
    args = parser.parse_args()
    
    try:
        # 交互式模式
        if args.interactive:
            interactive_mode()
            return
        
        # 从文件读取
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            authors = [
                Author(
                    name=a['name'],
                    roles=a['roles'],
                    affiliation=a.get('affiliation', '')
                )
                for a in data.get('authors', [])
            ]
            
            contribution = Contribution(
                authors=authors,
                equal_contribution=data.get('equal_contribution', []),
                corresponding=data.get('corresponding', []),
                language=data.get('language', 'zh')
            )
        
        # 从命令行参数
        elif args.authors:
            authors = parse_short_format(args.authors)
            equal_contribution = [n.strip() for n in args.equal.split(",")] if args.equal else []
            corresponding = [n.strip() for n in args.corresponding.split(",")] if args.corresponding else []
            
            contribution = Contribution(
                authors=authors,
                equal_contribution=equal_contribution,
                corresponding=corresponding,
                language=args.language
            )
        
        else:
            parser.print_help()
            return
        
        # 生成输出
        generator = CRediTGenerator(contribution)
        output = generator.generate(args.format)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"已保存到: {args.output}")
        else:
            print(output)
    
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{args.input}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
