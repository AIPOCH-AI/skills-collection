#!/usr/bin/env python3
"""
Flow Panel Designer
Design multicolor flow cytometry panels minimizing spectral overlap.
"""

import argparse
import itertools


class FlowPanelDesigner:
    """Design flow cytometry panels."""
    
    FLUOROCHROMES = {
        "FITC": {"emission_peak": 519, "excitation": "488", "brightness": "high"},
        "PE": {"emission_peak": 578, "excitation": "488", "brightness": "high"},
        "PerCP": {"emission_peak": 678, "excitation": "488", "brightness": "medium"},
        "APC": {"emission_peak": 660, "excitation": "633", "brightness": "high"},
        "PE-Cy7": {"emission_peak": 785, "excitation": "488", "brightness": "medium"},
        "APC-Cy7": {"emission_peak": 785, "excitation": "633", "brightness": "medium"},
        "BV421": {"emission_peak": 421, "excitation": "405", "brightness": "high"},
        "BV510": {"emission_peak": 510, "excitation": "405", "brightness": "high"},
        "BV605": {"emission_peak": 605, "excitation": "405", "brightness": "medium"},
        "BV650": {"emission_peak": 650, "excitation": "405", "brightness": "medium"},
        "BV785": {"emission_peak": 785, "excitation": "405", "brightness": "low"}
    }
    
    # Simplified overlap matrix (percentage)
    OVERLAP = {
        ("FITC", "PE"): 15,
        ("FITC", "PerCP"): 2,
        ("PE", "PerCP"): 8,
        ("PE", "PE-Cy7"): 5,
        ("APC", "APC-Cy7"): 5,
        ("BV421", "BV510"): 10,
        ("BV510", "BV605"): 8
    }
    
    def calculate_overlap(self, fluor1, fluor2):
        """Calculate spectral overlap between two fluorochromes."""
        key = (fluor1, fluor2)
        reverse_key = (fluor2, fluor1)
        
        if key in self.OVERLAP:
            return self.OVERLAP[key]
        elif reverse_key in self.OVERLAP:
            return self.OVERLAP[reverse_key]
        
        # Estimate based on emission peak proximity
        peak1 = self.FLUOROCHROMES[fluor1]["emission_peak"]
        peak2 = self.FLUOROCHROMES[fluor2]["emission_peak"]
        distance = abs(peak1 - peak2)
        
        if distance < 50:
            return 30  # High overlap
        elif distance < 100:
            return 10  # Moderate overlap
        else:
            return 2   # Low overlap
    
    def design_panel(self, markers, available_fluorochromes=None, max_overlap=15):
        """Design optimal panel for given markers."""
        if available_fluorochromes is None:
            available_fluorochromes = list(self.FLUOROCHROMES.keys())
        
        if len(markers) > len(available_fluorochromes):
            return {"error": "Not enough fluorochromes for all markers"}
        
        # Simple greedy assignment
        panel = []
        used_fluors = []
        
        for marker in markers:
            best_fluor = None
            best_score = float('inf')
            
            for fluor in available_fluorochromes:
                if fluor in used_fluors:
                    continue
                
                # Calculate total overlap with used fluorochromes
                total_overlap = sum(
                    self.calculate_overlap(fluor, used_fluor)
                    for used_fluor in used_fluors
                )
                
                if total_overlap < best_score and total_overlap <= max_overlap * len(used_fluors):
                    best_score = total_overlap
                    best_fluor = fluor
            
            if best_fluor:
                panel.append({
                    "marker": marker,
                    "fluorochrome": best_fluor,
                    "estimated_overlap": best_score
                })
                used_fluors.append(best_fluor)
            else:
                panel.append({
                    "marker": marker,
                    "fluorochrome": "Unassigned",
                    "note": "No suitable fluorochrome found"
                })
        
        return {"panel": panel, "fluorochromes_used": used_fluors}
    
    def check_compensation(self, panel):
        """Check if compensation matrix is needed."""
        overlaps = []
        for i, entry1 in enumerate(panel):
            for entry2 in panel[i+1:]:
                if entry1.get("fluorochrome") != "Unassigned" and entry2.get("fluorochrome") != "Unassigned":
                    overlap = self.calculate_overlap(entry1["fluorochrome"], entry2["fluorochrome"])
                    if overlap > 5:
                        overlaps.append({
                            "fluor1": entry1["fluorochrome"],
                            "fluor2": entry2["fluorochrome"],
                            "overlap": overlap
                        })
        
        return overlaps
    
    def print_panel(self, result):
        """Print panel design."""
        print(f"\n{'='*60}")
        print("FLOW CYTOMETRY PANEL DESIGN")
        print(f"{'='*60}\n")
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        print("Panel Configuration:")
        print("-"*60)
        for entry in result["panel"]:
            marker = entry["marker"]
            fluor = entry["fluorochrome"]
            overlap = entry.get("estimated_overlap", "N/A")
            print(f"  {marker:<20} → {fluor:<15} (overlap: {overlap})")
        
        print("-"*60)
        print(f"\nFluorochromes used: {', '.join(result['fluorochromes_used'])}")
        
        # Check compensation needs
        overlaps = self.check_compensation(result["panel"])
        if overlaps:
            print("\n⚠️  Compensation required for:")
            for ov in overlaps:
                print(f"  {ov['fluor1']} ↔ {ov['fluor2']}: {ov['overlap']}% overlap")
        else:
            print("\n✓ Minimal compensation needed")
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Flow Panel Designer")
    parser.add_argument("--markers", "-m", required=True, help="Comma-separated marker list")
    parser.add_argument("--fluorochromes", "-f", help="Available fluorochromes (comma-separated)")
    parser.add_argument("--max-overlap", type=int, default=15, help="Maximum acceptable overlap")
    parser.add_argument("--list-fluorochromes", action="store_true", help="List available fluorochromes")
    
    args = parser.parse_args()
    
    designer = FlowPanelDesigner()
    
    if args.list_fluorochromes:
        print("\nAvailable fluorochromes:")
        for name, data in designer.FLUOROCHROMES.items():
            print(f"  {name}: Ex{data['excitation']}nm, Em{data['emission_peak']}nm")
        return
    
    markers = [m.strip() for m in args.markers.split(",")]
    
    available = None
    if args.fluorochromes:
        available = [f.strip() for f in args.fluorochromes.split(",")]
    
    result = designer.design_panel(markers, available, args.max_overlap)
    designer.print_panel(result)


if __name__ == "__main__":
    main()
