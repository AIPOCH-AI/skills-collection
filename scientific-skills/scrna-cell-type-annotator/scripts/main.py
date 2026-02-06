#!/usr/bin/env python3
"""
scRNA Cell Type Annotator
Auto-annotate cell clusters from single-cell RNA data.
"""

import argparse
import pandas as pd


class CellTypeAnnotator:
    """Annotate cell types from scRNA data."""
    
    MARKER_DATABASE = {
        "CD4 T cell": ["CD3D", "CD4", "IL7R"],
        "CD8 T cell": ["CD3D", "CD8A", "CD8B"],
        "B cell": ["CD79A", "CD79B", "MS4A1"],
        "Monocyte": ["CD14", "LYZ", "S100A9"],
        "NK cell": ["NKG7", "GNLY", "KLRD1"],
        "Dendritic cell": ["FCER1A", "CST3", "CLEC10A"]
    }
    
    def score_cell_type(self, cluster_markers, cell_type_markers):
        """Score how well cluster matches cell type."""
        matches = sum(1 for m in cell_type_markers if m in cluster_markers)
        return matches / len(cell_type_markers)
    
    def annotate_cluster(self, cluster_markers, top_n=3):
        """Annotate cluster based on markers."""
        scores = []
        
        for cell_type, markers in self.MARKER_DATABASE.items():
            score = self.score_cell_type(cluster_markers, markers)
            scores.append((cell_type, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
    
    def annotate_all_clusters(self, cluster_markers_dict):
        """Annotate all clusters."""
        annotations = {}
        
        for cluster_id, markers in cluster_markers_dict.items():
            annotations[cluster_id] = self.annotate_cluster(markers)
        
        return annotations


def main():
    parser = argparse.ArgumentParser(description="scRNA Cell Type Annotator")
    parser.add_argument("--markers", "-m", help="CSV with cluster markers")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    
    annotator = CellTypeAnnotator()
    
    if args.demo:
        # Demo data
        cluster_markers = {
            "Cluster 0": ["CD3D", "CD4", "IL7R", "LTB"],
            "Cluster 1": ["CD79A", "CD79B", "MS4A1"],
            "Cluster 2": ["CD14", "LYZ", "S100A9"]
        }
        
        annotations = annotator.annotate_all_clusters(cluster_markers)
        
        print(f"\n{'='*60}")
        print("CELL TYPE ANNOTATIONS")
        print(f"{'='*60}\n")
        
        for cluster, predictions in annotations.items():
            print(f"{cluster}:")
            for cell_type, score in predictions:
                print(f"  {cell_type}: {score:.2f}")
            print()
        
        print(f"{'='*60}\n")
    else:
        print("Use --demo to see example output")


if __name__ == "__main__":
    main()
