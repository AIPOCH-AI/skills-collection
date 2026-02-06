#!/usr/bin/env python3
"""
Western Blot Quantifier
Automatic band identification and densitometry analysis.
"""

import argparse
import numpy as np


class WBQuantifier:
    """Quantify Western Blot bands."""
    
    def detect_bands(self, image_data, lane_positions):
        """Detect bands in each lane."""
        bands = []
        
        for lane_idx, lane_pos in enumerate(lane_positions):
            # Simplified band detection
            lane_data = image_data[:, lane_pos:lane_pos+50]
            profile = np.mean(lane_data, axis=1)
            
            # Find peaks (simplified)
            peaks = []
            for i in range(1, len(profile)-1):
                if profile[i] > profile[i-1] and profile[i] > profile[i+1] and profile[i] > 100:
                    peaks.append(i)
            
            for peak in peaks:
                bands.append({
                    "lane": lane_idx + 1,
                    "position": peak,
                    "intensity": float(profile[peak])
                })
        
        return bands
    
    def calculate_relative_expression(self, bands, control_lane=1):
        """Calculate relative expression."""
        control_bands = [b for b in bands if b["lane"] == control_lane]
        
        if not control_bands:
            return bands
        
        control_intensity = control_bands[0]["intensity"]
        
        for band in bands:
            band["relative_expression"] = band["intensity"] / control_intensity
        
        return bands


def main():
    parser = argparse.ArgumentParser(description="Western Blot Quantifier")
    parser.add_argument("--image", help="Image file path")
    parser.add_argument("--lanes", type=int, default=4, help="Number of lanes")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    
    quantifier = WBQuantifier()
    
    if args.demo:
        # Demo data
        image_data = np.random.rand(300, 400) * 50
        # Add some "bands"
        image_data[100:110, 50:100] = 200
        image_data[150:160, 150:200] = 180
        
        lane_positions = [50, 150, 250, 350]
        
        bands = quantifier.detect_bands(image_data, lane_positions)
        bands = quantifier.calculate_relative_expression(bands)
        
        print(f"\n{'='*60}")
        print("WESTERN BLOT QUANTIFICATION")
        print(f"{'='*60}\n")
        
        for band in bands:
            print(f"Lane {band['lane']}: Intensity={band['intensity']:.1f}", end="")
            if "relative_expression" in band:
                print(f", Relative={band['relative_expression']:.2f}")
            else:
                print()
        
        print(f"\n{'='*60}\n")
    else:
        print("Use --demo to see example output")


if __name__ == "__main__":
    main()
