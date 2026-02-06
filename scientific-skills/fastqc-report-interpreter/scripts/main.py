#!/usr/bin/env python3
"""
FastQC Report Interpreter
Interpret NGS quality control reports in plain language.
"""

import argparse
import json


class FastQCInterpreter:
    """Interpret FastQC reports."""
    
    QC_THRESHOLDS = {
        "per_base_quality": {
            "good": {"min": 28, "description": "High quality reads"},
            "warning": {"min": 20, "description": "Acceptable quality"},
            "fail": {"min": 0, "description": "Poor quality, consider trimming"}
        },
        "per_sequence_quality": {
            "good": {"min_mean": 30, "description": "Excellent overall quality"},
            "warning": {"min_mean": 25, "description": "Good quality"},
            "fail": {"min_mean": 0, "description": "Check for systematic issues"}
        },
        "gc_content": {
            "good": {"deviation": 5, "description": "Normal GC distribution"},
            "warning": {"deviation": 10, "description": "Slightly abnormal GC"},
            "fail": {"deviation": 15, "description": "Possible contamination or bias"}
        },
        "adapter_content": {
            "good": {"max": 5, "description": "Minimal adapter contamination"},
            "warning": {"max": 10, "description": "Some adapter presence"},
            "fail": {"max": 100, "description": "Significant adapter contamination - trim required"}
        },
        "duplication_levels": {
            "good": {"max": 20, "description": "Low duplication - good library complexity"},
            "warning": {"max": 50, "description": "Moderate duplication"},
            "fail": {"max": 100, "description": "High duplication - check PCR cycles"}
        }
    }
    
    def interpret_module(self, module_name, module_data):
        """Interpret a single FastQC module."""
        thresholds = self.QC_THRESHOLDS.get(module_name, {})
        
        if not thresholds:
            return {"status": "unknown", "interpretation": "No interpretation available"}
        
        # Simplified interpretation logic
        status = "good"
        interpretation = thresholds["good"]["description"]
        
        # Check against thresholds (simplified)
        if module_data.get("failed", False):
            status = "fail"
            interpretation = thresholds["fail"]["description"]
        elif module_data.get("warning", False):
            status = "warning"
            interpretation = thresholds["warning"]["description"]
        
        return {
            "status": status,
            "interpretation": interpretation,
            "recommendations": self.get_recommendations(module_name, status)
        }
    
    def get_recommendations(self, module_name, status):
        """Get recommendations based on status."""
        recommendations = {
            "per_base_quality": {
                "fail": ["Trim low quality bases from 3' end", "Consider more stringent filtering"],
                "warning": ["Monitor quality in downstream analysis", "Consider trimming if issues persist"]
            },
            "adapter_content": {
                "fail": ["Trim adapters using cutadapt or Trimmomatic", "Re-check library prep protocol"],
                "warning": ["Mild adapter trimming recommended"]
            },
            "duplication_levels": {
                "fail": ["Reduce PCR cycles in library prep", "Consider starting with more input material"],
                "warning": ["Monitor for PCR artifacts in analysis"]
            },
            "gc_content": {
                "fail": ["Check for contamination", "Verify species matches expected genome"],
                "warning": ["Check GC bias in downstream analysis"]
            }
        }
        
        return recommendations.get(module_name, {}).get(status, ["No specific recommendations"])
    
    def interpret_report(self, fastqc_data):
        """Interpret complete FastQC report."""
        interpretations = {}
        
        for module_name, module_data in fastqc_data.items():
            interpretations[module_name] = self.interpret_module(module_name, module_data)
        
        return interpretations
    
    def print_report(self, interpretations):
        """Print interpreted report."""
        print(f"\n{'='*60}")
        print("FASTQC REPORT INTERPRETATION")
        print(f"{'='*60}\n")
        
        status_icons = {"good": "✓", "warning": "⚠", "fail": "✗", "unknown": "?"}
        
        for module, result in interpretations.items():
            icon = status_icons.get(result["status"], "?")
            print(f"{icon} {module.replace('_', ' ').title()}")
            print(f"   Status: {result['status'].upper()}")
            print(f"   {result['interpretation']}")
            
            if result.get("recommendations"):
                print("   Recommendations:")
                for rec in result["recommendations"]:
                    print(f"      • {rec}")
            print()
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="FastQC Report Interpreter")
    parser.add_argument("--report", "-r", help="FastQC JSON report")
    parser.add_argument("--demo", action="store_true", help="Show demo interpretation")
    
    args = parser.parse_args()
    
    interpreter = FastQCInterpreter()
    
    if args.report:
        with open(args.report) as f:
            fastqc_data = json.load(f)
    else:
        # Demo data
        fastqc_data = {
            "per_base_quality": {"failed": False, "warning": False, "mean": 32},
            "per_sequence_quality": {"failed": False, "warning": False, "mean": 31},
            "gc_content": {"failed": False, "warning": True, "deviation": 8},
            "adapter_content": {"failed": False, "warning": False, "percent": 2},
            "duplication_levels": {"failed": True, "warning": False, "percent": 65}
        }
    
    interpretations = interpreter.interpret_report(fastqc_data)
    interpreter.print_report(interpretations)


if __name__ == "__main__":
    main()
