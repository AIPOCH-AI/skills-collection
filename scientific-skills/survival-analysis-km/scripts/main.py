#!/usr/bin/env python3
"""
Survival Analysis Tool - Kaplan-Meier Curves and Hazard Ratios
Generates publication-ready survival analysis with statistical tests.
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Survival analysis imports
try:
    from lifelines import KaplanMeierFitter, CoxPHFitter
    from lifelines.statistics import logrank_test, multivariate_logrank_test, pairwise_logrank_test
    from lifelines.plotting import add_at_risk_counts
    from lifelines.utils import restricted_mean_survival_time
except ImportError:
    print("Error: lifelines package not installed. Run: pip install lifelines")
    sys.exit(1)

try:
    import seaborn as sns
    sns.set_style("whitegrid")
except ImportError:
    pass


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Kaplan-Meier Survival Analysis with Hazard Ratios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data.csv --time survival_months --event death --group treatment --output ./results/
  %(prog)s --input data.csv --time time --event event --output ./results/ --risk-table
        """
    )
    parser.add_argument('--input', '-i', required=True, help='Input CSV file path')
    parser.add_argument('--time', '-t', required=True, help='Column name for survival time')
    parser.add_argument('--event', '-e', required=True, help='Column name for event indicator (1=event, 0=censored)')
    parser.add_argument('--group', '-g', help='Column name for grouping variable (optional)')
    parser.add_argument('--output', '-o', required=True, help='Output directory for results')
    parser.add_argument('--conf-level', '-c', type=float, default=0.95, help='Confidence level (default: 0.95)')
    parser.add_argument('--risk-table', '-r', action='store_true', help='Include risk table in plot')
    parser.add_argument('--figsize', type=str, default='10,8', help='Figure size as width,height (default: 10,8)')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for output images (default: 300)')
    return parser.parse_args()


def load_data(input_path, time_col, event_col, group_col=None):
    """Load and validate input data."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    
    # Check required columns
    if time_col not in df.columns:
        raise ValueError(f"Time column '{time_col}' not found in data. Available: {list(df.columns)}")
    if event_col not in df.columns:
        raise ValueError(f"Event column '{event_col}' not found in data. Available: {list(df.columns)}")
    if group_col and group_col not in df.columns:
        raise ValueError(f"Group column '{group_col}' not found in data. Available: {list(df.columns)}")
    
    # Validate data types
    if not pd.api.types.is_numeric_dtype(df[time_col]):
        raise ValueError(f"Time column '{time_col}' must be numeric")
    if not pd.api.types.is_numeric_dtype(df[event_col]):
        raise ValueError(f"Event column '{event_col}' must be numeric (0/1)")
    
    # Check for missing values
    if df[time_col].isna().sum() > 0:
        raise ValueError(f"Time column '{time_col}' contains missing values")
    if df[event_col].isna().sum() > 0:
        raise ValueError(f"Event column '{event_col}' contains missing values")
    
    # Check event values
    unique_events = df[event_col].unique()
    if not all(e in [0, 1] for e in unique_events):
        raise ValueError(f"Event column must contain only 0 (censored) and 1 (event), found: {unique_events}")
    
    # Remove rows with missing group values if grouping
    if group_col:
        df = df.dropna(subset=[group_col])
    
    return df


def calculate_survival_stats(df, time_col, event_col, group_col=None, alpha=0.05):
    """Calculate survival statistics."""
    results = {}
    ci = (1 - alpha) * 100
    
    if group_col:
        groups = df[group_col].unique()
        group_stats = []
        
        for group in sorted(groups):
            group_df = df[df[group_col] == group]
            kmf = KaplanMeierFitter(alpha=alpha)
            kmf.fit(group_df[time_col], event_observed=group_df[event_col], label=str(group))
            
            stats = {
                'group': group,
                'n_total': len(group_df),
                'n_events': group_df[event_col].sum(),
                'n_censored': len(group_df) - group_df[event_col].sum(),
                'median_survival': kmf.median_survival_time_,
            }
            
            # Get confidence interval for median
            try:
                ci_summary = kmf.confidence_interval_survival_function_
                # Find where survival crosses 0.5
                median_ci = kmf.confidence_interval_survival_function_.iloc[
                    (kmf.confidence_interval_survival_function_['KM_estimate_upper_0.95'] - 0.5).abs().argsort()[:1]
                ]
            except:
                pass
            
            group_stats.append(stats)
        
        results['group_stats'] = pd.DataFrame(group_stats)
    else:
        # Overall statistics
        kmf = KaplanMeierFitter(alpha=alpha)
        kmf.fit(df[time_col], event_observed=df[event_col], label="Overall")
        
        results['overall_stats'] = {
            'n_total': len(df),
            'n_events': df[event_col].sum(),
            'n_censored': len(df) - df[event_col].sum(),
            'median_survival': kmf.median_survival_time_,
        }
    
    return results


def perform_logrank_test(df, time_col, event_col, group_col):
    """Perform log-rank test between groups."""
    groups = df[group_col].unique()
    
    if len(groups) == 2:
        # Two-group comparison
        group1 = df[df[group_col] == groups[0]]
        group2 = df[df[group_col] == groups[1]]
        
        result = logrank_test(
            group1[time_col], group2[time_col],
            event_observed_A=group1[event_col],
            event_observed_B=group2[event_col]
        )
        
        return {
            'test_type': 'logrank_2group',
            'group1': groups[0],
            'group2': groups[1],
            'test_statistic': result.test_statistic,
            'p_value': result.p_value,
            'significant': result.p_value < 0.05
        }
    else:
        # Multi-group test
        result = multivariate_logrank_test(
            df[time_col], df[group_col], df[event_col]
        )
        
        # Pairwise comparisons
        pairwise_results = []
        for i, g1 in enumerate(sorted(groups)):
            for g2 in sorted(groups)[i+1:]:
                group1 = df[df[group_col] == g1]
                group2 = df[df[group_col] == g2]
                
                pair_result = logrank_test(
                    group1[time_col], group2[time_col],
                    event_observed_A=group1[event_col],
                    event_observed_B=group2[event_col]
                )
                
                pairwise_results.append({
                    'group1': g1,
                    'group2': g2,
                    'test_statistic': pair_result.test_statistic,
                    'p_value': pair_result.p_value,
                    'significant': pair_result.p_value < 0.05
                })
        
        return {
            'test_type': 'logrank_multigroup',
            'n_groups': len(groups),
            'test_statistic': result.test_statistic,
            'p_value': result.p_value,
            'significant': result.p_value < 0.05,
            'pairwise': pd.DataFrame(pairwise_results)
        }


def calculate_hazard_ratios(df, time_col, event_col, group_col):
    """Calculate hazard ratios using Cox proportional hazards model."""
    # Create dummy variables for groups
    dummies = pd.get_dummies(df[group_col], prefix='group', drop_first=True)
    cox_df = pd.concat([df[[time_col, event_col]], dummies], axis=1)
    
    cph = CoxPHFitter(alpha=0.05)
    cph.fit(cox_df, duration_col=time_col, event_col=event_col)
    
    # Extract results
    summary = cph.summary
    hr_results = []
    
    for idx, row in summary.iterrows():
        hr_results.append({
            'variable': idx,
            'hazard_ratio': row['exp(coef)'],
            'hr_lower_ci': row['exp(coef) lower 95%'],
            'hr_upper_ci': row['exp(coef) upper 95%'],
            'coef': row['coef'],
            'se': row['se(coef)'],
            'z': row['z'],
            'p_value': row['p'],
            'significant': row['p'] < 0.05
        })
    
    return {
        'summary': cph.summary,
        'hazard_ratios': pd.DataFrame(hr_results),
        'concordance': cph.concordance_index_,
        'log_likelihood': cph.log_likelihood_,
        'AIC': cph.AIC_partial_,
        'model': cph
    }


def plot_km_curve(df, time_col, event_col, group_col=None, risk_table=False, 
                  alpha=0.05, figsize=(10, 8), output_dir=None):
    """Generate Kaplan-Meier survival curve plot."""
    fig, ax = plt.subplots(figsize=figsize)
    
    kmf_list = []
    
    if group_col:
        groups = sorted(df[group_col].unique())
        colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))
        
        for i, group in enumerate(groups):
            group_df = df[df[group_col] == group]
            kmf = KaplanMeierFitter(alpha=alpha)
            kmf.fit(group_df[time_col], event_observed=group_df[event_col], 
                    label=f"{group} (n={len(group_df)})")
            kmf.plot_survival_function(ax=ax, ci_show=True, color=colors[i], 
                                       linewidth=2, at_risk_counts=False)
            kmf_list.append(kmf)
        
        ax.legend(loc='lower left', frameon=True, title=group_col)
    else:
        kmf = KaplanMeierFitter(alpha=alpha)
        kmf.fit(df[time_col], event_observed=df[event_col], label="Overall")
        kmf.plot_survival_function(ax=ax, ci_show=True, color='#2E86AB', 
                                   linewidth=2, at_risk_counts=False)
        kmf_list.append(kmf)
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Survival Probability', fontsize=12)
    ax.set_title('Kaplan-Meier Survival Curve', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    
    # Add at-risk table if requested
    if risk_table and group_col:
        add_at_risk_counts(*kmf_list, ax=ax, rows_to_show=['At risk'])
        plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'km_curve.png'), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(output_dir, 'km_curve.pdf'), bbox_inches='tight')
    
    plt.close()
    return fig


def generate_report(df, time_col, event_col, group_col, survival_stats, 
                    logrank_result, hr_result, output_dir):
    """Generate human-readable summary report."""
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("SURVIVAL ANALYSIS REPORT")
    report_lines.append("Kaplan-Meier Method with Cox Proportional Hazards")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    # Dataset summary
    report_lines.append("DATASET SUMMARY")
    report_lines.append("-" * 40)
    report_lines.append(f"Total observations: {len(df)}")
    report_lines.append(f"Total events: {df[event_col].sum()}")
    report_lines.append(f"Total censored: {len(df) - df[event_col].sum()}")
    report_lines.append(f"Censoring rate: {(1 - df[event_col].mean()) * 100:.1f}%")
    report_lines.append("")
    
    if group_col:
        report_lines.append(f"Grouping variable: {group_col}")
        for group in sorted(df[group_col].unique()):
            group_df = df[df[group_col] == group]
            report_lines.append(f"  {group}: n={len(group_df)}, events={group_df[event_col].sum()}")
        report_lines.append("")
    
    # Survival statistics
    report_lines.append("SURVIVAL STATISTICS")
    report_lines.append("-" * 40)
    
    if group_col and 'group_stats' in survival_stats:
        for _, row in survival_stats['group_stats'].iterrows():
            report_lines.append(f"\nGroup: {row['group']}")
            report_lines.append(f"  Sample size: {row['n_total']}")
            report_lines.append(f"  Events: {row['n_events']}")
            report_lines.append(f"  Censored: {row['n_censored']}")
            if pd.notna(row['median_survival']):
                report_lines.append(f"  Median survival: {row['median_survival']:.2f}")
            else:
                report_lines.append(f"  Median survival: Not reached")
    
    report_lines.append("")
    
    # Log-rank test results
    if logrank_result:
        report_lines.append("LOG-RANK TEST RESULTS")
        report_lines.append("-" * 40)
        report_lines.append(f"Test statistic: {logrank_result['test_statistic']:.4f}")
        report_lines.append(f"P-value: {logrank_result['p_value']:.6f}")
        report_lines.append(f"Significant at α=0.05: {'Yes' if logrank_result['significant'] else 'No'}")
        
        if 'pairwise' in logrank_result:
            report_lines.append("\nPairwise comparisons:")
            for _, row in logrank_result['pairwise'].iterrows():
                sig_marker = " *" if row['significant'] else ""
                report_lines.append(f"  {row['group1']} vs {row['group2']}: p={row['p_value']:.4f}{sig_marker}")
        report_lines.append("")
    
    # Hazard ratios
    if hr_result:
        report_lines.append("COX PROPORTIONAL HAZARDS MODEL")
        report_lines.append("-" * 40)
        report_lines.append(f"Concordance index: {hr_result['concordance']:.4f}")
        report_lines.append(f"Log-likelihood: {hr_result['log_likelihood']:.2f}")
        report_lines.append(f"AIC: {hr_result['AIC']:.2f}")
        report_lines.append("")
        report_lines.append("Hazard Ratios (reference: first group):")
        
        for _, row in hr_result['hazard_ratios'].iterrows():
            sig_marker = " *" if row['significant'] else ""
            report_lines.append(f"\n  {row['variable']}:")
            report_lines.append(f"    HR: {row['hazard_ratio']:.3f} "
                              f"(95% CI: {row['hr_lower_ci']:.3f}-{row['hr_upper_ci']:.3f}){sig_marker}")
            report_lines.append(f"    P-value: {row['p_value']:.4f}")
        report_lines.append("")
    
    # Interpretation notes
    report_lines.append("INTERPRETATION NOTES")
    report_lines.append("-" * 40)
    report_lines.append("* Hazard Ratio < 1: Reduced risk compared to reference")
    report_lines.append("* Hazard Ratio > 1: Increased risk compared to reference")
    report_lines.append("* HR = 0.5 means half the risk of reference group")
    report_lines.append("* Log-rank p < 0.05 indicates significantly different survival curves")
    report_lines.append("")
    report_lines.append("=" * 60)
    
    report_text = "\n".join(report_lines)
    
    with open(os.path.join(output_dir, 'report.txt'), 'w') as f:
        f.write(report_text)
    
    return report_text


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Parse figure size
    figsize = tuple(float(x) for x in args.figsize.split(','))
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    print("=" * 60)
    print("SURVIVAL ANALYSIS - KAPLAN-MEIER")
    print("=" * 60)
    
    # Load data
    print(f"\nLoading data from: {args.input}")
    try:
        df = load_data(args.input, args.time, args.event, args.group)
        print(f"Loaded {len(df)} observations")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    alpha = 1 - args.conf_level
    
    # Calculate survival statistics
    print("\nCalculating survival statistics...")
    survival_stats = calculate_survival_stats(df, args.time, args.event, args.group, alpha)
    
    # Perform log-rank test if grouping variable provided
    logrank_result = None
    if args.group:
        print("Performing log-rank test...")
        logrank_result = perform_logrank_test(df, args.time, args.event, args.group)
        print(f"  P-value: {logrank_result['p_value']:.6f}")
    
    # Calculate hazard ratios if grouping variable provided
    hr_result = None
    if args.group:
        print("Fitting Cox proportional hazards model...")
        try:
            hr_result = calculate_hazard_ratios(df, args.time, args.event, args.group)
            print(f"  Concordance: {hr_result['concordance']:.4f}")
        except Exception as e:
            print(f"  Warning: Could not fit Cox model: {e}")
    
    # Generate plot
    print("\nGenerating Kaplan-Meier curve...")
    plot_km_curve(df, args.time, args.event, args.group, args.risk_table, 
                  alpha, figsize, args.output)
    print(f"  Saved to: {os.path.join(args.output, 'km_curve.png')}")
    
    # Save statistics to CSV
    if args.group and 'group_stats' in survival_stats:
        survival_stats['group_stats'].to_csv(
            os.path.join(args.output, 'survival_stats.csv'), index=False
        )
    
    if logrank_result:
        logrank_df = pd.DataFrame([{
            'test_type': logrank_result['test_type'],
            'test_statistic': logrank_result['test_statistic'],
            'p_value': logrank_result['p_value'],
            'significant': logrank_result['significant']
        }])
        logrank_df.to_csv(os.path.join(args.output, 'logrank_test.csv'), index=False)
        
        if 'pairwise' in logrank_result:
            logrank_result['pairwise'].to_csv(
                os.path.join(args.output, 'logrank_pairwise.csv'), index=False
            )
    
    if hr_result:
        hr_result['hazard_ratios'].to_csv(
            os.path.join(args.output, 'hazard_ratios.csv'), index=False
        )
    
    # Generate report
    print("Generating summary report...")
    report = generate_report(df, args.time, args.event, args.group, 
                            survival_stats, logrank_result, hr_result, args.output)
    
    print(f"\n{'=' * 60}")
    print("ANALYSIS COMPLETE")
    print(f"{'=' * 60}")
    print(f"Results saved to: {args.output}")
    print("\nOutput files:")
    print("  - km_curve.png / km_curve.pdf: Survival curves")
    print("  - survival_stats.csv: Summary statistics")
    print("  - logrank_test.csv: Statistical test results")
    print("  - hazard_ratios.csv: Cox regression results")
    print("  - report.txt: Human-readable summary")
    
    # Print summary to console
    print("\n" + report)


if __name__ == '__main__':
    main()
