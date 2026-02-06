#!/usr/bin/env python3
"""
Buffer Calculator
Calculate complex buffer recipes with precise measurements.
"""

import argparse


class BufferCalculator:
    """Calculate buffer formulations."""
    
    BUFFER_RECIPES = {
        "PBS": {
            "components": {
                "NaCl": {"MW": 58.44, "concentration": 137},  # mM
                "KCl": {"MW": 74.55, "concentration": 2.7},
                "Na2HPO4": {"MW": 141.96, "concentration": 10},
                "KH2PO4": {"MW": 136.09, "concentration": 1.8}
            },
            "pH": 7.4
        },
        "RIPA": {
            "components": {
                "Tris": {"MW": 121.14, "concentration": 50},  # mM
                "NaCl": {"MW": 58.44, "concentration": 150},
                "SDS": {"MW": 288.38, "concentration": 0.1, "unit": "%"},
                "Triton X-100": {"MW": None, "concentration": 1, "unit": "%"}
            },
            "pH": 7.4
        },
        "TAE": {
            "components": {
                "Tris": {"MW": 121.14, "concentration": 40},
                "Acetic Acid": {"MW": 60.05, "concentration": 20},
                "EDTA": {"MW": 372.24, "concentration": 2}
            },
            "pH": None
        }
    }
    
    def calculate(self, buffer_type, final_volume_ml, concentration_x=1.0):
        """Calculate buffer recipe."""
        buffer_type = buffer_type.upper()
        
        if buffer_type not in self.BUFFER_RECIPES:
            return None
        
        recipe = self.BUFFER_RECIPES[buffer_type]
        results = []
        
        for component, data in recipe["components"].items():
            mw = data["MW"]
            conc = data["concentration"] * concentration_x
            unit = data.get("unit", "mM")
            
            if unit == "mM":
                # Calculate grams needed
                moles = conc * final_volume_ml / 1000  # mmol to mol
                grams = moles * mw
                results.append({
                    "component": component,
                    "amount_mg": round(grams * 1000, 2),
                    "amount_g": round(grams, 3),
                    "concentration": conc,
                    "unit": "mM"
                })
            elif unit == "%":
                ml_needed = conc * final_volume_ml / 100
                results.append({
                    "component": component,
                    "amount_ml": round(ml_needed, 2),
                    "concentration": conc,
                    "unit": "%"
                })
        
        return {
            "buffer": buffer_type,
            "volume": final_volume_ml,
            "concentration": concentration_x,
            "pH": recipe.get("pH"),
            "components": results
        }
    
    def print_recipe(self, result):
        """Print formatted recipe."""
        print(f"\n{'='*60}")
        print(f"BUFFER RECIPE: {result['buffer']} ({result['concentration']}X)")
        print(f"Final Volume: {result['volume']} mL")
        if result['pH']:
            print(f"Target pH: {result['pH']}")
        print(f"{'='*60}")
        print("\nComponents:")
        
        for comp in result['components']:
            if 'amount_mg' in comp:
                print(f"  {comp['component']:<20} {comp['amount_mg']:>8.2f} mg ({comp['amount_g']:.3f} g)")
            elif 'amount_ml' in comp:
                print(f"  {comp['component']:<20} {comp['amount_ml']:>8.2f} mL")
        
        print(f"\n{'='*60}")
        print("Instructions:")
        print("1. Dissolve all solid components in ~80% of final volume")
        print("2. Add liquid components")
        print("3. Adjust pH if necessary")
        print("4. Bring to final volume with distilled water")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Buffer Calculator")
    parser.add_argument("buffer", help="Buffer type (PBS, RIPA, TAE)")
    parser.add_argument("--volume", "-v", type=float, default=500,
                       help="Final volume in mL")
    parser.add_argument("--concentration", "-c", type=float, default=1.0,
                       help="Concentration (X)")
    parser.add_argument("--list", "-l", action="store_true",
                       help="List available buffers")
    
    args = parser.parse_args()
    
    calc = BufferCalculator()
    
    if args.list:
        print("\nAvailable buffers:")
        for buf in calc.BUFFER_RECIPES.keys():
            print(f"  - {buf}")
        return
    
    result = calc.calculate(args.buffer, args.volume, args.concentration)
    
    if result:
        calc.print_recipe(result)
    else:
        print(f"Unknown buffer: {args.buffer}")
        print("Use --list to see available buffers")


if __name__ == "__main__":
    main()
