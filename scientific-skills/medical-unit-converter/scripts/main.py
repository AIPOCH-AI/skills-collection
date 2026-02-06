#!/usr/bin/env python3
"""Medical Unit Converter - Lab value unit conversions."""

import json

class MedicalUnitConverter:
    """Converts medical units."""
    
    CONVERSIONS = {
        ("mg_dl", "mmol_l"): {"factor": 0.0555, "name": "glucose"},
        ("mmol_l", "mg_dl"): {"factor": 18.018, "name": "glucose"},
    }
    
    def convert(self, value: float, from_unit: str, to_unit: str) -> dict:
        """Convert between units."""
        
        key = (from_unit.lower(), to_unit.lower())
        
        if key in self.CONVERSIONS:
            conv = self.CONVERSIONS[key]
            result = value * conv["factor"]
            return {
                "converted_value": round(result, 2),
                "formula": f"{value} × {conv['factor']}",
                "from_unit": from_unit,
                "to_unit": to_unit
            }
        
        return {
            "converted_value": None,
            "error": "Conversion not supported"
        }

def main():
    conv = MedicalUnitConverter()
    result = conv.convert(100, "mg_dl", "mmol_l")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
