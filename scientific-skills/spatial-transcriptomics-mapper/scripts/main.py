#!/usr/bin/env python3
"""
Spatial Transcriptomics Mapper
处理10x Visium或Xenium数据，将基因表达投射回组织切片图像

Author: OpenClaw
Version: 1.0.0
"""

import os
import sys
import json
import argparse
import warnings
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize, LinearSegmentedColormap
from PIL import Image

# Optional imports with fallbacks
try:
    import scanpy as sc
    SCANPY_AVAILABLE = True
except ImportError:
    SCANPY_AVAILABLE = False
    warnings.warn("Scanpy not available. Some features may be limited.")

try:
    import squidpy as sq
    SQUIDPY_AVAILABLE = True
except ImportError:
    SQUIDPY_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

try:
    import pyarrow.parquet as pq
    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpatialMapper:
    """
    空间转录组数据映射器，支持Visium和Xenium平台
    """
    
    def __init__(
        self,
        platform: str,
        data_dir: str,
        output_dir: str = "./output",
        dpi: int = 300,
        cmap: str = "viridis"
    ):
        """
        初始化SpatialMapper
        
        Parameters
        ----------
        platform : str
            平台类型: 'visium' 或 'xenium'
        data_dir : str
            数据目录路径
        output_dir : str
            输出目录路径
        dpi : int
            输出图像DPI
        cmap : str
            颜色映射方案
        """
        self.platform = platform.lower()
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        self.cmap = cmap
        
        # Validate platform
        if self.platform not in ["visium", "xenium"]:
            raise ValueError(f"Unsupported platform: {platform}. Use 'visium' or 'xenium'.")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data containers
        self.adata = None  # AnnData object for Visium
        self.gene_names = []
        self.image = None
        self.scale_factors = {}
        self.positions = None
        
        # Xenium specific
        self.transcripts = None
        self.boundaries = None
        
        logger.info(f"Initialized SpatialMapper for {platform}")
        logger.info(f"Data directory: {data_dir}")
        logger.info(f"Output directory: {output_dir}")
    
    def load_data(self) -> None:
        """加载空间转录组数据"""
        if self.platform == "visium":
            self._load_visium_data()
        elif self.platform == "xenium":
            self._load_xenium_data()
    
    def _load_visium_data(self) -> None:
        """加载Visium数据（Space Ranger输出）"""
        if not SCANPY_AVAILABLE:
            raise ImportError("Scanpy is required for Visium data processing. Install with: pip install scanpy")
        
        logger.info("Loading Visium data...")
        
        # Check for required files
        matrix_file = self.data_dir / "filtered_feature_bc_matrix.h5"
        if not matrix_file.exists():
            # Try alternative path structure
            matrix_file = self.data_dir / "filtered_gene_bc_matrices" / "h5" / "filtered_feature_bc_matrix.h5"
        
        if not matrix_file.exists():
            raise FileNotFoundError(f"Matrix file not found: {matrix_file}")
        
        # Load AnnData
        self.adata = sc.read_visium(
            self.data_dir,
            count_file=matrix_file.name if matrix_file.parent == self.data_dir else None,
            load_images=True
        )
        
        # Store gene names
        self.gene_names = self.adata.var_names.tolist()
        logger.info(f"Loaded {len(self.gene_names)} genes and {self.adata.n_obs} spots")
        
        # Load scale factors
        scalefactors_file = self.data_dir / "spatial" / "scalefactors_json.json"
        if scalefactors_file.exists():
            with open(scalefactors_file) as f:
                self.scale_factors = json.load(f)
        
        # Load tissue image
        img_path = self.data_dir / "spatial" / "tissue_lowres_image.png"
        if img_path.exists():
            self.image = np.array(Image.open(img_path))
            logger.info(f"Loaded tissue image: {self.image.shape}")
    
    def _load_xenium_data(self) -> None:
        """加载Xenium数据"""
        logger.info("Loading Xenium data...")
        
        # Load cell feature matrix
        matrix_file = self.data_dir / "cell_feature_matrix.h5"
        if matrix_file.exists() and SCANPY_AVAILABLE:
            self.adata = sc.read_10x_h5(str(matrix_file))
            self.gene_names = self.adata.var_names.tolist()
            logger.info(f"Loaded {len(self.gene_names)} genes")
        
        # Load transcripts
        transcripts_file = self.data_dir / "transcripts.parquet"
        if transcripts_file.exists():
            if PYARROW_AVAILABLE:
                self.transcripts = pq.read_table(transcripts_file).to_pandas()
                logger.info(f"Loaded {len(self.transcripts)} transcripts")
            else:
                logger.warning("PyArrow not available, skipping transcripts loading")
        
        # Load cell boundaries
        boundaries_file = self.data_dir / "nucleus_boundaries.parquet"
        if boundaries_file.exists() and PYARROW_AVAILABLE:
            self.boundaries = pq.read_table(boundaries_file).to_pandas()
            logger.info(f"Loaded {len(self.boundaries)} boundary points")
        
        # Load morphology image
        img_file = self.data_dir / "morphology_focus.ome.tif"
        if img_file.exists():
            try:
                from tifffile import imread
                self.image = imread(str(img_file))
                logger.info(f"Loaded morphology image: {self.image.shape}")
            except ImportError:
                logger.warning("tifffile not available for OME-TIFF loading")
    
    def plot_gene_spatial(
        self,
        gene: str,
        save_path: Optional[str] = None,
        title: Optional[str] = None,
        spot_size: float = 1.0,
        alpha: float = 0.8,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        show_image: bool = True,
        figsize: Tuple[int, int] = (10, 10)
    ) -> plt.Figure:
        """
        绘制单个基因的空间表达图
        
        Parameters
        ----------
        gene : str
            基因名称
        save_path : str, optional
            保存路径
        title : str, optional
            图表标题
        spot_size : float
            Spot大小系数
        alpha : float
            透明度
        vmin, vmax : float, optional
            颜色范围
        show_image : bool
            是否显示组织图像
        figsize : tuple
            图像尺寸
            
        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        if gene not in self.gene_names:
            raise ValueError(f"Gene '{gene}' not found in dataset")
        
        if self.platform == "visium":
            return self._plot_visium_gene(
                gene, save_path, title, spot_size, alpha, 
                vmin, vmax, show_image, figsize
            )
        else:
            return self._plot_xenium_gene(
                gene, save_path, title, alpha, vmin, vmax, figsize
            )
    
    def _plot_visium_gene(
        self,
        gene: str,
        save_path: Optional[str],
        title: Optional[str],
        spot_size: float,
        alpha: float,
        vmin: Optional[float],
        vmax: Optional[float],
        show_image: bool,
        figsize: Tuple[int, int]
    ) -> plt.Figure:
        """绘制Visium单基因空间图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get gene expression
        gene_idx = self.gene_names.index(gene)
        expression = self.adata.X[:, gene_idx].toarray().flatten() if hasattr(self.adata.X, 'toarray') else self.adata.X[:, gene_idx]
        
        # Get spatial coordinates
        spatial = self.adata.obsm['spatial']
        
        # Plot tissue image background
        if show_image and self.image is not None:
            ax.imshow(self.image)
            # Scale coordinates to image
            if 'tissue_lowres_scalef' in self.scale_factors:
                scale = self.scale_factors['tissue_lowres_scalef']
                spatial_scaled = spatial * scale
            else:
                spatial_scaled = spatial
        else:
            spatial_scaled = spatial
        
        # Filter zero expression for better visualization
        nonzero_mask = expression > 0
        
        # Plot spots
        scatter = ax.scatter(
            spatial_scaled[nonzero_mask, 0],
            spatial_scaled[nonzero_mask, 1],
            c=expression[nonzero_mask],
            cmap=self.cmap,
            s=spot_size * 50,
            alpha=alpha,
            edgecolors='none',
            vmin=vmin or np.percentile(expression[expression > 0], 1),
            vmax=vmax or np.percentile(expression[expression > 0], 99)
        )
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.5)
        cbar.set_label(f'{gene} Expression', fontsize=10)
        
        # Styling
        ax.set_title(title or f'{gene} Spatial Expression', fontsize=14, fontweight='bold')
        ax.set_xlabel('X coordinate', fontsize=10)
        ax.set_ylabel('Y coordinate', fontsize=10)
        ax.axis('off' if show_image else 'on')
        
        plt.tight_layout()
        
        # Save figure
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            logger.info(f"Saved figure to {save_path}")
        
        return fig
    
    def _plot_xenium_gene(
        self,
        gene: str,
        save_path: Optional[str],
        title: Optional[str],
        alpha: float,
        vmin: Optional[float],
        vmax: Optional[float],
        figsize: Tuple[int, int]
    ) -> plt.Figure:
        """绘制Xenium单基因空间图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        if self.transcripts is not None:
            # Filter transcripts for this gene
            gene_transcripts = self.transcripts[self.transcripts['feature_name'] == gene]
            
            if len(gene_transcripts) == 0:
                logger.warning(f"No transcripts found for gene {gene}")
                ax.text(0.5, 0.5, f"No transcripts found for {gene}", 
                       ha='center', va='center', transform=ax.transAxes)
            else:
                # Plot transcripts
                scatter = ax.scatter(
                    gene_transcripts['x_location'],
                    gene_transcripts['y_location'],
                    c=gene_transcripts.get('qv', 20),  # Quality value if available
                    cmap=self.cmap,
                    s=1,
                    alpha=alpha,
                    vmin=vmin or 0,
                    vmax=vmax or 40
                )
                cbar = plt.colorbar(scatter, ax=ax, shrink=0.5)
                cbar.set_label('Quality Value', fontsize=10)
                
                logger.info(f"Plotted {len(gene_transcripts)} transcripts for {gene}")
        else:
            ax.text(0.5, 0.5, "Transcript data not available", 
                   ha='center', va='center', transform=ax.transAxes)
        
        # Styling
        ax.set_title(title or f'{gene} Transcript Locations', fontsize=14, fontweight='bold')
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            logger.info(f"Saved figure to {save_path}")
        
        return fig
    
    def plot_multi_genes(
        self,
        genes: List[str],
        mode: str = "grid",
        save_path: Optional[str] = None,
        spot_size: float = 1.0,
        alpha: float = 0.8,
        figsize_per_gene: Tuple[int, int] = (5, 5)
    ) -> plt.Figure:
        """
        绘制多个基因的空间图
        
        Parameters
        ----------
        genes : list
            基因名称列表
        mode : str
            布局模式: 'grid' 或 'overlay'
        save_path : str, optional
            保存路径
        spot_size : float
            Spot大小
        alpha : float
            透明度
        figsize_per_gene : tuple
            每个基因的子图尺寸
            
        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        # Validate genes
        missing_genes = [g for g in genes if g not in self.gene_names]
        if missing_genes:
            logger.warning(f"Genes not found: {missing_genes}")
            genes = [g for g in genes if g in self.gene_names]
        
        if not genes:
            raise ValueError("No valid genes to plot")
        
        if mode == "grid":
            n_genes = len(genes)
            n_cols = min(3, n_genes)
            n_rows = (n_genes + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(
                n_rows, n_cols,
                figsize=(figsize_per_gene[0] * n_cols, figsize_per_gene[1] * n_rows)
            )
            axes = np.atleast_1d(axes).flatten()
            
            for i, gene in enumerate(genes):
                ax = axes[i]
                self._plot_gene_on_axis(ax, gene, spot_size, alpha)
            
            # Hide unused subplots
            for i in range(len(genes), len(axes)):
                axes[i].axis('off')
        
        elif mode == "overlay":
            fig, ax = plt.subplots(figsize=(10, 10))
            self._plot_genes_overlay(ax, genes, spot_size, alpha)
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            logger.info(f"Saved multi-gene figure to {save_path}")
        
        return fig
    
    def _plot_gene_on_axis(
        self,
        ax: plt.Axes,
        gene: str,
        spot_size: float,
        alpha: float
    ) -> None:
        """在指定axis上绘制基因表达"""
        if self.platform != "visium" or self.adata is None:
            return
        
        gene_idx = self.gene_names.index(gene)
        expression = self.adata.X[:, gene_idx].toarray().flatten() if hasattr(self.adata.X, 'toarray') else self.adata.X[:, gene_idx]
        spatial = self.adata.obsm['spatial']
        
        # Scale coordinates
        if 'tissue_lowres_scalef' in self.scale_factors:
            scale = self.scale_factors['tissue_lowres_scalef']
            spatial_scaled = spatial * scale
        else:
            spatial_scaled = spatial
        
        # Plot
        nonzero_mask = expression > 0
        scatter = ax.scatter(
            spatial_scaled[nonzero_mask, 0],
            spatial_scaled[nonzero_mask, 1],
            c=expression[nonzero_mask],
            cmap=self.cmap,
            s=spot_size * 30,
            alpha=alpha,
            edgecolors='none'
        )
        
        # Add tissue image background
        if self.image is not None:
            ax.imshow(self.image, alpha=0.3)
        
        ax.set_title(gene, fontsize=12, fontweight='bold')
        ax.axis('off')
        plt.colorbar(scatter, ax=ax, shrink=0.5)
    
    def _plot_genes_overlay(
        self,
        ax: plt.Axes,
        genes: List[str],
        spot_size: float,
        alpha: float
    ) -> None:
        """叠加绘制多个基因（使用不同颜色）"""
        if self.platform != "visium" or self.adata is None:
            return
        
        # Use distinct colors for each gene
        colors = plt.cm.Set1(np.linspace(0, 1, len(genes)))
        
        spatial = self.adata.obsm['spatial']
        if 'tissue_lowres_scalef' in self.scale_factors:
            scale = self.scale_factors['tissue_lowres_scalef']
            spatial_scaled = spatial * scale
        else:
            spatial_scaled = spatial
        
        for i, gene in enumerate(genes):
            gene_idx = self.gene_names.index(gene)
            expression = self.adata.X[:, gene_idx].toarray().flatten() if hasattr(self.adata.X, 'toarray') else self.adata.X[:, gene_idx]
            
            nonzero_mask = expression > 0
            ax.scatter(
                spatial_scaled[nonzero_mask, 0],
                spatial_scaled[nonzero_mask, 1],
                c=[colors[i]],
                s=spot_size * 30 * (expression[nonzero_mask] / expression[nonzero_mask].max()),
                alpha=alpha,
                edgecolors='none',
                label=gene
            )
        
        if self.image is not None:
            ax.imshow(self.image, alpha=0.3)
        
        ax.legend(loc='upper right', title='Genes')
        ax.set_title('Multi-gene Overlay', fontsize=14, fontweight='bold')
        ax.axis('off')
    
    def plot_cluster_spatial(
        self,
        cluster_file: Optional[str] = None,
        cluster_key: str = "cluster",
        save_path: Optional[str] = None,
        spot_size: float = 1.5,
        figsize: Tuple[int, int] = (10, 10)
    ) -> plt.Figure:
        """
        绘制空间聚类图
        
        Parameters
        ----------
        cluster_file : str, optional
            聚类结果CSV文件路径
        cluster_key : str
            AnnData中的聚类obs key
        save_path : str, optional
            保存路径
        spot_size : float
            Spot大小
        figsize : tuple
            图像尺寸
            
        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        if self.platform != "visium" or self.adata is None:
            raise ValueError("Cluster spatial plot only supported for Visium data")
        
        # Load cluster assignments if provided
        if cluster_file:
            clusters = pd.read_csv(cluster_file, index_col=0)
            cluster_col = clusters.columns[0]
            self.adata.obs['cluster'] = clusters[cluster_col].astype('category')
        elif cluster_key in self.adata.obs:
            self.adata.obs['cluster'] = self.adata.obs[cluster_key].astype('category')
        else:
            raise ValueError(f"No cluster information found. Provide cluster_file or ensure '{cluster_key}' exists in adata.obs")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get coordinates
        spatial = self.adata.obsm['spatial']
        if 'tissue_lowres_scalef' in self.scale_factors:
            scale = self.scale_factors['tissue_lowres_scalef']
            spatial_scaled = spatial * scale
        else:
            spatial_scaled = spatial
        
        # Get unique clusters
        clusters = self.adata.obs['cluster'].cat.categories
        n_clusters = len(clusters)
        
        # Use distinct colors
        colors = plt.cm.tab20(np.linspace(0, 1, max(n_clusters, 20)))
        
        # Plot each cluster
        for i, cluster in enumerate(clusters):
            mask = self.adata.obs['cluster'] == cluster
            ax.scatter(
                spatial_scaled[mask, 0],
                spatial_scaled[mask, 1],
                c=[colors[i % 20]],
                s=spot_size * 50,
                alpha=0.8,
                edgecolors='black',
                linewidths=0.3,
                label=f'Cluster {cluster}'
            )
        
        # Add tissue image
        if self.image is not None:
            ax.imshow(self.image, alpha=0.3, zorder=0)
        
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0), title='Clusters')
        ax.set_title('Spatial Cluster Distribution', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            logger.info(f"Saved cluster plot to {save_path}")
        
        return fig
    
    def get_spatial_stats(self, gene: str) -> Dict:
        """
        获取基因的空间统计信息
        
        Parameters
        ----------
        gene : str
            基因名称
            
        Returns
        -------
        dict
            统计信息字典
        """
        if gene not in self.gene_names:
            raise ValueError(f"Gene '{gene}' not found")
        
        gene_idx = self.gene_names.index(gene)
        
        if self.adata is not None:
            expression = self.adata.X[:, gene_idx].toarray().flatten() if hasattr(self.adata.X, 'toarray') else self.adata.X[:, gene_idx]
        else:
            return {}
        
        spatial = self.adata.obsm.get('spatial', None)
        
        stats = {
            'gene': gene,
            'total_counts': int(expression.sum()),
            'mean_expression': float(expression.mean()),
            'max_expression': float(expression.max()),
            'expressed_spots': int((expression > 0).sum()),
            'detection_rate': float((expression > 0).mean()),
        }
        
        if spatial is not None:
            # Find hotspot (location with highest expression)
            hotspot_idx = expression.argmax()
            stats['hotspot_location'] = {
                'x': float(spatial[hotspot_idx, 0]),
                'y': float(spatial[hotspot_idx, 1])
            }
        
        return stats
    
    def generate_report(
        self,
        genes: List[str],
        output_file: str = "spatial_report.html"
    ) -> str:
        """
        生成HTML格式的综合报告
        
        Parameters
        ----------
        genes : list
            要包含在报告中的基因列表
        output_file : str
            输出HTML文件名
            
        Returns
        -------
        str
            输出文件路径
        """
        report_path = self.output_dir / output_file
        
        # Generate plots for each gene
        plot_paths = []
        for gene in genes[:6]:  # Limit to 6 genes for report
            if gene in self.gene_names:
                plot_path = self.output_dir / f"{gene}_spatial_map.png"
                self.plot_gene_spatial(gene, save_path=str(plot_path))
                plot_paths.append((gene, f"{gene}_spatial_map.png"))
        
        # Generate cluster plot if available
        cluster_plot = None
        if self.adata is not None and 'cluster' in self.adata.obs:
            cluster_plot_path = self.output_dir / "cluster_spatial_map.png"
            self.plot_cluster_spatial(save_path=str(cluster_plot_path))
            cluster_plot = "cluster_spatial_map.png"
        
        # Build HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Spatial Transcriptomics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .gene-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-top: 20px; }}
        .gene-card {{ background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .gene-card img {{ width: 100%; height: auto; border-radius: 4px; }}
        .gene-name {{ font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 10px; }}
        .stats {{ background: white; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
        .info {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>🧬 Spatial Transcriptomics Analysis Report</h1>
    
    <div class="info">
        <strong>Platform:</strong> {self.platform.upper()}<br>
        <strong>Sample:</strong> {self.data_dir.name}<br>
        <strong>Total Genes:</strong> {len(self.gene_names)}<br>
        {f"<strong>Total Spots:</strong> {self.adata.n_obs}" if self.adata else ""}
    </div>
    
    <h2>📊 Gene Expression Maps</h2>
    <div class="gene-grid">
"""
        
        for gene, plot_file in plot_paths:
            stats = self.get_spatial_stats(gene)
            html_content += f"""
        <div class="gene-card">
            <div class="gene-name">{gene}</div>
            <img src="{plot_file}" alt="{gene} expression">
            <div style="margin-top: 10px; font-size: 12px; color: #666;">
                Expression: {stats.get('total_counts', 'N/A')} counts | 
                Detection rate: {stats.get('detection_rate', 0):.1%}
            </div>
        </div>
"""
        
        html_content += """
    </div>
"""
        
        if cluster_plot:
            html_content += f"""
    <h2>🔬 Spatial Clusters</h2>
    <div class="gene-card">
        <img src="{cluster_plot}" alt="Cluster map" style="max-width: 600px;">
    </div>
"""
        
        # Add statistics table
        html_content += """
    <h2>📈 Expression Statistics</h2>
    <div class="stats">
        <table>
            <tr>
                <th>Gene</th>
                <th>Total Counts</th>
                <th>Mean Expression</th>
                <th>Max Expression</th>
                <th>Detection Rate</th>
            </tr>
"""
        
        for gene in genes[:10]:
            if gene in self.gene_names:
                stats = self.get_spatial_stats(gene)
                html_content += f"""
            <tr>
                <td>{gene}</td>
                <td>{stats.get('total_counts', 0):,}</td>
                <td>{stats.get('mean_expression', 0):.4f}</td>
                <td>{stats.get('max_expression', 0):.1f}</td>
                <td>{stats.get('detection_rate', 0):.1%}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <footer style="margin-top: 40px; text-align: center; color: #999; font-size: 12px;">
        Generated by Spatial Transcriptomics Mapper v1.0
    </footer>
</body>
</html>
"""
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {report_path}")
        return str(report_path)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Spatial Transcriptomics Mapper - 将基因表达投射回组织切片图像",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visium单基因分析
  python main.py --platform visium --data-dir ./visium/outs --gene PIK3CA --output ./results/

  # Xenium多基因分析
  python main.py --platform xenium --data-dir ./xenium/outs --genes SFTPB,SFTPC --mode multi

  # 空间聚类可视化
  python main.py --platform visium --data-dir ./data/outs --cluster-file ./clusters.csv
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--platform",
        type=str,
        required=True,
        choices=["visium", "xenium"],
        help="空间转录组平台类型"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="数据目录路径"
    )
    
    # Gene selection
    gene_group = parser.add_mutually_exclusive_group()
    gene_group.add_argument(
        "--gene",
        type=str,
        help="单个基因名称"
    )
    gene_group.add_argument(
        "--genes",
        type=str,
        help="多个基因，逗号分隔 (如: PIK3CA,PTEN,EGFR)"
    )
    
    # Analysis options
    parser.add_argument(
        "--mode",
        type=str,
        default="single",
        choices=["single", "overlay", "multi", "cluster"],
        help="分析模式 (default: single)"
    )
    parser.add_argument(
        "--cluster-file",
        type=str,
        help="聚类结果CSV文件路径 (barcode,cluster)"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="输出目录 (default: ./output)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="输出图像DPI (default: 300)"
    )
    parser.add_argument(
        "--cmap",
        type=str,
        default="viridis",
        help="颜色映射方案 (default: viridis)"
    )
    
    # Visualization options
    parser.add_argument(
        "--spot-size",
        type=float,
        default=1.0,
        help="Visium spot大小系数 (default: 1.0)"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.8,
        help="透明度 0-1 (default: 0.8)"
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=0,
        help="最小表达量过滤 (default: 0)"
    )
    
    # Advanced options
    parser.add_argument(
        "--crop",
        type=str,
        help="裁剪区域 (格式: x1,y1,x2,y2)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成HTML报告"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate data directory
    if not os.path.exists(args.data_dir):
        logger.error(f"Data directory not found: {args.data_dir}")
        sys.exit(1)
    
    # Initialize mapper
    try:
        mapper = SpatialMapper(
            platform=args.platform,
            data_dir=args.data_dir,
            output_dir=args.output,
            dpi=args.dpi,
            cmap=args.cmap
        )
        
        # Load data
        logger.info("Loading data...")
        mapper.load_data()
        
        # Determine genes to analyze
        genes_to_analyze = []
        if args.gene:
            genes_to_analyze = [args.gene]
        elif args.genes:
            genes_to_analyze = [g.strip() for g in args.genes.split(",")]
        
        # Execute based on mode
        if args.mode == "cluster" or args.cluster_file:
            # Cluster visualization mode
            logger.info("Generating cluster spatial map...")
            output_path = Path(args.output) / "cluster_spatial_map.png"
            mapper.plot_cluster_spatial(
                cluster_file=args.cluster_file,
                save_path=str(output_path),
                spot_size=args.spot_size
            )
        
        elif args.mode == "multi" and len(genes_to_analyze) > 1:
            # Multi-gene grid mode
            logger.info(f"Generating multi-gene plot for: {genes_to_analyze}")
            output_path = Path(args.output) / "multi_gene_grid.png"
            mapper.plot_multi_genes(
                genes=genes_to_analyze,
                mode="grid",
                save_path=str(output_path),
                spot_size=args.spot_size,
                alpha=args.alpha
            )
        
        elif args.mode == "overlay" and len(genes_to_analyze) > 1:
            # Overlay mode
            logger.info(f"Generating overlay plot for: {genes_to_analyze}")
            output_path = Path(args.output) / "multi_gene_overlay.png"
            mapper.plot_multi_genes(
                genes=genes_to_analyze,
                mode="overlay",
                save_path=str(output_path),
                spot_size=args.spot_size,
                alpha=args.alpha
            )
        
        elif genes_to_analyze:
            # Single gene mode
            for gene in genes_to_analyze:
                if gene in mapper.gene_names:
                    logger.info(f"Processing gene: {gene}")
                    output_path = Path(args.output) / f"{gene}_spatial_map.png"
                    mapper.plot_gene_spatial(
                        gene=gene,
                        save_path=str(output_path),
                        spot_size=args.spot_size,
                        alpha=args.alpha
                    )
                    
                    # Print stats
                    stats = mapper.get_spatial_stats(gene)
                    logger.info(f"  Total counts: {stats.get('total_counts', 'N/A')}")
                    logger.info(f"  Detection rate: {stats.get('detection_rate', 0):.1%}")
                else:
                    logger.warning(f"Gene '{gene}' not found in dataset")
                    logger.info(f"Available genes (first 10): {mapper.gene_names[:10]}")
        
        else:
            logger.info("No genes specified. Use --gene or --genes to specify genes to analyze.")
            logger.info(f"Dataset contains {len(mapper.gene_names)} genes")
        
        # Generate HTML report if requested
        if args.report and genes_to_analyze:
            logger.info("Generating HTML report...")
            report_path = mapper.generate_report(genes=genes_to_analyze)
            logger.info(f"Report saved to: {report_path}")
        
        logger.info("Analysis complete!")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
