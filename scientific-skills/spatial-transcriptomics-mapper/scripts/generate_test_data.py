#!/usr/bin/env python3
"""
示例数据生成器 - 用于测试Spatial Transcriptomics Mapper

生成模拟的Visium或Xenium格式数据
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
import h5py


def generate_visium_data(output_dir: str, n_spots: int = 500, n_genes: int = 1000, image_size: int = 600):
    """生成模拟Visium数据"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create spatial directory
    spatial_dir = output_dir / "spatial"
    spatial_dir.mkdir(exist_ok=True)
    
    print(f"Generating Visium data in {output_dir}")
    print(f"  - {n_spots} spots")
    print(f"  - {n_genes} genes")
    
    # Generate random gene names
    gene_names = [f"GENE_{i:04d}" for i in range(n_genes)]
    
    # Generate random barcodes
    barcodes = [f"AAACGA_{i:04d}-1" for i in range(n_spots)]
    
    # Generate random expression matrix (sparse-like)
    data = np.random.poisson(lam=2, size=(n_spots, n_genes))
    data = data.astype(np.float32)
    
    # Make some genes have spatial patterns
    # Gene 0: high expression in center
    center_x, center_y = image_size / 2, image_size / 2
    positions = np.random.rand(n_spots, 2) * image_size
    distances = np.sqrt((positions[:, 0] - center_x)**2 + (positions[:, 1] - center_y)**2)
    data[:, 0] = np.maximum(0, 50 - distances / 3) + np.random.poisson(2, n_spots)
    
    # Gene 1: gradient along x-axis
    data[:, 1] = positions[:, 0] / 10 + np.random.poisson(1, n_spots)
    
    # Gene 2: gradient along y-axis
    data[:, 2] = positions[:, 1] / 10 + np.random.poisson(1, n_spots)
    
    # Create H5 file
    h5_file = output_dir / "filtered_feature_bc_matrix.h5"
    with h5py.File(h5_file, 'w') as f:
        # Create matrix group
        matrix = f.create_group('matrix')
        
        # Store data (as dense for simplicity)
        matrix.create_dataset('data', data=data.flatten())
        matrix.create_dataset('indices', data=np.tile(np.arange(n_genes), n_spots))
        matrix.create_dataset('indptr', data=np.arange(0, n_spots * n_genes + 1, n_genes))
        matrix.create_dataset('shape', data=[n_genes, n_spots])
        
        # Store features (genes)
        features = matrix.create_group('features')
        features.create_dataset('id', data=np.array(gene_names, dtype=h5py.string_dtype()))
        features.create_dataset('name', data=np.array(gene_names, dtype=h5py.string_dtype()))
        features.create_dataset('feature_type', data=np.array(['Gene Expression'] * n_genes, dtype=h5py.string_dtype()))
        
        # Store barcodes
        matrix.create_dataset('barcodes', data=np.array(barcodes, dtype=h5py.string_dtype()))
    
    print(f"  Created {h5_file}")
    
    # Create tissue positions
    tissue_pos = pd.DataFrame({
        'barcode': barcodes,
        'in_tissue': [1] * n_spots,
        'array_row': np.random.randint(0, 78, n_spots),
        'array_col': np.random.randint(0, 128, n_spots),
        'pxl_col_in_fullres': positions[:, 0],
        'pxl_row_in_fullres': positions[:, 1]
    })
    tissue_pos_file = spatial_dir / "tissue_positions_list.csv"
    tissue_pos.to_csv(tissue_pos_file, index=False, header=False)
    print(f"  Created {tissue_pos_file}")
    
    # Create scale factors
    scalefactors = {
        'spot_diameter_fullres': 89.0,
        'tissue_hires_scalef': 0.17011142,
        'tissue_lowres_scalef': 0.051033426,
        'fiducial_diameter_fullres': 144.0
    }
    scalefactors_file = spatial_dir / "scalefactors_json.json"
    with open(scalefactors_file, 'w') as f:
        json.dump(scalefactors, f, indent=2)
    print(f"  Created {scalefactors_file}")
    
    # Create fake tissue image (white background with spots)
    from PIL import Image, ImageDraw
    
    # Low-res image
    lowres_size = int(image_size * scalefactors['tissue_lowres_scalef'])
    img_lowres = Image.new('RGB', (lowres_size, lowres_size), color=(240, 240, 240))
    draw = ImageDraw.Draw(img_lowres)
    
    for pos in positions * scalefactors['tissue_lowres_scalef']:
        x, y = pos
        r = 2
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(200, 200, 200))
    
    img_lowres.save(spatial_dir / "tissue_lowres_image.png")
    print(f"  Created tissue_lowres_image.png ({lowres_size}x{lowres_size})")
    
    # High-res image
    hires_size = int(image_size * scalefactors['tissue_hires_scalef'])
    img_hires = Image.new('RGB', (hires_size, hires_size), color=(240, 240, 240))
    draw = ImageDraw.Draw(img_hires)
    
    for pos in positions * scalefactors['tissue_hires_scalef']:
        x, y = pos
        r = 3
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(200, 200, 200))
    
    img_hires.save(spatial_dir / "tissue_hires_image.png")
    print(f"  Created tissue_hires_image.png ({hires_size}x{hires_size})")
    
    # Create gene list for reference
    gene_list_file = output_dir / "gene_list.txt"
    with open(gene_list_file, 'w') as f:
        for gene in gene_names[:20]:  # First 20 genes
            f.write(f"{gene}\n")
    print(f"  Created gene_list.txt (showing first 20 genes)")
    
    print(f"\nGenerated test data with spatial patterns:")
    print(f"  - GENE_0000: Expression concentrated in center")
    print(f"  - GENE_0001: Gradient along X-axis")
    print(f"  - GENE_0002: Gradient along Y-axis")
    print(f"\nTest command:")
    print(f"  python scripts/main.py --platform visium --data-dir {output_dir} --gene GENE_0000 --output ./test_output/")


def generate_xenium_data(output_dir: str, n_cells: int = 1000, n_genes: int = 500):
    """生成模拟Xenium数据（简化版）"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating Xenium data in {output_dir}")
    print(f"  - {n_cells} cells")
    print(f"  - {n_genes} genes")
    
    # Generate random gene names
    gene_names = [f"GENE_{i:04d}" for i in range(n_genes)]
    
    # Generate cell IDs
    cell_ids = [f"cell_{i:06d}" for i in range(n_cells)]
    
    print("Note: Xenium data generation requires additional dependencies.")
    print("For testing, use Visium format which is fully supported.")


def main():
    parser = argparse.ArgumentParser(description="Generate test data for Spatial Transcriptomics Mapper")
    parser.add_argument("--platform", type=str, required=True, choices=["visium", "xenium"],
                       help="Platform type")
    parser.add_argument("--output", type=str, required=True,
                       help="Output directory")
    parser.add_argument("--n-spots", type=int, default=500,
                       help="Number of spots (Visium)")
    parser.add_argument("--n-cells", type=int, default=1000,
                       help="Number of cells (Xenium)")
    parser.add_argument("--n-genes", type=int, default=1000,
                       help="Number of genes")
    parser.add_argument("--image-size", type=int, default=2000,
                       help="Image size in pixels")
    
    args = parser.parse_args()
    
    if args.platform == "visium":
        generate_visium_data(args.output, args.n_spots, args.n_genes, args.image_size)
    else:
        generate_xenium_data(args.output, args.n_cells, args.n_genes)


if __name__ == "__main__":
    main()
