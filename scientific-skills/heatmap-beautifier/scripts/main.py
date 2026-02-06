#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heatmap Beautifier - Gene Expression Heatmap Visualization Tool

针对基因表达热图的专业美化工具，自动添加聚类树、颜色注释条，
并智能优化标签布局避免重叠。

Author: Bioinformatics Visualization Team
"""

import argparse
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.font_manager import FontProperties

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


class HeatmapBeautifier:
    """
    基因表达热图美化器
    
    功能：
    - 自动添加层次聚类树
    - 支持多组颜色注释条
    - 智能标签字号优化
    - 专业科研配色方案
    """
    
    # 内置配色方案
    COLOR_PALETTES = {
        "RdBu_r": "红蓝配色（经典差异表达）",
        "viridis": "黄紫配色（连续数据）",
        "RdYlBu_r": "红黄蓝配色",
        "coolwarm": "冷暖配色",
        "seismic": "地震图配色",
        "bwr": "蓝白红配色",
        "Spectral_r": "光谱配色",
        "BrBG_r": "棕绿配色"
    }
    
    # 默认注释颜色
    DEFAULT_COLORS = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#e91e63", "#795548", "#607d8b", "#ff5722"
    ]
    
    def __init__(self, style: str = "white"):
        """
        初始化 HeatmapBeautifier
        
        Args:
            style: seaborn 样式 ("white", "dark", "whitegrid", "darkgrid", "ticks")
        """
        sns.set_style(style)
        self.fig = None
        self.ax = None
        
    def load_data(self, data_path: str) -> pd.DataFrame:
        """
        加载表达矩阵数据
        
        Args:
            data_path: CSV 文件路径
            
        Returns:
            DataFrame: 表达矩阵 (基因 x 样本)
        """
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在: {data_path}")
            
        # 支持多种分隔符
        try:
            df = pd.read_csv(data_path, index_col=0)
        except:
            try:
                df = pd.read_csv(data_path, index_col=0, sep='\t')
            except:
                df = pd.read_csv(data_path, index_col=0, sep=';')
                
        # 确保数据为数值型
        df = df.apply(pd.to_numeric, errors='coerce')
        
        print(f"✓ 加载数据: {df.shape[0]} 基因 × {df.shape[1]} 样本")
        return df
    
    def calculate_optimal_fontsizes(self, 
                                     n_rows: int, 
                                     n_cols: int, 
                                     figsize: Tuple[int, int],
                                     max_row_fontsize: float = 10,
                                     max_col_fontsize: float = 10) -> Tuple[float, float]:
        """
        计算最优标签字号以避免重叠
        
        Args:
            n_rows: 行数
            n_cols: 列数
            figsize: 图形尺寸
            max_row_fontsize: 最大行标签字号
            max_col_fontsize: 最大列标签字号
            
        Returns:
            (row_fontsize, col_fontsize): 最优字号元组
        """
        # 基于图形尺寸和元素数量计算
        fig_width, fig_height = figsize
        
        # 估计可用空间（考虑聚类树和注释条占用的空间）
        available_width = fig_width * 0.6  # 主热图约占 60% 宽度
        available_height = fig_height * 0.6  # 主热图约占 60% 高度
        
        # 计算每个单元格的平均大小（英寸）
        cell_width = available_width / max(n_cols, 1)
        cell_height = available_height / max(n_rows, 1)
        
        # 转换为字号（近似转换：1英寸 ≈ 72点）
        points_per_inch = 72
        
        # 行标签：基于单元格高度计算
        row_fontsize = min(cell_height * points_per_inch * 0.8, max_row_fontsize)
        row_fontsize = max(row_fontsize, 4)  # 最小字号 4
        
        # 列标签：基于单元格宽度计算
        col_fontsize = min(cell_width * points_per_inch * 0.8, max_col_fontsize)
        col_fontsize = max(col_fontsize, 4)  # 最小字号 4
        
        # 大数据集时进一步限制
        if n_rows > 100:
            row_fontsize = min(row_fontsize, 6)
        if n_cols > 50:
            col_fontsize = min(col_fontsize, 6)
            
        return row_fontsize, col_fontsize
    
    def prepare_annotations(self,
                           data: pd.DataFrame,
                           annotations: Optional[Dict[str, Dict[str, str]]],
                           axis: str = "row") -> Optional[pd.DataFrame]:
        """
        准备注释数据
        
        Args:
            data: 主数据矩阵
            annotations: 注释字典 {注释名: {条目: 值}}
            axis: "row" 或 "col"
            
        Returns:
            注释 DataFrame 或 None
        """
        if annotations is None:
            return None
            
        indices = data.index if axis == "row" else data.columns
        annot_data = {}
        
        for annot_name, annot_dict in annotations.items():
            annot_values = [annot_dict.get(str(idx), "Unknown") for idx in indices]
            annot_data[annot_name] = annot_values
            
        return pd.DataFrame(annot_data, index=indices)
    
    def generate_annotation_colors(self,
                                   annotations: pd.DataFrame,
                                   custom_colors: Optional[Dict[str, Dict[str, str]]] = None
                                   ) -> Dict[str, Dict[str, str]]:
        """
        生成注释颜色映射
        
        Args:
            annotations: 注释 DataFrame
            custom_colors: 用户自定义颜色 {注释名: {类别: 颜色}}
            
        Returns:
            颜色映射字典
        """
        color_maps = {}
        
        for i, col in enumerate(annotations.columns):
            unique_vals = annotations[col].unique()
            
            # 使用自定义颜色或自动生成
            if custom_colors and col in custom_colors:
                color_maps[col] = custom_colors[col]
            else:
                colors = self.DEFAULT_COLORS[i % len(self.DEFAULT_COLORS):]
                colors = colors + self.DEFAULT_COLORS[:max(0, len(unique_vals) - len(colors))]
                color_maps[col] = {val: colors[j % len(colors)] 
                                   for j, val in enumerate(unique_vals)}
                
        return color_maps
    
    def create_heatmap(self,
                      data_path: str,
                      output_path: str,
                      title: str = "Gene Expression Heatmap",
                      cmap: str = "RdBu_r",
                      center: Optional[float] = 0,
                      vmin: Optional[float] = None,
                      vmax: Optional[float] = None,
                      row_cluster: bool = True,
                      col_cluster: bool = True,
                      standard_scale: Optional[str] = None,
                      z_score: Optional[int] = None,
                      row_annotations: Optional[Dict[str, Dict[str, str]]] = None,
                      col_annotations: Optional[Dict[str, Dict[str, str]]] = None,
                      annotation_colors: Optional[Dict[str, Dict[str, str]]] = None,
                      max_row_label_fontsize: float = 10,
                      max_col_label_fontsize: float = 10,
                      rotate_col_labels: float = 45,
                      rotate_row_labels: float = 0,
                      hide_row_labels: bool = False,
                      hide_col_labels: bool = False,
                      figsize: Optional[Tuple[int, int]] = None,
                      dpi: int = 300,
                      linewidths: float = 0.5,
                      linecolor: str = "white",
                      cbar_label: str = "Expression",
                      show_plot: bool = False) -> None:
        """
        创建美化热图
        
        Args:
            data_path: 输入数据文件路径
            output_path: 输出图片路径
            title: 图表标题
            cmap: 颜色映射名称
            center: 颜色中心值
            vmin: 最小值
            vmax: 最大值
            row_cluster: 是否进行行聚类
            col_cluster: 是否进行列聚类
            standard_scale: 标准化方式 ("row", "col", None)
            z_score: Z-score 标准化 (0=行, 1=列, None=不标准化)
            row_annotations: 行注释字典
            col_annotations: 列注释字典
            annotation_colors: 自定义注释颜色
            max_row_label_fontsize: 最大行标签字号
            max_col_label_fontsize: 最大列标签字号
            rotate_col_labels: 列标签旋转角度
            rotate_row_labels: 行标签旋转角度
            hide_row_labels: 是否隐藏行标签
            hide_col_labels: 是否隐藏列标签
            figsize: 图形尺寸 (宽, 高)
            dpi: 输出分辨率
            linewidths: 单元格边框宽度
            linecolor: 单元格边框颜色
            cbar_label: 颜色条标签
            show_plot: 是否显示图形（调试用）
        """
        # 加载数据
        data = self.load_data(data_path)
        n_rows, n_cols = data.shape
        
        # 自动确定图形尺寸
        if figsize is None:
            # 基于数据量计算合适的尺寸
            base_width = 10
            base_height = 8
            width_per_col = 0.3
            height_per_row = 0.15
            
            # 考虑注释条的空间
            annot_height = 1.5 if col_annotations else 0
            annot_width = 2.0 if row_annotations else 0
            
            fig_width = max(base_width, n_cols * width_per_col + annot_width + 4)
            fig_height = max(base_height, n_rows * height_per_row + annot_height + 3)
            
            # 限制最大尺寸
            fig_width = min(fig_width, 24)
            fig_height = min(fig_height, 20)
            
            figsize = (fig_width, fig_height)
        
        print(f"✓ 图形尺寸: {figsize[0]:.1f} × {figsize[1]:.1f} 英寸")
        
        # 计算最优字号
        row_fontsize, col_fontsize = self.calculate_optimal_fontsizes(
            n_rows, n_cols, figsize,
            max_row_label_fontsize, max_col_label_fontsize
        )
        print(f"✓ 字号: 行标签 {row_fontsize:.1f}pt, 列标签 {col_fontsize:.1f}pt")
        
        # 准备注释数据
        row_colors = None
        col_colors = None
        
        if row_annotations:
            row_annot_df = self.prepare_annotations(data, row_annotations, axis="row")
            row_color_map = self.generate_annotation_colors(row_annot_df, annotation_colors)
            row_colors = pd.DataFrame({k: v.map(row_color_map[k]) 
                                       for k, v in row_annot_df.items()})
            print(f"✓ 行注释: {list(row_annot_df.columns)}")
            
        if col_annotations:
            col_annot_df = self.prepare_annotations(data, col_annotations, axis="col")
            col_color_map = self.generate_annotation_colors(col_annot_df, annotation_colors)
            col_colors = pd.DataFrame({k: v.map(col_color_map[k]) 
                                       for k, v in col_annot_df.items()})
            print(f"✓ 列注释: {list(col_annot_df.columns)}")
        
        # 创建热图
        print("✓ 正在生成热图...")
        
        # 调整布局参数
        g = sns.clustermap(
            data,
            cmap=cmap,
            center=center,
            vmin=vmin,
            vmax=vmax,
            row_cluster=row_cluster,
            col_cluster=col_cluster,
            standard_scale=standard_scale,
            z_score=z_score,
            row_colors=row_colors,
            col_colors=col_colors,
            figsize=figsize,
            linewidths=linewidths,
            linecolor=linecolor,
            dendrogram_ratio=0.15,
            colors_ratio=0.03,
            cbar_pos=(0.02, 0.8, 0.03, 0.15),
            cbar_kws={"label": cbar_label},
            yticklabels=not hide_row_labels,
            xticklabels=not hide_col_labels
        )
        
        # 设置标签
        if not hide_row_labels and n_rows <= 200:
            g.ax_heatmap.set_yticklabels(
                g.ax_heatmap.get_ymajorticklabels(),
                fontsize=row_fontsize,
                rotation=rotate_row_labels
            )
        else:
            g.ax_heatmap.set_yticks([])
            
        if not hide_col_labels and n_cols <= 100:
            g.ax_heatmap.set_xticklabels(
                g.ax_heatmap.get_xmajorticklabels(),
                fontsize=col_fontsize,
                rotation=rotate_col_labels,
                ha='right'
            )
        else:
            g.ax_heatmap.set_xticks([])
        
        # 设置标题
        plt.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图形
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 支持多种格式
        supported_formats = ['pdf', 'png', 'svg', 'eps', 'tiff']
        file_format = output_path.suffix.lstrip('.').lower()
        if file_format not in supported_formats:
            file_format = 'pdf'
            output_path = output_path.with_suffix('.pdf')
        
        g.savefig(output_path, dpi=dpi, bbox_inches='tight', format=file_format)
        print(f"✓ 已保存: {output_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def quick_heatmap(self,
                     data_path: str,
                     output_path: str,
                     **kwargs) -> None:
        """
        快速生成热图（使用默认参数）
        
        Args:
            data_path: 输入数据路径
            output_path: 输出路径
            **kwargs: 可选参数覆盖
        """
        defaults = {
            'title': 'Gene Expression Heatmap',
            'cmap': 'RdBu_r',
            'center': 0,
            'row_cluster': True,
            'col_cluster': True,
            'dpi': 300
        }
        defaults.update(kwargs)
        
        self.create_heatmap(data_path, output_path, **defaults)


def load_annotations_from_json(path: str) -> Dict[str, Dict[str, str]]:
    """从 JSON 文件加载注释"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='Heatmap Beautifier - 基因表达热图美化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i expression.csv -o heatmap.pdf
  %(prog)s -i expression.csv -o heatmap.png --row-cluster --col-cluster
  %(prog)s -i expression.csv -o heatmap.pdf --row-annot row.json --col-annot col.json
        """
    )
    
    parser.add_argument('-i', '--input', required=True, 
                       help='输入表达矩阵 (CSV格式)')
    parser.add_argument('-o', '--output', required=True,
                       help='输出图片路径')
    parser.add_argument('-t', '--title', default='Gene Expression Heatmap',
                       help='图表标题')
    parser.add_argument('--cmap', default='RdBu_r',
                       help='颜色映射 (默认: RdBu_r)')
    parser.add_argument('--center', type=float, default=0,
                       help='颜色中心值 (默认: 0)')
    parser.add_argument('--vmin', type=float,
                       help='最小值')
    parser.add_argument('--vmax', type=float,
                       help='最大值')
    parser.add_argument('--row-cluster', action='store_true',
                       help='启用行聚类')
    parser.add_argument('--col-cluster', action='store_true',
                       help='启用列聚类')
    parser.add_argument('--row-annot', 
                       help='行注释 JSON 文件路径')
    parser.add_argument('--col-annot',
                       help='列注释 JSON 文件路径')
    parser.add_argument('--z-score', type=int, choices=[0, 1],
                       help='Z-score 标准化 (0=行, 1=列)')
    parser.add_argument('--standard-scale', choices=['row', 'col'],
                       help='标准化方式 (row 或 col)')
    parser.add_argument('--figsize', nargs=2, type=float,
                       help='图形尺寸 (宽 高)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='输出分辨率 (默认: 300)')
    parser.add_argument('--hide-row-labels', action='store_true',
                       help='隐藏行标签')
    parser.add_argument('--hide-col-labels', action='store_true',
                       help='隐藏列标签')
    parser.add_argument('--rotate-col', type=float, default=45,
                       help='列标签旋转角度 (默认: 45)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    # 加载注释
    row_annotations = None
    col_annotations = None
    
    if args.row_annot:
        row_annotations = load_annotations_from_json(args.row_annot)
    if args.col_annot:
        col_annotations = load_annotations_from_json(args.col_annot)
    
    # 构建参数
    kwargs = {
        'title': args.title,
        'cmap': args.cmap,
        'center': args.center,
        'vmin': args.vmin,
        'vmax': args.vmax,
        'row_cluster': args.row_cluster,
        'col_cluster': args.col_cluster,
        'row_annotations': row_annotations,
        'col_annotations': col_annotations,
        'z_score': args.z_score,
        'standard_scale': args.standard_scale,
        'dpi': args.dpi,
        'hide_row_labels': args.hide_row_labels,
        'hide_col_labels': args.hide_col_labels,
        'rotate_col_labels': args.rotate_col
    }
    
    if args.figsize:
        kwargs['figsize'] = tuple(args.figsize)
    
    # 移除 None 值
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    # 执行
    hb = HeatmapBeautifier()
    hb.create_heatmap(args.input, args.output, **kwargs)
    print("✓ 完成!")


if __name__ == '__main__':
    main()
