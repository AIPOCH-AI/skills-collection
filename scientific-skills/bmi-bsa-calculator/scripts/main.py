#!/usr/bin/env python3
"""BMI & BSA Calculator - Body metrics for dosing."""

import json
import math

class BMIBSACalculator:
    """Calculates BMI and BSA."""
    
    def calculate(self, weight_kg: float, height_cm: float) -> dict:
        """Calculate BMI and BSA."""
        
        height_m = height_cm / 100
        
        # BMI
        bmi = weight_kg / (height_m ** 2)
        
        # BSA (DuBois formula)
        bsa = 0.007184 * (weight_kg ** 0.425) * (height_cm ** 0.725)
        
        # Category
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return {
            "bmi": round(bmi, 1),
            "bsa": round(bsa, 2),
            "bmi_category": category,
            "weight_kg": weight_kg,
            "height_cm": height_cm
        }

def main():
    calc = BMIBSACalculator()
    result = calc.calculate(70, 175)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
