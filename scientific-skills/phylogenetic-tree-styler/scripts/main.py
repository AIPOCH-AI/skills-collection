#!/usr/bin/env python3
"""
Phylogenetic Tree Styler
美化进化树，添加物种分类色块、Bootstrap值和时间轴
"""

import argparse
import sys
from pathlib import Path

try:
    from ete3 import Tree, TreeStyle, NodeStyle, TextFace, RectFace, CircleFace
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"错误: 缺少依赖包 - {e}")
    print("请安装依赖: pip install ete3 matplotlib numpy pandas")
    sys.exit(1)


# 预定义的颜色方案
TAXONOMY_COLORS = {
    'domain': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'],
    'phylum': ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d3', '#c7c7c7'],
    'class': ['#9edae5', '#dbdb8d', '#bcbd22', '#17becf', '#e6550d', '#fd8d3c', '#31a354', '#74c476'],
}


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Phylogenetic Tree Styler - 美化进化树可视化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i tree.nwk -o output.png
  %(prog)s -i tree.nwk --show-bootstrap --taxonomy-file taxo.csv
  %(prog)s -i tree.nwk --show-timeline --root-age 500
        """
    )
    
    parser.add_argument('-i', '--input', required=True, help='输入的Newick格式进化树文件')
    parser.add_argument('-o', '--output', default='tree_styled.png', help='输出图像文件路径')
    parser.add_argument('-f', '--format', choices=['png', 'pdf', 'svg'], default='png', help='输出格式')
    parser.add_argument('--width', type=int, default=1200, help='图像宽度(像素)')
    parser.add_argument('--height', type=int, default=800, help='图像高度(像素)')
    parser.add_argument('--show-bootstrap', action='store_true', help='显示Bootstrap值')
    parser.add_argument('--bootstrap-threshold', type=float, default=50, help='只显示高于此阈值的Bootstrap值')
    parser.add_argument('--taxonomy-file', help='物种分类信息文件(CSV格式)')
    parser.add_argument('--show-timeline', action='store_true', help='显示时间轴')
    parser.add_argument('--root-age', type=float, help='根节点年代(百万年前)')
    parser.add_argument('--branch-color', default='black', help='分支颜色')
    parser.add_argument('--leaf-color', default='black', help='叶节点标签颜色')
    parser.add_argument('--dpi', type=int, default=150, help='输出DPI')
    
    return parser.parse_args()


def load_tree(tree_file):
    """加载进化树文件"""
    try:
        tree = Tree(tree_file, format=1)
        return tree
    except Exception as e:
        print(f"错误: 无法解析进化树文件 - {e}")
        sys.exit(1)


def load_taxonomy(taxonomy_file):
    """加载分类信息文件"""
    if not taxonomy_file:
        return None
    
    try:
        df = pd.read_csv(taxonomy_file)
        required_cols = ['name']
        if not all(col in df.columns for col in required_cols):
            print(f"错误: 分类文件必须包含 'name' 列")
            return None
        
        # 创建物种到分类信息的映射
        taxonomy_map = {}
        for _, row in df.iterrows():
            taxonomy_map[row['name']] = row.to_dict()
        
        return taxonomy_map
    except Exception as e:
        print(f"警告: 无法加载分类文件 - {e}")
        return None


def assign_taxonomy_colors(taxonomy_map, level='domain'):
    """为分类等级分配颜色"""
    if not taxonomy_map:
        return {}
    
    # 收集所有唯一的分类值
    values = set()
    for taxo in taxonomy_map.values():
        if level in taxo and pd.notna(taxo[level]):
            values.add(taxo[level])
    
    values = sorted(list(values))
    colors = TAXONOMY_COLORS.get(level, TAXONOMY_COLORS['domain'])
    
    color_map = {}
    for i, value in enumerate(values):
        color_map[value] = colors[i % len(colors)]
    
    return color_map


def style_tree(tree, args, taxonomy_map=None):
    """设置树的样式"""
    # 创建树样式
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.mode = 'r'  # 放射状模式，可改为 'c' 为圆形模式
    ts.optimal_scale_level = 'full'
    ts.scale = 200
    
    # 如果有时间轴，调整布局
    if args.show_timeline:
        ts.mode = 'r'
        ts.show_scale = True
        ts.scale_length = 0.1
    
    # 为分类等级分配颜色
    domain_colors = {}
    phylum_colors = {}
    if taxonomy_map:
        domain_colors = assign_taxonomy_colors(taxonomy_map, 'domain')
        phylum_colors = assign_taxonomy_colors(taxonomy_map, 'phylum')
    
    # 为每个节点设置样式
    for node in tree.traverse():
        nstyle = NodeStyle()
        nstyle['size'] = 0
        nstyle['fgcolor'] = args.branch_color
        nstyle['hz_line_color'] = args.branch_color
        nstyle['vt_line_color'] = args.branch_color
        nstyle['hz_line_width'] = 2
        nstyle['vt_line_width'] = 2
        
        # 叶节点样式
        if node.is_leaf():
            nstyle['size'] = 8
            nstyle['fgcolor'] = args.leaf_color
            
            # 添加分类色块
            if taxonomy_map and node.name in taxonomy_map:
                taxo = taxonomy_map[node.name]
                
                # 添加domain色块
                if 'domain' in taxo and pd.notna(taxo['domain']):
                    domain = taxo['domain']
                    color = domain_colors.get(domain, '#999999')
                    domain_face = RectFace(15, 15, color, color)
                    domain_face.margin_right = 5
                    node.add_face(domain_face, column=0, position='aligned')
                    
                    # 添加domain标签
                    domain_text = TextFace(f" {domain}", fsize=10, fgcolor=color)
                    node.add_face(domain_text, column=1, position='aligned')
                
                # 添加phylum色块
                if 'phylum' in taxo and pd.notna(taxo['phylum']):
                    phylum = taxo['phylum']
                    color = phylum_colors.get(phylum, '#cccccc')
                    phylum_face = RectFace(15, 15, color, color)
                    phylum_face.margin_right = 5
                    node.add_face(phylum_face, column=2, position='aligned')
                    
                    # 添加phylum标签
                    phylum_text = TextFace(f" {phylum}", fsize=10, fgcolor='#666666')
                    node.add_face(phylum_text, column=3, position='aligned')
        
        # 内部节点 - 显示Bootstrap值
        else:
            # 尝试获取bootstrap值
            bootstrap = None
            
            # 从节点名称解析(常见格式: (A,B)95:0.1)
            if node.name and node.name.replace('.', '').replace('-', '').isdigit():
                try:
                    bootstrap = float(node.name)
                except:
                    pass
            
            # 从support属性获取
            if bootstrap is None and hasattr(node, 'support') and node.support is not None:
                try:
                    bootstrap = float(node.support)
                except:
                    pass
            
            # 显示Bootstrap值
            if args.show_bootstrap and bootstrap is not None and bootstrap >= args.bootstrap_threshold:
                # 根据bootstrap值设置颜色强度
                intensity = min(1.0, bootstrap / 100)
                if bootstrap >= 90:
                    color = '#2166ac'  # 深蓝色 - 高置信度
                elif bootstrap >= 70:
                    color = '#4393c3'  # 中蓝色
                else:
                    color = '#92c5de'  # 浅蓝色
                
                bootstrap_face = TextFace(f"{int(bootstrap)}", fsize=9, fgcolor=color, bold=True)
                node.add_face(bootstrap_face, column=0, position='branch-top')
                
                # 节点大小反映bootstrap值
                nstyle['size'] = 4 + (bootstrap / 100) * 6
                nstyle['fgcolor'] = color
        
        node.set_style(nstyle)
    
    return ts


def add_timeline(tree, ts, root_age):
    """添加时间轴"""
    if not root_age:
        return
    
    # 计算树的高度
    tree_height = tree.get_farthest_leaf()[1]
    
    # 添加时间刻度
    ts.show_scale = True
    ts.scale_length = tree_height / 5
    
    # 添加标题说明
    ts.title.add_face(TextFace(f"Time Scale: {root_age} Mya", fsize=12, bold=True), column=0)


def render_tree(tree, ts, output_file, args):
    """渲染树到图像文件"""
    try:
        # 设置图像大小
        tree.render(output_file, tree_style=ts, w=args.width, h=args.height, dpi=args.dpi)
        print(f"成功: 图像已保存到 {output_file}")
        return True
    except Exception as e:
        print(f"错误: 渲染失败 - {e}")
        return False


def main():
    args = parse_args()
    
    # 检查输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 加载进化树
    print(f"正在加载进化树: {args.input}")
    tree = load_tree(args.input)
    print(f"树信息: {len(tree)} 个叶节点")
    
    # 加载分类信息
    taxonomy_map = None
    if args.taxonomy_file:
        print(f"正在加载分类信息: {args.taxonomy_file}")
        taxonomy_map = load_taxonomy(args.taxonomy_file)
        if taxonomy_map:
            print(f"已加载 {len(taxonomy_map)} 个物种的分类信息")
    
    # 设置树样式
    print("正在设置样式...")
    ts = style_tree(tree, args, taxonomy_map)
    
    # 添加时间轴
    if args.show_timeline:
        print("正在添加时间轴...")
        add_timeline(tree, ts, args.root_age)
    
    # 设置输出路径
    output_path = Path(args.output)
    if output_path.suffix != f'.{args.format}':
        output_path = output_path.with_suffix(f'.{args.format}')
    
    # 渲染图像
    print(f"正在渲染图像...")
    if render_tree(tree, ts, str(output_path), args):
        print(f"完成! 输出文件: {output_path}")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
