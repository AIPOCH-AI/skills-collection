#!/usr/bin/env python3
"""
Serial Dilution Calculator
Generate qPCR/ELISA dilution protocols with precise pipetting steps.
"""

import argparse


class SerialDilutionCalculator:
    """Calculate serial dilution protocols."""
    
    def calculate_dilutions(self, stock_conc, target_conc, dilution_factor, num_points):
        """Calculate serial dilution series."""
        protocol = []
        
        current_conc = stock_conc
        
        for i in range(num_points + 1):  # +1 for stock
            protocol.append({
                "dilution": i,
                "concentration": current_conc,
                "dilution_factor": dilution_factor ** i if i > 0 else 1
            })
            
            if i < num_points:
                current_conc = current_conc / dilution_factor
        
        return protocol
    
    def generate_pipetting_steps(self, dilution_factor, volume_per_tube=100):
        """Generate pipetting instructions."""
        transfer_volume = volume_per_tube / dilution_factor
        diluent_volume = volume_per_tube - transfer_volume
        
        return {
            "transfer_volume": transfer_volume,
            "diluent_volume": diluent_volume,
            "total_volume": volume_per_tube
        }


def main():
    parser = argparse.ArgumentParser(description="Serial Dilution Calculator")
    parser.add_argument("--stock", "-s", type=float, required=True, help="Stock concentration")
    parser.add_argument("--dilution-factor", "-d", type=float, default=2, help="Dilution factor")
    parser.add_argument("--points", "-p", type=int, default=6, help="Number of dilution points")
    parser.add_argument("--volume", "-v", type=float, default=100, help="Volume per tube (µL)")
    
    args = parser.parse_args()
    
    calculator = SerialDilutionCalculator()
    
    protocol = calculator.calculate_dilutions(args.stock, 0, args.dilution_factor, args.points)
    pipetting = calculator.generate_pipetting_steps(args.dilution_factor, args.volume)
    
    print(f"\n{'='*60}")
    print("SERIAL DILUTION PROTOCOL")
    print(f"{'='*60}\n")
    
    print("Concentrations:")
    for p in protocol:
        if p['dilution'] == 0:
            print(f"  Stock: {p['concentration']:.2f}")
        else:
            print(f"  1:{p['dilution_factor']:.0f}: {p['concentration']:.4f}")
    
    print(f"\nPipetting:")
    print(f"  Transfer: {pipetting['transfer_volume']:.1f} µL")
    print(f"  Add diluent: {pipetting['diluent_volume']:.1f} µL")
    print(f"  Total: {pipetting['total_volume']:.1f} µL")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
