#!/usr/bin/env python3
"""
Sample Size Basic
Basic sample size calculator for clinical research.
"""

import argparse
import numpy as np
from scipy import stats


class SampleSizeCalculator:
    """Calculate sample sizes for common study designs."""
    
    def two_proportions(self, p1, p2, alpha=0.05, power=0.8):
        """Sample size for comparing two proportions."""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        p_avg = (p1 + p2) / 2
        delta = abs(p1 - p2)
        
        n = ((z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + 
              z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (delta ** 2)
        
        return int(np.ceil(n))
    
    def two_means(self, mu1, mu2, sigma, alpha=0.05, power=0.8):
        """Sample size for comparing two means."""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        delta = abs(mu1 - mu2)
        n = (2 * (z_alpha + z_beta) ** 2 * sigma ** 2) / (delta ** 2)
        
        return int(np.ceil(n))
    
    def survival_analysis(self, hr, alpha=0.05, power=0.8, p_event=0.5):
        """Sample size for survival analysis."""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        events = ((z_alpha + z_beta) ** 2) / (p_event * (np.log(hr) ** 2))
        n = events / p_event
        
        return int(np.ceil(n))


def main():
    parser = argparse.ArgumentParser(description="Sample Size Basic")
    parser.add_argument("--test", "-t", choices=["proportions", "means", "survival"],
                       required=True, help="Statistical test")
    parser.add_argument("--alpha", "-a", type=float, default=0.05, help="Alpha level")
    parser.add_argument("--power", "-p", type=float, default=0.8, help="Power")
    
    # For proportions
    parser.add_argument("--p1", type=float, help="Proportion 1")
    parser.add_argument("--p2", type=float, help="Proportion 2")
    
    # For means
    parser.add_argument("--mu1", type=float, help="Mean 1")
    parser.add_argument("--mu2", type=float, help="Mean 2")
    parser.add_argument("--sd", type=float, help="Standard deviation")
    
    # For survival
    parser.add_argument("--hr", type=float, help="Hazard ratio")
    
    args = parser.parse_args()
    
    calc = SampleSizeCalculator()
    
    if args.test == "proportions":
        if args.p1 is None or args.p2 is None:
            print("Error: --p1 and --p2 required for proportions test")
            return
        n = calc.two_proportions(args.p1, args.p2, args.alpha, args.power)
        print(f"\nSample size per group: {n}")
        print(f"Total sample size: {n * 2}")
        
    elif args.test == "means":
        if args.mu1 is None or args.mu2 is None or args.sd is None:
            print("Error: --mu1, --mu2, and --sd required for means test")
            return
        n = calc.two_means(args.mu1, args.mu2, args.sd, args.alpha, args.power)
        print(f"\nSample size per group: {n}")
        print(f"Total sample size: {n * 2}")
        
    elif args.test == "survival":
        if args.hr is None:
            print("Error: --hr required for survival test")
            return
        n = calc.survival_analysis(args.hr, args.alpha, args.power)
        print(f"\nTotal sample size: {n}")


if __name__ == "__main__":
    main()
