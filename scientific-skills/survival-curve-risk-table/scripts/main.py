#!/usr/bin/env python3
"""
Survival Curve Risk Table Generator
在Kaplan-Meier生存曲线下方自动对齐并添加"Number at risk"表格
符合临床肿瘤学期刊标准（NEJM、Lancet、JCO等）

Author: OpenClaw
Version: 1.0.0
"""

import argparse
import sys
import warnings
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Union
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# 尝试导入可选依赖
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    warnings.warn("PIL not installed. Image combining features disabled.")

try:
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test
    HAS_LIFELINES = True
except ImportError:
    HAS_LIFELINES = False
    warnings.warn("lifelines not installed. Survival analysis features limited.")


class RiskTableGenerator:
    """
    生存曲线风险表生成器
    
    主要功能：
    1. 从生存数据计算各时间点风险人数
    2. 生成符合期刊标准的表格
    3. 与KM曲线组合生成出版级图像
    """
    
    # 预定义的期刊风格配置
    JOURNAL_STYLES = {
        "NEJM": {
            "font_family": "Helvetica",
            "font_size": 8,
            "table_height_ratio": 0.15,
            "show_grid": False,
            "separator_lines": True,
            "header_bold": True,
            "time_label": "mo",
        },
        "Lancet": {
            "font_family": "Times New Roman",
            "font_size": 9,
            "table_height_ratio": 0.18,
            "show_grid": True,
            "separator_lines": True,
            "header_bold": True,
            "time_label": "months",
        },
        "JCO": {
            "font_family": "Arial",
            "font_size": 8,
            "table_height_ratio": 0.16,
            "show_grid": False,
            "separator_lines": False,
            "header_bold": False,
            "time_label": "mo",
            "show_censored": True,
            "censor_symbol": "+",
        },
        "custom": {
            "font_family": "Arial",
            "font_size": 8,
            "table_height_ratio": 0.15,
            "show_grid": False,
            "separator_lines": True,
            "header_bold": True,
            "time_label": "mo",
        }
    }
    
    def __init__(
        self,
        style: str = "NEJM",
        time_points: Optional[List[float]] = None,
        figure_size: Tuple[float, float] = (8, 6),
        dpi: int = 300,
        custom_style: Optional[Dict] = None
    ):
        """
        初始化风险表生成器
        
        Args:
            style: 期刊风格 (NEJM, Lancet, JCO, custom)
            time_points: 自定义时间点列表
            figure_size: 图像尺寸 (宽, 高) 英寸
            dpi: 图像分辨率
            custom_style: 自定义风格配置（当style='custom'时使用）
        """
        self.style_name = style
        self.style = self.JOURNAL_STYLES.get(style, self.JOURNAL_STYLES["NEJM"]).copy()
        
        if custom_style and style == "custom":
            self.style.update(custom_style)
        
        self.time_points = time_points
        self.figure_size = figure_size
        self.dpi = dpi
        
        self.data = None
        self.time_col = None
        self.event_col = None
        self.group_col = None
        self.groups = None
        
    def load_data(
        self,
        df: pd.DataFrame,
        time_col: str,
        event_col: str,
        group_col: Optional[str] = None
    ) -> None:
        """
        加载生存数据
        
        Args:
            df: 生存数据DataFrame
            time_col: 时间列名
            event_col: 事件列名（1=事件, 0=删失）
            group_col: 分组列名（可选）
        """
        self.data = df.copy()
        self.time_col = time_col
        self.event_col = event_col
        self.group_col = group_col
        
        # 验证必需列
        required_cols = [time_col, event_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        if group_col and group_col not in df.columns:
            raise ValueError(f"Group column '{group_col}' not found in data")
        
        # 提取分组信息
        if group_col:
            self.groups = df[group_col].unique().tolist()
        else:
            self.groups = ["All"]
            self.data["__group__"] = "All"
            self.group_col = "__group__"
        
        # 数据类型检查
        if not pd.api.types.is_numeric_dtype(self.data[time_col]):
            raise ValueError(f"Time column '{time_col}' must be numeric")
        
        # 确保事件列为数值型
        self.data[event_col] = pd.to_numeric(self.data[event_col], errors='coerce')
        
        # 自动确定时间点（如果未指定）
        if self.time_points is None:
            self._auto_select_time_points()
    
    def load_data_from_file(
        self,
        file_path: str,
        time_col: str,
        event_col: str,
        group_col: Optional[str] = None
    ) -> None:
        """
        从文件加载生存数据
        
        支持格式：CSV, Excel, SAS, pickle
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.csv':
            df = pd.read_csv(file_path)
        elif suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif suffix == '.sas7bdat':
            df = pd.read_sas(file_path)
        elif suffix in ['.pkl', '.pickle']:
            df = pd.read_pickle(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        self.load_data(df, time_col, event_col, group_col)
    
    def _auto_select_time_points(self, n_points: int = 7) -> None:
        """
        自动选择时间点
        
        策略：使用等距时间点，覆盖数据的0到最大随访时间
        """
        if self.data is None:
            raise ValueError("No data loaded")
        
        max_time = self.data[self.time_col].max()
        
        # 生成等距时间点（包含0和最大值）
        self.time_points = np.linspace(0, max_time, n_points).tolist()
        self.time_points = [round(t, 1) for t in self.time_points]
    
    def calculate_number_at_risk(self) -> pd.DataFrame:
        """
        计算各时间点的风险人数
        
        Returns:
            DataFrame，列为时间点，行为分组，值为风险人数
        """
        if self.data is None:
            raise ValueError("No data loaded")
        
        results = []
        
        for group in self.groups:
            group_data = self.data[self.data[self.group_col] == group]
            n_total = len(group_data)
            
            row = {"Group": group}
            for t in self.time_points:
                # 风险人数 = 总人数 - 在t时刻前发生事件的人数 - 在t时刻前删失的人数
                events_before = len(group_data[
                    (group_data[self.time_col] <= t) & 
                    (group_data[self.event_col] == 1)
                ])
                censored_before = len(group_data[
                    (group_data[self.time_col] < t) & 
                    (group_data[self.event_col] == 0)
                ])
                
                n_at_risk = n_total - events_before - censored_before
                row[f"t_{t}"] = max(0, n_at_risk)
            
            results.append(row)
        
        return pd.DataFrame(results)
    
    def calculate_censored_counts(self) -> pd.DataFrame:
        """
        计算各时间区间的删失人数（用于JCO风格）
        """
        if self.data is None:
            raise ValueError("No data loaded")
        
        results = []
        
        for group in self.groups:
            group_data = self.data[self.data[self.group_col] == group]
            row = {"Group": group}
            
            for i, t in enumerate(self.time_points):
                if i == 0:
                    censored_in_interval = 0
                else:
                    t_prev = self.time_points[i - 1]
                    censored_in_interval = len(group_data[
                        (group_data[self.time_col] > t_prev) &
                        (group_data[self.time_col] <= t) &
                        (group_data[self.event_col] == 0)
                    ])
                row[f"t_{t}"] = censored_in_interval
            
            results.append(row)
        
        return pd.DataFrame(results)
    
    def generate_risk_table(
        self,
        output_path: str,
        show_censored: Optional[bool] = None,
        show_events: bool = False,
        title: Optional[str] = None
    ) -> None:
        """
        生成独立的风险表图像
        
        Args:
            output_path: 输出文件路径
            show_censored: 是否显示删失人数（默认从风格配置读取）
            show_events: 是否显示事件发生数
            title: 表格标题
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if show_censored is None:
            show_censored = self.style.get("show_censored", False)
        
        # 计算数据
        risk_df = self.calculate_number_at_risk()
        
        # 设置字体
        plt.rcParams['font.family'] = self.style.get("font_family", "Arial")
        
        # 创建图形
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        ax.axis('off')
        
        # 准备表格数据
        table_data = self._prepare_table_data(risk_df, show_censored)
        
        # 绘制表格
        self._draw_risk_table(ax, table_data, title)
        
        # 保存
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"Risk table saved to: {output_path}")
    
    def _prepare_table_data(
        self,
        risk_df: pd.DataFrame,
        show_censored: bool
    ) -> List[List[str]]:
        """
        准备表格数据
        """
        # 表头
        time_label = self.style.get("time_label", "mo")
        headers = ["Number at risk"]
        for t in self.time_points:
            if t == self.time_points[-1]:
                headers.append(f"{int(t)} ({time_label})")
            else:
                headers.append(str(int(t)))
        
        # 数据行
        rows = []
        for _, row in risk_df.iterrows():
            group_name = row["Group"]
            data_row = [group_name]
            for t in self.time_points:
                data_row.append(str(int(row[f"t_{t}"])))
            rows.append(data_row)
        
        # 如果需要显示删失人数（JCO风格）
        if show_censored:
            censored_df = self.calculate_censored_counts()
            for _, row in censored_df.iterrows():
                group_name = row["Group"]
                data_row = [f"  ({self.style.get('censor_symbol', '+')})"]
                for t in self.time_points:
                    count = int(row[f"t_{t}"])
                    data_row.append(str(count) if count > 0 else "")
                rows.append(data_row)
        
        return [headers] + rows
    
    def _draw_risk_table(
        self,
        ax,
        table_data: List[List[str]],
        title: Optional[str] = None
    ) -> None:
        """
        绘制风险表
        """
        font_size = self.style.get("font_size", 8)
        show_grid = self.style.get("show_grid", False)
        header_bold = self.style.get("header_bold", True)
        
        # 创建表格
        table = ax.table(
            cellText=table_data[1:],
            colLabels=table_data[0],
            loc='center',
            cellLoc='center'
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(font_size)
        table.scale(1, 2)
        
        # 设置样式
        for i, key in enumerate(table.get_celld().keys()):
            cell = table.get_celld()[key]
            row, col = key
            
            # 表头样式
            if row == 0:
                cell.set_text_props(fontweight='bold' if header_bold else 'normal')
                cell.set_facecolor('#f0f0f0')
                cell.set_edgecolor('black' if show_grid else 'none')
            else:
                # 数据行样式
                cell.set_edgecolor('black' if show_grid else 'none')
                
                # 第一列（分组名）左对齐
                if col == 0:
                    cell.set_text_props(ha='left')
                    cell._loc = 'left'
        
        # 添加标题
        if title:
            ax.set_title(title, fontsize=font_size + 2, fontweight='bold', pad=10)
    
    def generate_combined_plot(
        self,
        km_plot_path: Optional[str] = None,
        output_path: str = "combined_survival_plot.png",
        km_ax: Optional[matplotlib.axes.Axes] = None,
        show_km_plot: bool = True,
        km_title: Optional[str] = None
    ) -> None:
        """
        生成KM曲线和风险表的组合图
        
        Args:
            km_plot_path: 外部KM曲线图像路径（可选）
            output_path: 输出文件路径
            km_ax: 预先生成的KM曲线axes（可选）
            show_km_plot: 是否显示KM曲线
            km_title: KM曲线标题
        """
        if not HAS_LIFELINES and km_ax is None and km_plot_path is None:
            raise ImportError("lifelines is required for generating KM plots. "
                            "Install with: pip install lifelines")
        
        # 设置字体
        plt.rcParams['font.family'] = self.style.get("font_family", "Arial")
        
        # 创建图形布局
        fig_height = self.figure_size[1]
        table_height_ratio = self.style.get("table_height_ratio", 0.15)
        
        if show_km_plot:
            fig = plt.figure(figsize=(self.figure_size[0], fig_height), dpi=self.dpi)
            gs = GridSpec(2, 1, height_ratios=[1 - table_height_ratio, table_height_ratio],
                         hspace=0.05)
            
            # 上部：KM曲线
            ax_km = fig.add_subplot(gs[0])
            
            if km_plot_path and Path(km_plot_path).exists():
                # 使用外部图像
                img = plt.imread(km_plot_path)
                ax_km.imshow(img)
                ax_km.axis('off')
            elif km_ax is not None:
                # 使用提供的axes（复杂，暂不实现）
                pass
            else:
                # 自动生成KM曲线
                self._plot_km_curve(ax_km, km_title)
            
            # 下部：风险表
            ax_table = fig.add_subplot(gs[1])
            ax_table.axis('off')
            
            # 准备并绘制表格
            risk_df = self.calculate_number_at_risk()
            show_censored = self.style.get("show_censored", False)
            table_data = self._prepare_table_data(risk_df, show_censored)
            self._draw_risk_table(ax_table, table_data)
            
            # 对齐X轴
            if hasattr(self, '_km_xlim'):
                ax_table.set_xlim(self._km_xlim)
        else:
            # 仅生成风险表
            self.generate_risk_table(output_path)
            return
        
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"Combined plot saved to: {output_path}")
    
    def _plot_km_curve(
        self,
        ax: matplotlib.axes.Axes,
        title: Optional[str] = None
    ) -> None:
        """
        使用lifelines绘制KM曲线
        """
        if not HAS_LIFELINES:
            raise ImportError("lifelines is required for generating KM plots")
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.groups)))
        
        for i, group in enumerate(self.groups):
            group_data = self.data[self.data[self.group_col] == group]
            
            kmf = KaplanMeierFitter()
            kmf.fit(
                durations=group_data[self.time_col],
                event_observed=group_data[self.event_col],
                label=group
            )
            
            kmf.plot_survival_function(
                ax=ax,
                ci_show=False,
                color=colors[i],
                linewidth=2
            )
        
        ax.set_xlabel(f"Time ({self.style.get('time_label', 'months')})", fontsize=10)
        ax.set_ylabel("Survival Probability", fontsize=10)
        ax.set_ylim(0, 1.05)
        ax.legend(loc='lower left', frameon=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        if title:
            ax.set_title(title, fontsize=12, fontweight='bold')
        
        # 保存X轴范围用于对齐
        self._km_xlim = ax.get_xlim()
    
    def export_risk_table_data(self, output_path: str) -> None:
        """
        导出风险表数据为CSV
        """
        risk_df = self.calculate_number_at_risk()
        
        # 重命名列为更友好的名称
        time_label = self.style.get("time_label", "mo")
        col_map = {"Group": "Group"}
        for t in self.time_points:
            col_map[f"t_{t}"] = f"{int(t)} {time_label}"
        
        risk_df = risk_df.rename(columns=col_map)
        risk_df.to_csv(output_path, index=False)
        print(f"Risk table data exported to: {output_path}")


def create_sample_data(output_path: str, n_patients: int = 300, seed: int = 42) -> None:
    """
    创建示例生存数据用于测试
    """
    np.random.seed(seed)
    
    # 生成两组数据
    n_per_group = n_patients // 2
    
    # 实验组：更好的生存
    exp_times = np.random.exponential(scale=36, size=n_per_group)
    exp_events = np.random.binomial(1, 0.6, n_per_group)
    
    # 对照组
    ctrl_times = np.random.exponential(scale=24, size=n_per_group)
    ctrl_events = np.random.binomial(1, 0.7, n_per_group)
    
    # 组合数据
    df = pd.DataFrame({
        'time': np.concatenate([exp_times, ctrl_times]),
        'event': np.concatenate([exp_events, ctrl_events]),
        'treatment': ['Experimental'] * n_per_group + ['Control'] * n_per_group
    })
    
    # 删失超过60个月的
    df.loc[df['time'] > 60, 'event'] = 0
    df.loc[df['time'] > 60, 'time'] = 60
    
    df.to_csv(output_path, index=False)
    print(f"Sample data created: {output_path}")


def main():
    """
    命令行入口
    """
    parser = argparse.ArgumentParser(
        description="Generate Number at Risk table for Kaplan-Meier survival curves",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 基础用法
  python main.py --input data.csv --time-col time --event-col event --output risk_table.png
  
  # 指定期刊风格
  python main.py --input data.csv --time-col time --event-col event --style NEJM --output figure.pdf
  
  # 组合图（自动生成KM曲线）
  python main.py --input data.csv --time-col time --event-col event --combine --output combined.png
  
  # 指定时间点
  python main.py --input data.csv --time-col time --event-col event --time-points 0,6,12,18,24,30,36
  
  # 创建示例数据
  python main.py --create-sample-data sample.csv
        """
    )
    
    # 输入参数
    parser.add_argument('--input', '-i', type=str, help='Input data file path')
    parser.add_argument('--time-col', type=str, help='Time column name')
    parser.add_argument('--event-col', type=str, help='Event column name (1=event, 0=censored)')
    parser.add_argument('--group-col', type=str, help='Group column name (optional)')
    
    # 输出参数
    parser.add_argument('--output', '-o', type=str, default='risk_table.png',
                       help='Output file path (default: risk_table.png)')
    parser.add_argument('--output-dir', type=str, help='Output directory for batch processing')
    
    # 风格参数
    parser.add_argument('--style', type=str, default='NEJM',
                       choices=['NEJM', 'Lancet', 'JCO', 'custom'],
                       help='Journal style (default: NEJM)')
    parser.add_argument('--time-points', type=str,
                       help='Comma-separated time points (e.g., 0,6,12,18,24)')
    
    # 图像参数
    parser.add_argument('--width', type=float, default=8, help='Figure width in inches (default: 8)')
    parser.add_argument('--height', type=float, default=6, help='Figure height in inches (default: 6)')
    parser.add_argument('--dpi', type=int, default=300, help='DPI resolution (default: 300)')
    parser.add_argument('--font-size', type=int, help='Font size (overrides style default)')
    
    # 功能开关
    parser.add_argument('--combine', action='store_true',
                       help='Generate combined KM plot with risk table')
    parser.add_argument('--km-plot', type=str, help='Path to existing KM plot image')
    parser.add_argument('--show-censored', action='store_true',
                       help='Show censored counts in table')
    parser.add_argument('--show-events', action='store_true',
                       help='Show event counts in table')
    parser.add_argument('--export-data', action='store_true',
                       help='Export risk table data as CSV')
    
    # 工具
    parser.add_argument('--create-sample-data', type=str, metavar='PATH',
                       help='Create sample survival data for testing')
    
    args = parser.parse_args()
    
    # 创建示例数据
    if args.create_sample_data:
        create_sample_data(args.create_sample_data)
        return
    
    # 验证必需参数
    if not args.input:
        parser.error("--input is required (or use --create-sample-data to generate test data)")
    
    if not args.time_col or not args.event_col:
        parser.error("--time-col and --event-col are required")
    
    # 解析时间点
    time_points = None
    if args.time_points:
        time_points = [float(x.strip()) for x in args.time_points.split(',')]
    
    # 自定义风格
    custom_style = {}
    if args.font_size:
        custom_style['font_size'] = args.font_size
    
    # 初始化生成器
    generator = RiskTableGenerator(
        style=args.style,
        time_points=time_points,
        figure_size=(args.width, args.height),
        dpi=args.dpi,
        custom_style=custom_style if custom_style else None
    )
    
    # 加载数据
    print(f"Loading data from: {args.input}")
    generator.load_data_from_file(
        args.input,
        args.time_col,
        args.event_col,
        args.group_col
    )
    print(f"Loaded {len(generator.data)} records")
    print(f"Groups: {generator.groups}")
    print(f"Time points: {generator.time_points}")
    
    # 导出数据
    if args.export_data:
        data_output = args.output.replace('.png', '.csv').replace('.pdf', '.csv')
        generator.export_risk_table_data(data_output)
    
    # 生成图像
    if args.combine:
        print("Generating combined plot...")
        generator.generate_combined_plot(
            km_plot_path=args.km_plot,
            output_path=args.output
        )
    else:
        print("Generating risk table...")
        generator.generate_risk_table(
            output_path=args.output,
            show_censored=args.show_censored,
            show_events=args.show_events
        )
    
    print("Done!")


if __name__ == "__main__":
    main()
