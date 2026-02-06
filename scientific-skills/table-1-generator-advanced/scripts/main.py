#!/usr/bin/env python3
"""
Table 1 Generator
Automated baseline characteristics table for clinical papers.
"""

import argparse
import pandas as pd
import numpy as np
from scipy import stats


class Table1Generator:
    """Generate baseline characteristics table."""
    
    def __init__(self, data):
        self.data = data
    
    def detect_var_type(self, var):
        """Detect variable type."""
        if pd.api.types.is_numeric_dtype(self.data[var]):
            unique_count = self.data[var].nunique()
            if unique_count <= 5:
                return "categorical"
            return "continuous"
        return "categorical"
    
    def summarize_continuous(self, var, group_var=None):
        """Summarize continuous variable."""
        if group_var:
            results = []
            groups = self.data[group_var].unique()
            
            for group in sorted(groups):
                subset = self.data[self.data[group_var] == group][var].dropna()
                mean = subset.mean()
                std = subset.std()
                median = subset.median()
                q25 = subset.quantile(0.25)
                q75 = subset.quantile(0.75)
                n = len(subset)
                
                results.append({
                    "group": group,
                    "n": n,
                    "mean_sd": f"{mean:.1f} ± {std:.1f}",
                    "median_iqr": f"{median:.1f} [{q25:.1f}-{q75:.1f}]"
                })
            
            # Statistical test
            groups_data = [self.data[self.data[group_var] == g][var].dropna() 
                          for g in groups]
            if len(groups) == 2:
                stat, pvalue = stats.ttest_ind(groups_data[0], groups_data[1])
                test = f"t-test p={pvalue:.3f}"
            else:
                stat, pvalue = stats.f_oneway(*groups_data)
                test = f"ANOVA p={pvalue:.3f}"
            
            return results, test
        else:
            subset = self.data[var].dropna()
            mean = subset.mean()
            std = subset.std()
            median = subset.median()
            q25 = subset.quantile(0.25)
            q75 = subset.quantile(0.75)
            n = len(subset)
            
            return [{
                "n": n,
                "mean_sd": f"{mean:.1f} ± {std:.1f}",
                "median_iqr": f"{median:.1f} [{q25:.1f}-{q75:.1f}]"
            }], ""
    
    def summarize_categorical(self, var, group_var=None):
        """Summarize categorical variable."""
        if group_var:
            crosstab = pd.crosstab(self.data[var], self.data[group_var])
            percentages = pd.crosstab(self.data[var], self.data[group_var], 
                                     normalize='columns') * 100
            
            results = []
            for category in crosstab.index:
                row = {"category": category}
                for group in crosstab.columns:
                    n = crosstab.loc[category, group]
                    pct = percentages.loc[category, group]
                    row[f"group_{group}"] = f"{n} ({pct:.1f}%)"
                results.append(row)
            
            # Chi-square test
            chi2, pvalue, dof, expected = stats.chi2_contingency(crosstab)
            test = f"Chi-square p={pvalue:.3f}"
            
            return results, test
        else:
            counts = self.data[var].value_counts()
            percentages = self.data[var].value_counts(normalize=True) * 100
            
            results = []
            for category in counts.index:
                results.append({
                    "category": category,
                    "n_pct": f"{counts[category]} ({percentages[category]:.1f}%)"
                })
            
            return results, ""
    
    def generate_table(self, group_var=None, var_list=None):
        """Generate complete Table 1."""
        if var_list is None:
            var_list = [c for c in self.data.columns if c != group_var]
        
        table_rows = []
        
        for var in var_list:
            var_type = self.detect_var_type(var)
            
            if var_type == "continuous":
                results, test = self.summarize_continuous(var, group_var)
                table_rows.append({
                    "Variable": var,
                    "Type": "Continuous",
                    "Statistics": results,
                    "P-value": test
                })
            else:
                results, test = self.summarize_categorical(var, group_var)
                for r in results:
                    table_rows.append({
                        "Variable": f"  {r.get('category', var)}",
                        "Type": "Categorical",
                        "Statistics": r,
                        "P-value": test if r == results[0] else ""
                    })
        
        return table_rows
    
    def print_table(self, table_rows):
        """Print formatted table."""
        print("\n" + "=" * 80)
        print("TABLE 1: BASELINE CHARACTERISTICS")
        print("=" * 80)
        
        for row in table_rows:
            print(f"\n{row['Variable']} ({row['Type']})")
            print(f"  Stats: {row['Statistics']}")
            if row['P-value']:
                print(f"  Test: {row['P-value']}")
        
        print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Table 1 Generator")
    parser.add_argument("--data", "-d", required=True, help="Data CSV file")
    parser.add_argument("--group", "-g", help="Grouping variable")
    parser.add_argument("--vars", "-v", help="Comma-separated variables to include")
    parser.add_argument("--output", "-o", help="Output CSV file")
    
    args = parser.parse_args()
    
    # Load data
    data = pd.read_csv(args.data)
    
    # Select variables
    var_list = None
    if args.vars:
        var_list = [v.strip() for v in args.vars.split(",")]
    
    # Generate table
    generator = Table1Generator(data)
    table = generator.generate_table(args.group, var_list)
    
    # Print
    generator.print_table(table)
    
    # Save if requested
    if args.output:
        # Flatten for CSV output
        flat_rows = []
        for row in table:
            flat_row = {
                "Variable": row["Variable"],
                "Type": row["Type"],
                "P-value": row["P-value"]
            }
            if isinstance(row["Statistics"], list):
                for i, stat in enumerate(row["Statistics"]):
                    for key, val in stat.items():
                        flat_row[f"Group{i}_{key}"] = val
            else:
                for key, val in row["Statistics"].items():
                    flat_row[key] = val
            flat_rows.append(flat_row)
        
        df = pd.DataFrame(flat_rows)
        df.to_csv(args.output, index=False)
        print(f"Table saved to: {args.output}")


if __name__ == "__main__":
    main()
