#!/usr/bin/env python3
"""
Forest Plot Styler - 美化 Meta 分析森林图
ID: 157
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Forest Plot Styler - 美化 Meta 分析森林图',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py -i data.csv
  python main.py -i data.csv --point-color="#E63946" --ci-linewidth=3
  python main.py -i data.xlsx --subgroup group_col -f pdf -o output.pdf
        """
    )
    
    parser.add_argument('-i', '--input', required=True, help='输入数据文件 (CSV 或 Excel)')
    parser.add_argument('-o', '--output', default='forest_plot.png', help='输出文件路径 (默认: forest_plot.png)')
    parser.add_argument('-f', '--format', choices=['png', 'pdf', 'svg'], default='png', help='输出格式')
    parser.add_argument('--point-size', type=float, default=8, help='OR 点大小 (默认: 8)')
    parser.add_argument('--point-color', default='#2E86AB', help='OR 点颜色 (默认: #2E86AB)')
    parser.add_argument('--ci-color', default='#2E86AB', help='置信区间线条颜色 (默认: #2E86AB)')
    parser.add_argument('--ci-linewidth', type=float, default=2, help='置信区间线条粗细 (默认: 2)')
    parser.add_argument('--ci-capwidth', type=float, default=5, help='置信区间端点宽度 (默认: 5)')
    parser.add_argument('--summary-color', default='#A23B72', help='汇总效应点颜色 (默认: #A23B72)')
    parser.add_argument('--summary-shape', default='diamond', choices=['diamond', 'square', 'circle'], 
                        help='汇总效应点形状 (默认: diamond)')
    parser.add_argument('--subgroup', help='亚组分析列名')
    parser.add_argument('-t', '--title', default='Forest Plot', help='图表标题')
    parser.add_argument('-x', '--xlabel', default='Odds Ratio (95% CI)', help='X 轴标签')
    parser.add_argument('--reference-line', type=float, default=1, help='参考线位置 (默认: 1)')
    parser.add_argument('-W', '--width', type=float, default=12, help='图片宽度/英寸 (默认: 12)')
    parser.add_argument('-H', '--height', type=float, default=None, help='图片高度/英寸 (默认: 自动)')
    parser.add_argument('--dpi', type=int, default=300, help='图片分辨率 (默认: 300)')
    parser.add_argument('--font-size', type=float, default=10, help='字体大小 (默认: 10)')
    parser.add_argument('-s', '--style', choices=['default', 'minimal', 'dark'], default='default', 
                        help='预设样式 (默认: default)')
    
    return parser.parse_args()


def load_data(filepath):
    """加载输入数据"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"找不到文件: {filepath}")
    
    suffix = path.suffix.lower()
    if suffix == '.csv':
        return pd.read_csv(filepath)
    elif suffix in ['.xlsx', '.xls']:
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"不支持的文件格式: {suffix}")


def validate_data(df):
    """验证数据格式"""
    required_cols = ['study', 'or', 'ci_lower', 'ci_upper']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"缺少必要列: {missing}")
    
    # 检查数值列
    numeric_cols = ['or', 'ci_lower', 'ci_upper']
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"列 '{col}' 必须是数值类型")
    
    return True


def apply_style(style_name):
    """应用预设样式"""
    styles = {
        'default': {
            'bg_color': 'white',
            'text_color': 'black',
            'grid_color': '#E0E0E0',
            'grid_alpha': 0.5,
            'spine_color': 'black'
        },
        'minimal': {
            'bg_color': 'white',
            'text_color': '#333333',
            'grid_color': '#F0F0F0',
            'grid_alpha': 0.3,
            'spine_color': '#CCCCCC'
        },
        'dark': {
            'bg_color': '#1E1E1E',
            'text_color': '#E0E0E0',
            'grid_color': '#404040',
            'grid_alpha': 0.3,
            'spine_color': '#666666'
        }
    }
    return styles.get(style_name, styles['default'])


def calculate_summary_effect(df):
    """计算汇总效应值（逆方差加权）"""
    # 使用对数尺度计算
    log_or = np.log(df['or'])
    
    # 估计标准误（基于置信区间）
    se = (np.log(df['ci_upper']) - np.log(df['ci_lower'])) / (2 * 1.96)
    
    # 逆方差权重
    weights = 1 / (se ** 2)
    
    # 加权平均
    pooled_log_or = np.sum(weights * log_or) / np.sum(weights)
    pooled_se = np.sqrt(1 / np.sum(weights))
    
    # 转换回 OR 尺度
    pooled_or = np.exp(pooled_log_or)
    ci_lower = np.exp(pooled_log_or - 1.96 * pooled_se)
    ci_upper = np.exp(pooled_log_or + 1.96 * pooled_se)
    
    return pooled_or, ci_lower, ci_upper


def draw_diamond(ax, x, y, width, height, color):
    """绘制菱形标记"""
    diamond = plt.Polygon([
        (x, y + height/2),
        (x + width/2, y),
        (x, y - height/2),
        (x - width/2, y)
    ], facecolor=color, edgecolor=color, zorder=5)
    ax.add_patch(diamond)


def create_forest_plot(df, args):
    """创建森林图"""
    style = apply_style(args.style)
    
    # 自动计算高度
    n_studies = len(df)
    if args.height is None:
        height = max(6, n_studies * 0.5 + 3)
    else:
        height = args.height
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(args.width, height))
    fig.patch.set_facecolor(style['bg_color'])
    ax.set_facecolor(style['bg_color'])
    
    # 设置文字颜色
    ax.tick_params(colors=style['text_color'])
    ax.xaxis.label.set_color(style['text_color'])
    ax.yaxis.label.set_color(style['text_color'])
    ax.title.set_color(style['text_color'])
    
    # 准备数据
    y_positions = np.arange(n_studies, 0, -1)
    or_values = df['or'].values
    ci_lower = df['ci_lower'].values
    ci_upper = df['ci_upper'].values
    
    # 使用权重调整点大小
    if 'weight' in df.columns:
        weights = df['weight'].values
        point_sizes = args.point_size * (weights / weights.max()) * 2
    else:
        point_sizes = [args.point_size] * n_studies
    
    # 绘制置信区间
    for i, (y, or_val, ci_l, ci_u) in enumerate(zip(y_positions, or_values, ci_lower, ci_upper)):
        # 绘制横线
        ax.plot([ci_l, ci_u], [y, y], color=args.ci_color, linewidth=args.ci_linewidth, zorder=2)
        # 绘制端点
        ax.plot([ci_l, ci_l], [y - args.ci_capwidth/100, y + args.ci_capwidth/100], 
                color=args.ci_color, linewidth=args.ci_linewidth, zorder=2)
        ax.plot([ci_u, ci_u], [y - args.ci_capwidth/100, y + args.ci_capwidth/100], 
                color=args.ci_color, linewidth=args.ci_linewidth, zorder=2)
    
    # 绘制 OR 点
    ax.scatter(or_values, y_positions, s=point_sizes, color=args.point_color, 
               zorder=3, edgecolor='white', linewidth=1)
    
    # 亚组分析
    subgroup_offsets = 0
    if args.subgroup and args.subgroup in df.columns:
        subgroups = df[args.subgroup].unique()
        for subgroup in subgroups:
            mask = df[args.subgroup] == subgroup
            subgroup_df = df[mask]
            if len(subgroup_df) > 0:
                pooled_or, pooled_ci_l, pooled_ci_u = calculate_summary_effect(subgroup_df)
                y_pos = y_positions[mask].min() - 0.5
                # 绘制亚组汇总
                ax.plot([pooled_ci_l, pooled_ci_u], [y_pos, y_pos], 
                        color=args.summary_color, linewidth=args.ci_linewidth + 1, zorder=4)
                if args.summary_shape == 'diamond':
                    draw_diamond(ax, pooled_or, y_pos, (pooled_ci_u - pooled_ci_l) * 0.15, 0.3, args.summary_color)
                elif args.summary_shape == 'square':
                    ax.scatter(pooled_or, y_pos, s=args.point_size * 3, marker='s', 
                               color=args.summary_color, zorder=4)
                else:
                    ax.scatter(pooled_or, y_pos, s=args.point_size * 3, marker='o', 
                               color=args.summary_color, zorder=4)
        subgroup_offsets = len(subgroups) * 0.5
    
    # 总体汇总效应
    pooled_or, pooled_ci_l, pooled_ci_u = calculate_summary_effect(df)
    summary_y = 0.5 - subgroup_offsets
    
    ax.plot([pooled_ci_l, pooled_ci_u], [summary_y, summary_y], 
            color=args.summary_color, linewidth=args.ci_linewidth + 2, zorder=4)
    
    if args.summary_shape == 'diamond':
        draw_diamond(ax, pooled_or, summary_y, (pooled_ci_u - pooled_ci_l) * 0.15, 0.3, args.summary_color)
    elif args.summary_shape == 'square':
        ax.scatter(pooled_or, summary_y, s=args.point_size * 4, marker='s', 
                   color=args.summary_color, zorder=4)
    else:
        ax.scatter(pooled_or, summary_y, s=args.point_size * 4, marker='o', 
                   color=args.summary_color, zorder=4)
    
    # 参考线
    ax.axvline(x=args.reference_line, color='#E63946', linestyle='--', linewidth=1.5, zorder=1, alpha=0.7)
    
    # 设置标签
    study_labels = df['study'].tolist()
    if args.subgroup and args.subgroup in df.columns:
        study_labels.append('Overall')
    else:
        study_labels.append('Overall')
    
    all_y_positions = list(y_positions) + [summary_y]
    
    ax.set_yticks(all_y_positions)
    ax.set_yticklabels(study_labels, fontsize=args.font_size)
    ax.set_xlabel(args.xlabel, fontsize=args.font_size + 1, color=style['text_color'])
    ax.set_title(args.title, fontsize=args.font_size + 3, fontweight='bold', pad=15, color=style['text_color'])
    
    # 设置边框
    for spine in ax.spines.values():
        spine.set_color(style['spine_color'])
    
    # 网格线
    ax.grid(True, axis='x', alpha=style['grid_alpha'], color=style['grid_color'], linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # 添加数值标签列
    # 右侧添加 OR (95% CI) 列
    or_labels = [f"{or_val:.2f} [{ci_l:.2f}-{ci_u:.2f}]" for or_val, ci_l, ci_u in zip(or_values, ci_lower, ci_upper)]
    or_labels.append(f"{pooled_or:.2f} [{pooled_ci_l:.2f}-{pooled_ci_u:.2f}]")
    
    # 在右侧添加文本
    for y, label in zip(all_y_positions, or_labels):
        ax.text(ax.get_xlim()[1] * 1.02, y, label, va='center', ha='left', 
                fontsize=args.font_size - 1, color=style['text_color'])
    
    # 调整布局
    plt.tight_layout()
    
    return fig, ax


def main():
    """主函数"""
    try:
        args = parse_args()
        
        # 加载数据
        print(f"正在加载数据: {args.input}")
        df = load_data(args.input)
        
        # 验证数据
        validate_data(df)
        print(f"成功加载 {len(df)} 个研究")
        
        # 创建森林图
        print("正在生成森林图...")
        fig, ax = create_forest_plot(df, args)
        
        # 保存
        output_path = args.output
        if not output_path.endswith(f".{args.format}"):
            output_path = f"{output_path}.{args.format}"
        
        fig.savefig(output_path, format=args.format, dpi=args.dpi, 
                    bbox_inches='tight', facecolor=fig.get_facecolor())
        print(f"森林图已保存: {output_path}")
        
        plt.close(fig)
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
