#!/usr/bin/env python3
"""
Outlier Detection Handler
Statistical outlier identification and handling recommendations.
"""

import argparse
import numpy as np
from scipy import stats


class OutlierDetector:
    """Detect and handle statistical outliers."""
    
    def zscore_method(self, data, threshold=3):
        """Detect outliers using Z-score."""
        z_scores = np.abs(stats.zscore(data))
        outliers = np.where(z_scores > threshold)[0]
        return outliers, z_scores
    
    def iqr_method(self, data):
        """Detect outliers using IQR."""
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = np.where((data < lower_bound) | (data > upper_bound))[0]
        return outliers, (lower_bound, upper_bound)
    
    def grubbs_test(self, data, alpha=0.05):
        """Grubbs' test for outliers."""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        G = np.max(np.abs(data - mean)) / std
        
        # Critical value (simplified)
        t_critical = stats.t.ppf(1 - alpha / (2 * n), n - 2)
        G_critical = ((n - 1) / np.sqrt(n)) * np.sqrt(t_critical**2 / (n - 2 + t_critical**2))
        
        is_outlier = G > G_critical
        
        return is_outlier, G, G_critical
    
    def recommend_handling(self, outlier_count, total_count):
        """Recommend outlier handling approach."""
        percentage = (outlier_count / total_count) * 100
        
        if percentage < 1:
            return "Remove outliers - likely data entry errors"
        elif percentage < 5:
            return "Investigate outliers - may be legitimate extreme values"
        else:
            return "Consider robust statistical methods - high outlier percentage"


def main():
    parser = argparse.ArgumentParser(description="Outlier Detection Handler")
    parser.add_argument("--data", "-d", help="Data file (one value per line)")
    parser.add_argument("--method", "-m", choices=["zscore", "iqr", "grubbs"],
                       default="iqr", help="Detection method")
    parser.add_argument("--threshold", "-t", type=float, default=3,
                       help="Z-score threshold")
    
    args = parser.parse_args()
    
    detector = OutlierDetector()
    
    if args.data:
        with open(args.data) as f:
            data = np.array([float(line.strip()) for line in f if line.strip()])
    else:
        # Demo data
        data = np.array([10, 12, 11, 13, 12, 11, 100, 12, 11, 13])
    
    print(f"\n{'='*60}")
    print("OUTLIER DETECTION RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Data points: {len(data)}")
    print(f"Mean: {np.mean(data):.2f}")
    print(f"Std: {np.std(data):.2f}")
    print()
    
    if args.method == "zscore":
        outliers, scores = detector.zscore_method(data, args.threshold)
        print(f"Method: Z-score (threshold = {args.threshold})")
        
    elif args.method == "iqr":
        outliers, bounds = detector.iqr_method(data)
        print(f"Method: IQR")
        print(f"Bounds: [{bounds[0]:.2f}, {bounds[1]:.2f}]")
        
    elif args.method == "grubbs":
        is_outlier, G, G_critical = detector.grubbs_test(data)
        print(f"Method: Grubbs' test")
        print(f"G statistic: {G:.3f}")
        print(f"G critical: {G_critical:.3f}")
        outliers = [np.argmax(np.abs(data - np.mean(data)))] if is_outlier else []
    
    print(f"\nOutliers detected: {len(outliers)}")
    if len(outliers) > 0:
        print("Outlier values:")
        for idx in outliers:
            print(f"  Index {idx}: {data[idx]}")
    
    recommendation = detector.recommend_handling(len(outliers), len(data))
    print(f"\nRecommendation: {recommendation}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
