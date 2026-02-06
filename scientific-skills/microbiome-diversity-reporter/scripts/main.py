#!/usr/bin/env python3
"""
Microbiome Diversity Reporter
=============================
分析16S rRNA测序结果中的Alpha和Beta多样性指标

Author: OpenClaw
Version: 1.0.0
"""

import argparse
import sys
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy import stats

# 尝试导入可选依赖
try:
    import skbio
    from skbio.diversity import alpha_diversity, beta_diversity
    from skbio.stats.ordination import pcoa
    SKBIO_AVAILABLE = True
except ImportError:
    SKBIO_AVAILABLE = False
    warnings.warn("scikit-bio not available, using fallback implementations")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class AlphaDiversityCalculator:
    """Alpha多样性计算器"""
    
    METRICS = ['shannon', 'simpson', 'chao1', 'observed_otus', 'pielou']
    
    def __init__(self):
        self.results = {}
    
    def calculate(self, otu_table: pd.DataFrame, metric: str = 'shannon') -> Dict[str, float]:
        """
        计算Alpha多样性
        
        Parameters:
        -----------
        otu_table : pd.DataFrame
            OTU表格 (samples x OTUs)
        metric : str
            多样性指标名称
            
        Returns:
        --------
        Dict[str, float]
            每个样本的多样性指数
        """
        if metric not in self.METRICS:
            raise ValueError(f"Unsupported metric: {metric}. Use one of {self.METRICS}")
        
        results = {}
        for sample in otu_table.index:
            counts = otu_table.loc[sample].values
            results[sample] = self._calculate_metric(counts, metric)
        
        self.results[metric] = results
        return results
    
    def _calculate_metric(self, counts: np.ndarray, metric: str) -> float:
        """计算单个指标"""
        # 去除零值
        counts = counts[counts > 0]
        total = counts.sum()
        
        if total == 0:
            return 0.0
        
        proportions = counts / total
        
        if metric == 'shannon':
            # Shannon指数: -sum(p_i * ln(p_i))
            return -np.sum(proportions * np.log(proportions))
        
        elif metric == 'simpson':
            # Simpson指数: 1 - sum(p_i^2)
            return 1 - np.sum(proportions ** 2)
        
        elif metric == 'chao1':
            # Chao1估计
            f1 = np.sum(counts == 1)  # singletons
            f2 = np.sum(counts == 2)  # doubletons
            s_obs = len(counts)
            if f2 == 0:
                return s_obs + f1 * (f1 - 1) / 2
            return s_obs + f1 ** 2 / (2 * f2)
        
        elif metric == 'observed_otus':
            # 观测到的OTU数量
            return len(counts)
        
        elif metric == 'pielou':
            # Pielou均匀度指数: H' / ln(S)
            shannon = -np.sum(proportions * np.log(proportions))
            s_obs = len(counts)
            if s_obs <= 1:
                return 0.0
            return shannon / np.log(s_obs)
        
        return 0.0
    
    def calculate_all(self, otu_table: pd.DataFrame) -> pd.DataFrame:
        """计算所有Alpha多样性指标"""
        all_results = {}
        for metric in self.METRICS:
            all_results[metric] = self.calculate(otu_table, metric)
        return pd.DataFrame(all_results)
    
    def rarefaction_curve(self, otu_table: pd.DataFrame, 
                          step: int = 100,
                          iterations: int = 10) -> pd.DataFrame:
        """
        生成稀疏曲线数据
        
        Parameters:
        -----------
        otu_table : pd.DataFrame
            OTU表格
        step : int
            采样步长
        iterations : int
            每个点的迭代次数
            
        Returns:
        --------
        pd.DataFrame
            稀疏曲线数据
        """
        curves = []
        max_depth = int(otu_table.sum(axis=1).min())
        depths = range(step, max_depth + 1, step)
        
        for sample in otu_table.index:
            counts = otu_table.loc[sample].values
            sample_curve = {'sample': sample, 'depths': [], 'richness': []}
            
            for depth in depths:
                richness_values = []
                for _ in range(iterations):
                    # 随机子采样
                    subsampled = self._subsample(counts, depth)
                    richness = np.sum(subsampled > 0)
                    richness_values.append(richness)
                
                sample_curve['depths'].append(depth)
                sample_curve['richness'].append(np.mean(richness_values))
            
            curves.append(sample_curve)
        
        return pd.DataFrame(curves)
    
    def _subsample(self, counts: np.ndarray, depth: int) -> np.ndarray:
        """对计数进行子采样"""
        # 创建重复列表
        expanded = np.repeat(np.arange(len(counts)), counts.astype(int))
        # 随机采样
        if len(expanded) <= depth:
            return counts
        sampled = np.random.choice(expanded, size=depth, replace=False)
        # 重新计算计数
        result = np.zeros_like(counts)
        for idx in sampled:
            result[idx] += 1
        return result


class BetaDiversityCalculator:
    """Beta多样性计算器"""
    
    METRICS = ['braycurtis', 'jaccard', 'unweighted_unifrac', 'weighted_unifrac']
    
    def __init__(self):
        self.distance_matrix = None
        self.metric = None
    
    def calculate(self, otu_table: pd.DataFrame, metric: str = 'braycurtis') -> pd.DataFrame:
        """
        计算Beta多样性距离矩阵
        
        Parameters:
        -----------
        otu_table : pd.DataFrame
            OTU表格 (samples x OTUs)
        metric : str
            距离度量方法
            
        Returns:
        --------
        pd.DataFrame
            距离矩阵
        """
        self.metric = metric
        
        if metric == 'braycurtis':
            distances = pdist(otu_table.values, metric='braycurtis')
            self.distance_matrix = pd.DataFrame(
                squareform(distances),
                index=otu_table.index,
                columns=otu_table.index
            )
        
        elif metric == 'jaccard':
            # Jaccard距离 (基于存在/缺失)
            binary_table = (otu_table > 0).astype(int)
            distances = pdist(binary_table.values, metric='jaccard')
            self.distance_matrix = pd.DataFrame(
                squareform(distances),
                index=otu_table.index,
                columns=otu_table.index
            )
        
        else:
            raise ValueError(f"Metric '{metric}' not implemented in fallback mode")
        
        return self.distance_matrix
    
    def pcoa(self, n_components: int = 3) -> Dict:
        """
        主坐标分析 (PCoA)
        
        Parameters:
        -----------
        n_components : int
            保留的维度数
            
        Returns:
        --------
        Dict
            PCoA结果
        """
        if self.distance_matrix is None:
            raise ValueError("Must calculate distance matrix first")
        
        # 使用scikit-bio的PCoA (如果可用)
        if SKBIO_AVAILABLE:
            dm = skbio.DistanceMatrix(self.distance_matrix.values, ids=self.distance_matrix.index)
            pcoa_result = skbio.stats.ordination.pcoa(dm, number_of_dimensions=n_components)
            
            return {
                'samples': pd.DataFrame(
                    pcoa_result.samples.values[:, :n_components],
                    index=self.distance_matrix.index,
                    columns=[f'PC{i+1}' for i in range(n_components)]
                ),
                'variance_explained': pcoa_result.proportion_explained.values[:n_components],
                'eigenvalues': pcoa_result.eigvals.values[:n_components]
            }
        
        # Fallback: 使用经典多维尺度分析 (MDS)
        dist_matrix = self.distance_matrix.values
        n = dist_matrix.shape[0]
        
        # 双重中心化
        J = np.eye(n) - np.ones((n, n)) / n
        B = -0.5 * J @ (dist_matrix ** 2) @ J
        
        # 特征值分解
        eigenvalues, eigenvectors = np.linalg.eigh(B)
        
        # 排序并选择前n_components个
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx][:n_components]
        eigenvectors = eigenvectors[:, idx][:, :n_components]
        
        # 计算坐标
        coords = eigenvectors * np.sqrt(np.maximum(eigenvalues, 0))
        
        # 计算方差解释比例
        total_variance = np.sum(np.maximum(eigenvalues, 0))
        variance_explained = eigenvalues / total_variance if total_variance > 0 else np.zeros(n_components)
        
        return {
            'samples': pd.DataFrame(
                coords,
                index=self.distance_matrix.index,
                columns=[f'PC{i+1}' for i in range(n_components)]
            ),
            'variance_explained': variance_explained,
            'eigenvalues': eigenvalues
        }
    
    def permanova(self, metadata: pd.DataFrame, grouping_column: str) -> Dict:
        """
        PERMANOVA统计检验
        
        Parameters:
        -----------
        metadata : pd.DataFrame
            元数据表格
        grouping_column : str
            分组列名
            
        Returns:
        --------
        Dict
            PERMANOVA结果
        """
        if self.distance_matrix is None:
            raise ValueError("Must calculate distance matrix first")
        
        # 简单实现 (基于scipy)
        groups = metadata[grouping_column].loc[self.distance_matrix.index].values
        unique_groups = np.unique(groups)
        
        if len(unique_groups) < 2:
            return {'error': 'Need at least 2 groups for PERMANOVA'}
        
        # 计算组间和组内距离
        distances = self.distance_matrix.values
        n = len(groups)
        
        # 分组索引
        group_indices = {g: np.where(groups == g)[0] for g in unique_groups}
        
        # 计算组内平均距离 (pseudo-F统计量的简化版本)
        within_sum = 0
        between_sum = 0
        
        total_mean = distances.mean()
        
        for g in unique_groups:
            idx = group_indices[g]
            group_distances = distances[np.ix_(idx, idx)]
            group_mean = group_distances.mean()
            within_sum += len(idx) * group_mean
        
        # 简化的统计量
        between_sum = total_mean * (n ** 2) - within_sum
        
        return {
            'test': 'PERMANOVA (approximation)',
            'grouping_variable': grouping_column,
            'num_groups': len(unique_groups),
            'group_sizes': {g: len(group_indices[g]) for g in unique_groups},
            'pseudo_f': between_sum / within_sum if within_sum > 0 else float('inf')
        }


class DiversityReporter:
    """多样性报告生成器"""
    
    def __init__(self, otu_table: pd.DataFrame, metadata: Optional[pd.DataFrame] = None):
        self.otu_table = otu_table
        self.metadata = metadata
        self.alpha_calc = AlphaDiversityCalculator()
        self.beta_calc = BetaDiversityCalculator()
        self.results = {}
    
    def analyze_alpha(self, metrics: Optional[List[str]] = None) -> pd.DataFrame:
        """分析Alpha多样性"""
        if metrics is None:
            metrics = ['shannon', 'simpson', 'observed_otus']
        
        results = {}
        for metric in metrics:
            results[metric] = self.alpha_calc.calculate(self.otu_table, metric)
        
        df = pd.DataFrame(results)
        self.results['alpha'] = df
        return df
    
    def analyze_beta(self, metric: str = 'braycurtis') -> Dict:
        """分析Beta多样性"""
        # 计算距离矩阵
        dist_matrix = self.beta_calc.calculate(self.otu_table, metric)
        
        # PCoA
        pcoa_result = self.beta_calc.pcoa()
        
        result = {
            'distance_matrix': dist_matrix,
            'pcoa': pcoa_result
        }
        
        # 如果有元数据，进行PERMANOVA
        if self.metadata is not None:
            for col in self.metadata.columns:
                if col != 'SampleID':
                    permanova_result = self.beta_calc.permanova(self.metadata, col)
                    result[f'permanova_{col}'] = permanova_result
        
        self.results['beta'] = result
        return result
    
    def generate_report(self, output_format: str = 'json') -> Union[str, Dict]:
        """生成报告"""
        report = {
            'summary': {
                'num_samples': len(self.otu_table),
                'num_otus': len(self.otu_table.columns),
                'total_reads': int(self.otu_table.sum().sum()),
                'reads_per_sample': {
                    'mean': float(self.otu_table.sum(axis=1).mean()),
                    'std': float(self.otu_table.sum(axis=1).std()),
                    'min': float(self.otu_table.sum(axis=1).min()),
                    'max': float(self.otu_table.sum(axis=1).max())
                }
            }
        }
        
        # 添加Alpha多样性结果
        if 'alpha' in self.results:
            alpha_df = self.results['alpha']
            report['alpha_diversity'] = {
                metric: {
                    'values': alpha_df[metric].to_dict(),
                    'statistics': {
                        'mean': float(alpha_df[metric].mean()),
                        'std': float(alpha_df[metric].std()),
                        'min': float(alpha_df[metric].min()),
                        'max': float(alpha_df[metric].max())
                    }
                }
                for metric in alpha_df.columns
            }
        
        # 添加Beta多样性结果
        if 'beta' in self.results:
            beta_result = self.results['beta']
            report['beta_diversity'] = {
                'metric': self.beta_calc.metric,
                'pcoa': {
                    'variance_explained': beta_result['pcoa']['variance_explained'].tolist(),
                    'samples': beta_result['pcoa']['samples'].to_dict('index')
                }
            }
            
            # 添加PERMANOVA结果
            for key, value in beta_result.items():
                if key.startswith('permanova_'):
                    report['beta_diversity'][key] = value
        
        if output_format == 'json':
            return json.dumps(report, indent=2)
        return report
    
    def generate_html_report(self, output_path: str):
        """生成HTML报告"""
        report_data = self.generate_report(output_format='dict')
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>微生物组多样性报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary-box {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-name {{
            font-weight: bold;
            color: #3498db;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        .metric-value {{
            font-size: 1.5em;
            color: #2c3e50;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 10px;
            border-left: 4px solid #ffc107;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <h1>🔬 微生物组多样性分析报告</h1>
    
    <div class="summary-box">
        <h2>📊 样本摘要</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-name">样本数量</div>
                <div class="metric-value">{report_data['summary']['num_samples']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">OTU数量</div>
                <div class="metric-value">{report_data['summary']['num_otus']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">总Reads数</div>
                <div class="metric-value">{report_data['summary']['total_reads']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">平均Reads/样本</div>
                <div class="metric-value">{report_data['summary']['reads_per_sample']['mean']:.0f}</div>
            </div>
        </div>
    </div>
"""
        
        # 添加Alpha多样性部分
        if 'alpha_diversity' in report_data:
            html_content += """
    <div class="summary-box">
        <h2>📈 Alpha多样性分析</h2>
        <p>Alpha多样性衡量单个样本内的微生物多样性。</p>
        <table>
            <tr>
                <th>指标</th>
                <th>平均值</th>
                <th>标准差</th>
                <th>最小值</th>
                <th>最大值</th>
            </tr>
"""
            for metric, data in report_data['alpha_diversity'].items():
                stats = data['statistics']
                html_content += f"""
            <tr>
                <td><strong>{metric.upper()}</strong></td>
                <td>{stats['mean']:.3f}</td>
                <td>{stats['std']:.3f}</td>
                <td>{stats['min']:.3f}</td>
                <td>{stats['max']:.3f}</td>
            </tr>
"""
            html_content += """
        </table>
    </div>
"""
        
        # 添加Beta多样性部分
        if 'beta_diversity' in report_data:
            pcoa = report_data['beta_diversity']['pcoa']
            html_content += f"""
    <div class="summary-box">
        <h2>🌐 Beta多样性分析</h2>
        <p>Beta多样性衡量样本间的微生物组成差异。使用 {report_data['beta_diversity']['metric']} 距离。</p>
        
        <div class="highlight">
            <strong>PCoA方差解释:</strong><br>
            PC1: {pcoa['variance_explained'][0]*100:.1f}%<br>
            PC2: {pcoa['variance_explained'][1]*100:.1f}%<br>
            PC3: {pcoa['variance_explained'][2]*100:.1f}%
        </div>
        
        <h3>样本坐标 (前3个主成分)</h3>
        <table>
            <tr>
                <th>样本</th>
                <th>PC1</th>
                <th>PC2</th>
                <th>PC3</th>
            </tr>
"""
            for sample, coords in pcoa['samples'].items():
                html_content += f"""
            <tr>
                <td>{sample}</td>
                <td>{coords['PC1']:.3f}</td>
                <td>{coords['PC2']:.3f}</td>
                <td>{coords['PC3']:.3f}</td>
            </tr>
"""
            html_content += """
        </table>
    </div>
"""
        
        html_content += """
    <div class="summary-box">
        <h2>ℹ️ 指标解释</h2>
        <ul>
            <li><strong>Shannon指数:</strong> 考虑物种丰富度和均匀度，值越高多样性越好</li>
            <li><strong>Simpson指数:</strong> 衡量随机选择两个个体属于不同物种的概率</li>
            <li><strong>Observed OTUs:</strong> 实际观测到的OTU数量</li>
            <li><strong>Chao1:</strong> 估计总物种数的非参数方法</li>
            <li><strong>Bray-Curtis:</strong> 考虑物种丰度的组成差异度量</li>
            <li><strong>Jaccard:</strong> 基于物种存在/缺失的二元距离</li>
        </ul>
    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #7f8c8d;">
        <p>Generated by Microbiome Diversity Reporter v1.0.0</p>
    </footer>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path


def load_otu_table(path: str) -> pd.DataFrame:
    """加载OTU表格"""
    df = pd.read_csv(path, sep='\t', index_col=0, comment='#')
    # 转置使样本为行，OTU为列
    if df.shape[0] > df.shape[1]:
        df = df.T
    return df


def load_metadata(path: str) -> pd.DataFrame:
    """加载元数据"""
    df = pd.read_csv(path, sep='\t')
    if 'SampleID' in df.columns:
        df.set_index('SampleID', inplace=True)
    return df


def main():
    parser = argparse.ArgumentParser(
        description='微生物组多样性分析工具 - 分析16S rRNA测序数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # Alpha多样性分析
  python main.py --input otu_table.tsv --alpha --output alpha_report.html
  
  # Beta多样性分析 (需要元数据)
  python main.py --input otu_table.tsv --beta --metadata metadata.tsv --output beta_report.html
  
  # 完整分析
  python main.py --input otu_table.tsv --full --metadata metadata.tsv --output full_report.html
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                        help='OTU/ASV表格路径 (TSV格式)')
    parser.add_argument('--metadata', '-m',
                        help='样本元数据路径 (TSV格式)')
    parser.add_argument('--metric', choices=['shannon', 'simpson', 'chao1', 'observed_otus'],
                        default='shannon',
                        help='Alpha多样性指标 (默认: shannon)')
    parser.add_argument('--alpha', action='store_true',
                        help='仅分析Alpha多样性')
    parser.add_argument('--beta', action='store_true',
                        help='仅分析Beta多样性')
    parser.add_argument('--full', action='store_true',
                        help='完整分析 (Alpha + Beta)')
    parser.add_argument('--output', '-o',
                        help='输出文件路径 (默认输出到stdout)')
    parser.add_argument('--format', choices=['html', 'json', 'markdown'],
                        default='html',
                        help='输出格式 (默认: html)')
    
    args = parser.parse_args()
    
    # 确定分析模式
    if not any([args.alpha, args.beta, args.full]):
        args.full = True  # 默认完整分析
    
    # 加载数据
    try:
        otu_table = load_otu_table(args.input)
        print(f"加载OTU表格: {otu_table.shape[0]} 样本 x {otu_table.shape[1]} OTUs", file=sys.stderr)
    except Exception as e:
        print(f"错误: 无法加载OTU表格 - {e}", file=sys.stderr)
        sys.exit(1)
    
    metadata = None
    if args.metadata:
        try:
            metadata = load_metadata(args.metadata)
            print(f"加载元数据: {metadata.shape[0]} 样本 x {metadata.shape[1]} 属性", file=sys.stderr)
        except Exception as e:
            print(f"警告: 无法加载元数据 - {e}", file=sys.stderr)
    
    # 创建分析器
    reporter = DiversityReporter(otu_table, metadata)
    
    # 执行分析
    if args.alpha or args.full:
        print("计算Alpha多样性...", file=sys.stderr)
        reporter.analyze_alpha()
    
    if args.beta or args.full:
        print("计算Beta多样性...", file=sys.stderr)
        if metadata is None:
            print("警告: Beta分析需要元数据进行分组比较", file=sys.stderr)
        reporter.analyze_beta()
    
    # 生成报告
    if args.output:
        if args.format == 'html':
            output_path = reporter.generate_html_report(args.output)
            print(f"报告已生成: {output_path}")
        elif args.format == 'json':
            report = reporter.generate_report(output_format='json')
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"JSON报告已生成: {args.output}")
        else:
            report = reporter.generate_report(output_format='dict')
            # Markdown输出
            md_content = f"""# 微生物组多样性分析报告

## 样本摘要

- **样本数量**: {report['summary']['num_samples']}
- **OTU数量**: {report['summary']['num_otus']}
- **总Reads数**: {report['summary']['total_reads']:,}
- **平均Reads/样本**: {report['summary']['reads_per_sample']['mean']:.0f}

## Alpha多样性

"""
            if 'alpha_diversity' in report:
                md_content += "| 指标 | 平均值 | 标准差 |\n"
                md_content += "|------|--------|--------|\n"
                for metric, data in report['alpha_diversity'].items():
                    stats = data['statistics']
                    md_content += f"| {metric} | {stats['mean']:.3f} | {stats['std']:.3f} |\n"
            
            with open(args.output, 'w') as f:
                f.write(md_content)
            print(f"Markdown报告已生成: {args.output}")
    else:
        # 输出到stdout
        report = reporter.generate_report(output_format='json')
        print(report)


if __name__ == '__main__':
    main()
