#!/usr/bin/env python3
"""
Sample Size & Power Calculator (Advanced)
Advanced calculations for complex study designs.
"""

import argparse
import numpy as np
from scipy import stats


class SampleSizeCalculator:
    """Calculate sample size for various study designs."""
    
    def ttest_independent(self, effect_size, alpha=0.05, power=0.8, ratio=1.0):
        """Sample size for independent t-test."""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n_per_group = ((z_alpha + z_beta) ** 2 * 2) / (effect_size ** 2)
        n1 = int(np.ceil(n_per_group))
        n2 = int(np.ceil(n_per_group * ratio))
        
        return {"n1": n1, "n2": n2, "total": n1 + n2}
    
    def ttest_paired(self, effect_size, alpha=0.05, power=0.8):
        """Sample size for paired t-test."""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n = ((z_alpha + z_beta) ** 2) / (effect_size ** 2)
        return {"n": int(np.ceil(n))}
    
    def chisquare(self, p1, p2, alpha=0.05, power=0.8):
        """Sample size for chi-square test (two proportions)."""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        p_avg = (p1 + p2) / 2
        effect = abs(p1 - p2)
        
        n_per_group = ((z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + 
                       z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (effect ** 2)
        
        return {"n_per_group": int(np.ceil(n_per_group)), "total": int(np.ceil(n_per_group * 2))}
    
    def survival_logrank(self, hazard_ratio, alpha=0.05, power=0.8, p_event=0.5):
        """Sample size for survival analysis (log-rank test)."""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # Schoenfeld formula
        events = ((z_alpha + z_beta) ** 2) / (p_event * (np.log(hazard_ratio) ** 2))
        n_per_group = events / p_event
        
        return {
            "events_per_group": int(np.ceil(events / 2)),
            "total_events": int(np.ceil(events)),
            "n_per_group": int(np.ceil(n_per_group)),
            "total_n": int(np.ceil(n_per_group * 2))
        }
    
    def anova(self, f, k, alpha=0.05, power=0.8):
        """Sample size for ANOVA."""
        # Simplified calculation
        z_alpha = stats.norm.ppf(1 - alpha)
        z_beta = stats.norm.ppf(power)
        
        n_per_group = ((z_alpha + z_beta) ** 2 * 2) / (f ** 2)
        return {"n_per_group": int(np.ceil(n_per_group)), "total": int(np.ceil(n_per_group * k)), "k": k}
    
    def noninferiority(self, delta, sigma, alpha=0.025, power=0.8, margin=0):
        """Sample size for non-inferiority trial."""
        z_alpha = stats.norm.ppf(1 - alpha)
        z_beta = stats.norm.ppf(power)
        
        n_per_group = ((z_alpha + z_beta) ** 2 * 2 * (sigma ** 2)) / ((delta - margin) ** 2)
        return {"n_per_group": int(np.ceil(n_per_group)), "total": int(np.ceil(n_per_group * 2))}
    
    def adjust_for_dropout(self, n, dropout_rate=0.2):
        """Adjust sample size for dropout."""
        adjusted = int(np.ceil(n / (1 - dropout_rate)))
        return {"original": n, "dropout_rate": dropout_rate, "adjusted": adjusted}
    
    def power_curve(self, effect_sizes, test_func, **kwargs):
        """Generate power curve for range of effect sizes."""
        results = []
        for es in effect_sizes:
            result = test_func(es, **kwargs)
            results.append((es, result))
        return results


def main():
    parser = argparse.ArgumentParser(description="Sample Size & Power Calculator (Advanced)")
    parser.add_argument("--test", "-t", required=True,
                       choices=["ttest-ind", "ttest-paired", "chisq", "survival", "anova", "noninf"],
                       help="Statistical test")
    parser.add_argument("--effect", "-e", type=float, help="Effect size")
    parser.add_argument("--p1", type=float, help="Proportion 1 (for chisq)")
    parser.add_argument("--p2", type=float, help="Proportion 2 (for chisq)")
    parser.add_argument("--hazard-ratio", "-hr", type=float, help="Hazard ratio (for survival)")
    parser.add_argument("--k", type=int, help="Number of groups (for ANOVA)")
    parser.add_argument("--alpha", "-a", type=float, default=0.05, help="Significance level")
    parser.add_argument("--power", "-p", type=float, default=0.8, help="Desired power")
    parser.add_argument("--ratio", "-r", type=float, default=1.0, help="Group allocation ratio")
    parser.add_argument("--dropout", "-d", type=float, default=0.2, help="Expected dropout rate")
    
    args = parser.parse_args()
    
    calc = SampleSizeCalculator()
    
    print("\n" + "=" * 70)
    print("SAMPLE SIZE CALCULATION (Advanced)")
    print("=" * 70)
    print(f"Test: {args.test}")
    print(f"Alpha: {args.alpha}, Power: {args.power}")
    
    if args.test == "ttest-ind":
        result = calc.ttest_independent(args.effect, args.alpha, args.power, args.ratio)
        print(f"\nIndependent t-test:")
        print(f"  Effect size (Cohen's d): {args.effect}")
        print(f"  Group 1 n: {result['n1']}")
        print(f"  Group 2 n: {result['n2']}")
        print(f"  Total: {result['total']}")
        
    elif args.test == "ttest-paired":
        result = calc.ttest_paired(args.effect, args.alpha, args.power)
        print(f"\nPaired t-test:")
        print(f"  Effect size: {args.effect}")
        print(f"  Sample size: {result['n']}")
        
    elif args.test == "chisq":
        result = calc.chisquare(args.p1, args.p2, args.alpha, args.power)
        print(f"\nChi-square test (two proportions):")
        print(f"  p1: {args.p1}, p2: {args.p2}")
        print(f"  Per group: {result['n_per_group']}")
        print(f"  Total: {result['total']}")
        
    elif args.test == "survival":
        result = calc.survival_logrank(args.hazard_ratio, args.alpha, args.power)
        print(f"\nSurvival analysis (log-rank test):")
        print(f"  Hazard ratio: {args.hazard_ratio}")
        print(f"  Total events required: {result['total_events']}")
        print(f"  Total sample size: {result['total_n']}")
        
    elif args.test == "anova":
        result = calc.anova(args.effect, args.k, args.alpha, args.power)
        print(f"\nANOVA:")
        print(f"  f: {args.effect}, k: {args.k}")
        print(f"  Per group: {result['n_per_group']}")
        print(f"  Total: {result['total']}")
        
    elif args.test == "noninf":
        print("\nNon-inferiority: Please use Python API with sigma parameter")
    
    # Dropout adjustment
    total_n = result.get('total', result.get('n', 0))
    if total_n > 0:
        adjusted = calc.adjust_for_dropout(total_n, args.dropout)
        print(f"\nDropout adjustment ({args.dropout*100}% rate):")
        print(f"  Original: {adjusted['original']}")
        print(f"  Adjusted: {adjusted['adjusted']}")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
