#!/usr/bin/env python3
"""
Metagenomic Krona Chart Generator
生成宏基因组数据的交互式Krona旭日图

Author: OpenClaw
Skill ID: 169
"""

import argparse
import sys
import re
from pathlib import Path
from collections import defaultdict

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
except ImportError as e:
    print(f"Error: 缺少必要的依赖 - {e}")
    print("请运行: pip install plotly pandas")
    sys.exit(1)


class TaxonomyNode:
    """分类树节点"""
    def __init__(self, name, rank, tax_id, parent_id=None, reads=0, percent=0):
        self.name = name
        self.rank = rank
        self.tax_id = tax_id
        self.parent_id = parent_id
        self.reads = reads
        self.percent = percent
        self.children = []
        self.path = []  # 从根到当前节点的路径
    
    def add_child(self, child):
        self.children.append(child)
    
    def get_full_path(self):
        """获取完整路径字符串"""
        return " | ".join(self.path + [self.name])


def parse_kraken2_report(filepath):
    """
    解析Kraken2/Bracken报告格式
    格式: percent  reads  direct_reads  rank  tax_id  name
    """
    nodes = {}
    root = None
    stack = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.rstrip('\n\r')
            if not line:
                continue
            
            # 解析行 - 处理可能的前导空格
            parts = line.split('\t')
            if len(parts) < 6:
                # 尝试空格分隔
                parts = line.split()
                if len(parts) < 6:
                    continue
            
            try:
                percent = float(parts[0])
                reads = int(parts[1])
                # parts[2] = direct reads (unused)
                rank = parts[3]
                tax_id = parts[4]
                name = parts[5].strip()
            except (ValueError, IndexError):
                continue
            
            # 计算缩进深度（前导空格数）
            leading_spaces = len(line) - len(line.lstrip())
            depth = leading_spaces // 2
            
            node = TaxonomyNode(
                name=name,
                rank=rank,
                tax_id=tax_id,
                reads=reads,
                percent=percent
            )
            nodes[tax_id] = node
            
            # 确定父节点
            if rank == 'R' or name == 'root':
                root = node
                node.path = [name]
                stack = [node]
            else:
                # 根据深度确定父节点
                while len(stack) > depth:
                    stack.pop()
                
                if stack:
                    parent = stack[-1]
                    node.parent_id = parent.tax_id
                    parent.add_child(node)
                    node.path = parent.path + [name]
                    stack.append(node)
                else:
                    # 没有root的情况
                    if root is None:
                        root = TaxonomyNode(name="root", rank="R", tax_id="1")
                        nodes["1"] = root
                    node.parent_id = root.tax_id
                    root.add_child(node)
                    node.path = [root.name, name]
                    stack = [root, node]
    
    return root, nodes


def parse_custom_tsv(filepath):
    """
    解析自定义TSV格式
    列: taxon_id, name, rank, parent_id, reads, percent
    """
    df = pd.read_csv(filepath, sep='\t')
    
    nodes = {}
    root = None
    
    # 首先创建所有节点
    for _, row in df.iterrows():
        tax_id = str(row.get('taxon_id', row.get('tax_id', '')))
        name = row.get('name', '')
        rank = row.get('rank', '')
        parent_id = str(row.get('parent_id', row.get('parent', '')))
        reads = int(row.get('reads', 0))
        percent = float(row.get('percent', 0))
        
        node = TaxonomyNode(
            name=name,
            rank=rank,
            tax_id=tax_id,
            parent_id=parent_id if parent_id and parent_id != 'nan' else None,
            reads=reads,
            percent=percent
        )
        nodes[tax_id] = node
        
        if rank in ['R', 'root', 'no rank'] or parent_id is None:
            root = node
    
    # 建立父子关系
    for tax_id, node in nodes.items():
        if node.parent_id and node.parent_id in nodes:
            parent = nodes[node.parent_id]
            parent.add_child(node)
    
    # 计算路径
    def calc_path(node, current_path):
        node.path = current_path + [node.name]
        for child in node.children:
            calc_path(child, node.path)
    
    if root:
        calc_path(root, [])
    
    return root, nodes


def auto_detect_format(filepath):
    """自动检测输入文件格式"""
    with open(filepath, 'r') as f:
        first_line = f.readline().strip()
    
    # 检查是否为TSV且包含列名
    if '\t' in first_line:
        parts = first_line.split('\t')
        # 如果第一行是列名
        if any(col in first_line.lower() for col in ['taxon_id', 'name', 'rank']):
            return 'custom'
    
    # Kraken2格式: 以百分比开头
    try:
        float(first_line.split()[0])
        return 'kraken2'
    except (ValueError, IndexError):
        pass
    
    return 'kraken2'  # 默认


def flatten_tree(node, data, min_percent=0, max_depth=7, current_depth=0):
    """
    将树结构扁平化为旭日图所需的数据格式
    """
    if current_depth > max_depth:
        return
    
    if node.percent < min_percent:
        return
    
    # 跳过unclassified或root的重复计数
    if node.name.lower() in ['unclassified', 'unclass'] and node.rank == 'U':
        return
    
    path_str = " | ".join(node.path) if node.path else node.name
    
    data.append({
        'name': node.name,
        'path': path_str,
        'reads': node.reads,
        'percent': node.percent,
        'rank': node.rank,
        'depth': current_depth
    })
    
    # 递归处理子节点
    for child in sorted(node.children, key=lambda x: x.percent, reverse=True):
        flatten_tree(child, data, min_percent, max_depth, current_depth + 1)


def get_rank_color(rank):
    """根据分类等级获取颜色"""
    color_map = {
        'R': '#2c3e50',      # root - 深蓝灰
        'D': '#e74c3c',      # domain - 红
        'K': '#e74c3c',      # kingdom - 红
        'P': '#3498db',      # phylum - 蓝
        'C': '#2ecc71',      # class - 绿
        'O': '#f39c12',      # order - 橙
        'F': '#9b59b6',      # family - 紫
        'G': '#1abc9c',      # genus - 青
        'S': '#e91e63',      # species - 粉红
    }
    return color_map.get(rank, '#95a5a6')  # 默认灰色


def create_krona_chart(root, output_path, title="Metagenomic Krona Chart", 
                        min_percent=0.01, max_depth=7):
    """
    创建Krona旭日图
    """
    # 扁平化数据
    data = []
    flatten_tree(root, data, min_percent, max_depth)
    
    if not data:
        print("Warning: 没有数据可以绘制")
        return False
    
    df = pd.DataFrame(data)
    
    # 构建旭日图数据
    # 使用sunburst需要id/parent格式
    ids = []
    labels = []
    parents = []
    values = []
    hover_texts = []
    colors = []
    
    # 创建唯一ID映射
    id_map = {}
    
    for idx, row in df.iterrows():
        path_parts = row['path'].split(' | ')
        
        # 创建唯一ID
        node_id = f"{row['path']}_{idx}"
        id_map[row['path']] = node_id
        
        # 确定父节点
        if len(path_parts) > 1:
            parent_path = ' | '.join(path_parts[:-1])
            parent_id = id_map.get(parent_path, '')
        else:
            parent_id = ''
        
        ids.append(node_id)
        labels.append(row['name'])
        parents.append(parent_id)
        values.append(row['reads'])
        
        # 悬停信息
        hover_text = f"<b>{row['name']}</b><br>" \
                     f"Rank: {row['rank']}<br>" \
                     f"Reads: {row['reads']:,}<br>" \
                     f"Percent: {row['percent']:.2f}%"
        hover_texts.append(hover_text)
        
        # 颜色
        colors.append(get_rank_color(row['rank']))
    
    # 创建图表
    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        hovertext=hover_texts,
        hoverinfo='text',
        marker=dict(
            colors=colors,
            line=dict(width=1, color='white')
        ),
        textfont=dict(size=12),
        insidetextorientation='radial'
    ))
    
    # 布局设置
    total_reads = sum(df[df['depth'] == 0]['reads']) if len(df) > 0 else 0
    
    fig.update_layout(
        title=dict(
            text=f"{title}<br><sup>Total Reads: {total_reads:,}</sup>",
            x=0.5,
            font=dict(size=20)
        ),
        margin=dict(t=80, l=20, r=20, b=20),
        sunburstcolorway=[
            '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
            '#9b59b6', '#1abc9c', '#e91e63', '#34495e'
        ],
        paper_bgcolor='white',
        width=900,
        height=800
    )
    
    # 添加图例说明
    rank_legend = [
        ("Domain (D)", "#e74c3c"),
        ("Phylum (P)", "#3498db"),
        ("Class (C)", "#2ecc71"),
        ("Order (O)", "#f39c12"),
        ("Family (F)", "#9b59b6"),
        ("Genus (G)", "#1abc9c"),
        ("Species (S)", "#e91e63")
    ]
    
    for i, (label, color) in enumerate(rank_legend):
        fig.add_annotation(
            x=1.15,
            y=1 - i * 0.08,
            xref='paper',
            yref='paper',
            text=f"◆ {label}",
            showarrow=False,
            font=dict(size=11, color=color),
            align='left'
        )
    
    # 调整布局以适应图例
    fig.update_layout(
        margin=dict(t=80, l=20, r=150, b=20),
        annotations=list(fig.layout.annotations) if fig.layout.annotations else []
    )
    
    # 保存HTML
    fig.write_html(output_path, include_plotlyjs='cdn')
    print(f"Krona chart saved to: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Generate interactive Krona chart for metagenomic data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i kraken2_report.txt -o krona.html
  %(prog)s -i bracken_output.tsv -t bracken --min-percent 0.1
  %(prog)s -i custom_data.tsv -t custom --title "My Sample"
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                        help='Input file path (Kraken2/Bracken report or custom TSV)')
    parser.add_argument('-o', '--output', default='krona_chart.html',
                        help='Output HTML file path (default: krona_chart.html)')
    parser.add_argument('-t', '--type', choices=['kraken2', 'bracken', 'custom', 'auto'],
                        default='auto', help='Input format type (default: auto)')
    parser.add_argument('--max-depth', type=int, default=7,
                        help='Maximum depth to display (default: 7)')
    parser.add_argument('--min-percent', type=float, default=0.01,
                        help='Minimum percentage threshold (default: 0.01)')
    parser.add_argument('--title', default='Metagenomic Krona Chart',
                        help='Chart title')
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 自动检测格式
    file_type = args.type
    if file_type == 'auto':
        file_type = auto_detect_format(args.input)
        print(f"Detected format: {file_type}")
    
    # 解析输入文件
    print(f"Parsing {file_type} format...")
    try:
        if file_type in ['kraken2', 'bracken']:
            root, nodes = parse_kraken2_report(args.input)
        else:
            root, nodes = parse_custom_tsv(args.input)
    except Exception as e:
        print(f"Error parsing input: {e}")
        sys.exit(1)
    
    if root is None:
        print("Error: 无法解析数据，请检查输入文件格式")
        sys.exit(1)
    
    print(f"Loaded {len(nodes)} taxonomy nodes")
    print(f"Root: {root.name} ({root.reads:,} reads, {root.percent:.2f}%)")
    
    # 生成图表
    print("Generating Krona chart...")
    success = create_krona_chart(
        root=root,
        output_path=args.output,
        title=args.title,
        min_percent=args.min_percent,
        max_depth=args.max_depth
    )
    
    if success:
        print("Done!")
    else:
        print("Failed to generate chart")
        sys.exit(1)


if __name__ == '__main__':
    main()
