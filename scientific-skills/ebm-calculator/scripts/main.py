#!/usr/bin/env python3
"""EBM Calculator - Evidence-Based Medicine diagnostic statistics."""

import json
from typing import Dict

class EBMCalculator:
    """Calculates EBM diagnostic test statistics."""
    
    def calculate(self, tp: int, fn: int, tn: int, fp: int, prevalence: float = None) -> Dict:
        """Calculate all EBM metrics from confusion matrix."""
        
        total = tp + fn + tn + fp
        disease_total = tp + fn
        healthy_total = tn + fp
        
        # Sensitivity and Specificity
        sensitivity = tp / disease_total if disease_total > 0 else 0
        specificity = tn / healthy_total if healthy_total > 0 else 0
        
        # PPV and NPV (using prevalence if provided)
        if prevalence is not None:
            # Bayes' theorem for population-adjusted PPV/NPV
            p_disease = prevalence
            p_healthy = 1 - prevalence
            
            ppv = (sensitivity * p_disease) / ((sensitivity * p_disease) + ((1 - specificity) * p_healthy))
            npv = (specificity * p_healthy) / ((specificity * p_healthy) + ((1 - sensitivity) * p_disease))
        else:
            ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
            npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        
        # Likelihood Ratios
        lr_positive = sensitivity / (1 - specificity) if specificity < 1 else float('inf')
        lr_negative = (1 - sensitivity) / specificity if specificity > 0 else float('inf')
        
        # Diagnostic Accuracy
        accuracy = (tp + tn) / total if total > 0 else 0
        
        return {
            "sensitivity": round(sensitivity, 4),
            "specificity": round(specificity, 4),
            "ppv": round(ppv, 4),
            "npv": round(npv, 4),
            "lr_positive": round(lr_positive, 4) if lr_positive != float('inf') else "Infinity",
            "lr_negative": round(lr_negative, 4) if lr_negative != float('inf') else "Infinity",
            "accuracy": round(accuracy, 4),
            "interpretation": self._interpret(sensitivity, specificity),
            "sample_size": total
        }
    
    def calculate_nnt(self, control_event_rate: float, experimental_event_rate: float) -> Dict:
        """Calculate Number Needed to Treat."""
        arr = control_event_rate - experimental_event_rate
        nnt = 1 / arr if arr > 0 else float('inf')
        
        return {
            "absolute_risk_reduction": round(arr, 4),
            "relative_risk_reduction": round(arr / control_event_rate, 4) if control_event_rate > 0 else 0,
            "nnt": round(nnt, 1) if nnt != float('inf') else "Infinity",
            "interpretation": f"Need to treat {int(nnt)} patients to prevent 1 event" if nnt != float('inf') else "No benefit"
        }
    
    def _interpret(self, sens: float, spec: float) -> str:
        """Interpret diagnostic performance."""
        if sens >= 0.95 and spec >= 0.95:
            return "Excellent diagnostic test"
        elif sens >= 0.90 and spec >= 0.90:
            return "Good diagnostic test"
        elif sens < 0.70 or spec < 0.70:
            return "Poor diagnostic test - consider alternatives"
        else:
            return "Moderate diagnostic test"
    
    def pretest_to_posttest(self, pretest_prob: float, lr: float) -> Dict:
        """Convert pre-test to post-test probability using likelihood ratio."""
        pretest_odds = pretest_prob / (1 - pretest_prob)
        posttest_odds = pretest_odds * lr
        posttest_prob = posttest_odds / (1 + posttest_odds)
        
        return {
            "pretest_probability": round(pretest_prob, 4),
            "likelihood_ratio": round(lr, 4),
            "posttest_probability": round(posttest_prob, 4),
            "probability_change": round(posttest_prob - pretest_prob, 4)
        }

def main():
    import sys
    calc = EBMCalculator()
    
    if len(sys.argv) >= 5:
        tp, fn, tn, fp = map(int, sys.argv[1:5])
        prev = float(sys.argv[5]) if len(sys.argv) > 5 else None
        result = calc.calculate(tp, fn, tn, fp, prev)
    else:
        # Demo
        result = calc.calculate(tp=90, fn=10, tn=80, fp=20, prevalence=0.1)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
