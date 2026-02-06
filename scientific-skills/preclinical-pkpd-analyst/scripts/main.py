#!/usr/bin/env python3
"""
Preclinical PK/PD Analyst
Calculate PK parameters from blood concentration-time data.
"""

import argparse
import numpy as np
from scipy.optimize import curve_fit


class PKPDAnalyzer:
    """Analyze preclinical PK/PD data."""
    
    def one_compartment_model(self, t, A, ke, ka):
        """One-compartment oral model."""
        if ka == ke:
            return A * t * np.exp(-ke * t)
        return A * (np.exp(-ke * t) - np.exp(-ka * t))
    
    def calculate_pk_parameters(self, time_points, concentrations):
        """Calculate PK parameters from data."""
        # Fit model
        popt, _ = curve_fit(self.one_compartment_model, time_points, concentrations,
                           p0=[max(concentrations), 0.1, 1.0],
                           maxfev=10000)
        
        A, ke, ka = popt
        
        # Calculate parameters
        cmax = max(concentrations)
        tmax = time_points[np.argmax(concentrations)]
        
        # AUC (trapezoidal rule)
        auc = np.trapz(concentrations, time_points)
        
        # Half-life
        t_half = 0.693 / ke
        
        # Clearance (assuming dose = 1 for normalized data)
        cl = 1 / auc if auc > 0 else 0
        
        return {
            "Cmax": cmax,
            "Tmax": tmax,
            "AUC": auc,
            "t_half": t_half,
            "ke": ke,
            "ka": ka,
            "Clearance": cl
        }
    
    def print_parameters(self, params):
        """Print PK parameters."""
        print(f"\n{'='*60}")
        print("PK PARAMETERS")
        print(f"{'='*60}\n")
        
        print(f"Cmax:        {params['Cmax']:.2f} μg/mL")
        print(f"Tmax:        {params['Tmax']:.2f} h")
        print(f"AUC(0-t):    {params['AUC']:.2f} μg·h/mL")
        print(f"t1/2:        {params['t_half']:.2f} h")
        print(f"ke:          {params['ke']:.4f} 1/h")
        print(f"ka:          {params['ka']:.4f} 1/h")
        print(f"Clearance:   {params['Clearance']:.4f} L/h")
        
        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Preclinical PK/PD Analyst")
    parser.add_argument("--data", "-d", help="PK data file (time,concentration)")
    parser.add_argument("--demo", action="store_true", help="Run demo analysis")
    
    args = parser.parse_args()
    
    analyzer = PKPDAnalyzer()
    
    if args.demo or not args.data:
        # Demo data
        time_points = np.array([0, 0.5, 1, 2, 4, 8, 12, 24])
        concentrations = np.array([0, 5.2, 8.5, 7.8, 5.1, 2.8, 1.5, 0.4])
    else:
        data = np.loadtxt(args.data, delimiter=',')
        time_points = data[:, 0]
        concentrations = data[:, 1]
    
    params = analyzer.calculate_pk_parameters(time_points, concentrations)
    analyzer.print_parameters(params)


if __name__ == "__main__":
    main()
