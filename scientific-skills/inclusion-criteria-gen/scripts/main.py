#!/usr/bin/env python3
"""
Inclusion/Exclusion Criteria Generator and Optimizer

Generates and optimizes clinical trial eligibility criteria to balance
scientific rigor with recruitment feasibility.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class CriteriaCategory(Enum):
    DEMOGRAPHICS = "demographics"
    DISEASE_SEVERITY = "disease_severity"
    MEDICAL_HISTORY = "medical_history"
    CONCOMITANT_MEDS = "concomitant_meds"
    LABORATORY = "laboratory"
    LIFESTYLE = "lifestyle"
    COMPLIANCE = "compliance"
    SAFETY = "safety"


class Priority(Enum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class Impact(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Criterion:
    id: str
    criterion: str
    category: CriteriaCategory
    rationale: str
    priority: Priority = Priority.REQUIRED
    impact: Impact = Impact.MEDIUM
    flexibility: Optional[str] = None
    alternatives: List[str] = field(default_factory=list)


@dataclass
class StudyDesign:
    indication: str
    phase: str
    population: str
    study_duration: str
    age_range: Dict[str, int] = field(default_factory=lambda: {"min": 18, "max": 75})
    treatment_type: str = ""
    primary_endpoints: List[str] = field(default_factory=list)
    secondary_endpoints: List[str] = field(default_factory=list)
    safety_considerations: List[str] = field(default_factory=list)
    concomitant_meds_allowed: List[str] = field(default_factory=list)
    concomitant_meds_prohibited: List[str] = field(default_factory=list)


class CriteriaGenerator:
    """Generate inclusion/exclusion criteria from study design parameters."""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load criteria templates by therapeutic area."""
        templates_path = os.path.join(
            os.path.dirname(__file__), "..", "references", "criteria_templates.json"
        )
        if os.path.exists(templates_path):
            with open(templates_path, 'r') as f:
                return json.load(f)
        return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict:
        """Default templates for common therapeutic areas."""
        return {
            "diabetes": {
                "inclusion_templates": [
                    {
                        "id": "DM_INC_001",
                        "criterion": "Age {}-{} years, inclusive",
                        "category": "demographics",
                        "rationale": "Adult population per regulatory guidance"
                    },
                    {
                        "id": "DM_INC_002",
                        "criterion": "Diagnosed with Type 2 Diabetes Mellitus for at least 6 months",
                        "category": "disease_severity",
                        "rationale": "Ensure stable disease status"
                    },
                    {
                        "id": "DM_INC_003",
                        "criterion": "HbA1c >= {}% and <= {}% at screening",
                        "category": "disease_severity",
                        "rationale": "Optimal range for detecting treatment effect"
                    },
                    {
                        "id": "DM_INC_004",
                        "criterion": "BMI >= 18.5 kg/m²",
                        "category": "demographics",
                        "rationale": "Ensure appropriate body composition for dosing"
                    }
                ],
                "exclusion_templates": [
                    {
                        "id": "DM_EXC_001",
                        "criterion": "History of severe hypoglycemia requiring assistance within 6 months",
                        "category": "safety",
                        "rationale": "Exclude high-risk hypoglycemia patients"
                    },
                    {
                        "id": "DM_EXC_002",
                        "criterion": "eGFR < 30 mL/min/1.73m²",
                        "category": "laboratory",
                        "rationale": "Renal function requirement for safety"
                    },
                    {
                        "id": "DM_EXC_003",
                        "criterion": "Significant cardiovascular event within 6 months",
                        "category": "safety",
                        "rationale": "Recent CV events may confound safety assessment"
                    }
                ]
            },
            "oncology": {
                "inclusion_templates": [
                    {
                        "id": "ONC_INC_001",
                        "criterion": "Age >= 18 years",
                        "category": "demographics",
                        "rationale": "Adult population"
                    },
                    {
                        "id": "ONC_INC_002",
                        "criterion": "Histologically confirmed {}",
                        "category": "disease_severity",
                        "rationale": "Confirmed diagnosis required"
                    },
                    {
                        "id": "ONC_INC_003",
                        "criterion": "ECOG performance status 0-1",
                        "category": "disease_severity",
                        "rationale": "Adequate performance status for study participation"
                    },
                    {
                        "id": "ONC_INC_004",
                        "criterion": "Adequate organ function as defined by laboratory parameters",
                        "category": "laboratory",
                        "rationale": "Safety requirement for treatment"
                    }
                ],
                "exclusion_templates": [
                    {
                        "id": "ONC_EXC_001",
                        "criterion": "Prior treatment with {}",
                        "category": "medical_history",
                        "rationale": "Exclude prior exposure to study drug class"
                    },
                    {
                        "id": "ONC_EXC_002",
                        "criterion": "Active autoimmune disease requiring systemic therapy",
                        "category": "safety",
                        "rationale": "Immunotherapy safety consideration"
                    }
                ]
            },
            "cardiovascular": {
                "inclusion_templates": [
                    {
                        "id": "CV_INC_001",
                        "criterion": "Age {}-{} years",
                        "category": "demographics",
                        "rationale": "Target population age range"
                    },
                    {
                        "id": "CV_INC_002",
                        "criterion": "Established diagnosis of {}",
                        "category": "disease_severity",
                        "rationale": "Confirmed indication"
                    },
                    {
                        "id": "CV_INC_003",
                        "criterion": "NYHA Class II-III heart failure",
                        "category": "disease_severity",
                        "rationale": "Target disease severity"
                    }
                ],
                "exclusion_templates": [
                    {
                        "id": "CV_EXC_001",
                        "criterion": "Systolic blood pressure < 90 or > 180 mmHg",
                        "category": "laboratory",
                        "rationale": "Blood pressure safety limits"
                    },
                    {
                        "id": "CV_EXC_002",
                        "criterion": "Severe hepatic impairment (Child-Pugh C)",
                        "category": "laboratory",
                        "rationale": "Hepatic function requirement"
                    }
                ]
            },
            "general": {
                "inclusion_templates": [
                    {
                        "id": "GEN_INC_001",
                        "criterion": "Age {}-{} years, inclusive",
                        "category": "demographics",
                        "rationale": "Adult population per study design"
                    },
                    {
                        "id": "GEN_INC_002",
                        "criterion": "Able to provide written informed consent",
                        "category": "compliance",
                        "rationale": "Regulatory requirement"
                    },
                    {
                        "id": "GEN_INC_003",
                        "criterion": "Willing and able to comply with study procedures",
                        "category": "compliance",
                        "rationale": "Protocol compliance requirement"
                    }
                ],
                "exclusion_templates": [
                    {
                        "id": "GEN_EXC_001",
                        "criterion": "Participation in another interventional clinical trial within 30 days",
                        "category": "compliance",
                        "rationale": "Avoid confounding from other interventions"
                    },
                    {
                        "id": "GEN_EXC_002",
                        "criterion": "Known hypersensitivity to study drug or components",
                        "category": "safety",
                        "rationale": "Allergy safety precaution"
                    },
                    {
                        "id": "GEN_EXC_003",
                        "criterion": "Pregnant or breastfeeding women",
                        "category": "safety",
                        "rationale": "Reproductive safety"
                    }
                ]
            }
        }
    
    def _get_therapeutic_area(self, indication: str) -> str:
        """Map indication to therapeutic area."""
        indication_lower = indication.lower()
        
        diabetes_keywords = ['diabetes', 'diabetic', 't2dm', 'type 2', 't1dm']
        if any(kw in indication_lower for kw in diabetes_keywords):
            return "diabetes"
        
        oncology_keywords = ['cancer', 'carcinoma', 'tumor', 'tumour', 'malignancy', 'neoplasm']
        if any(kw in indication_lower for kw in oncology_keywords):
            return "oncology"
        
        cv_keywords = ['cardiovascular', 'heart failure', 'hypertension', 'myocardial', 'stroke']
        if any(kw in indication_lower for kw in cv_keywords):
            return "cardiovascular"
        
        return "general"
    
    def generate(self, design: StudyDesign) -> Dict[str, Any]:
        """Generate criteria based on study design."""
        area = self._get_therapeutic_area(design.indication)
        templates = self.templates.get(area, self.templates["general"])
        
        inclusion_criteria = []
        exclusion_criteria = []
        
        # Generate inclusion criteria
        for idx, template in enumerate(templates.get("inclusion_templates", templates.get("inclusion", [])), 1):
            criterion_text = template["criterion"]
            
            # Format with study-specific values
            if "{}-{}" in criterion_text or "{}" in criterion_text:
                if "Age" in criterion_text and "{}-{}" in criterion_text:
                    criterion_text = criterion_text.format(
                        design.age_range["min"], 
                        design.age_range["max"]
                    )
                elif "HbA1c" in criterion_text:
                    # Default HbA1c range for diabetes trials
                    if area == "diabetes":
                        criterion_text = criterion_text.format(7.5, 10.5)
                elif "confirmed" in criterion_text.lower():
                    criterion_text = criterion_text.format(design.indication)
            
            inclusion_criteria.append({
                "id": f"I{idx}",
                "criterion": criterion_text,
                "category": template["category"],
                "rationale": template["rationale"],
                "priority": "required",
                "impact": "medium"
            })
        
        # Generate exclusion criteria
        for idx, template in enumerate(templates.get("exclusion_templates", templates.get("exclusion", [])), 1):
            criterion_text = template["criterion"]
            
            # Format with study-specific values
            if "{}" in criterion_text and "treatment with" in criterion_text:
                # Generic placeholder - keep as template if no specific drug
                criterion_text = criterion_text.format("[investigational agent]")
            
            exclusion_criteria.append({
                "id": f"E{idx}",
                "criterion": criterion_text,
                "category": template["category"],
                "rationale": template["rationale"],
                "priority": "required",
                "impact": "high" if template["category"] == "safety" else "medium"
            })
        
        # Add phase-specific criteria
        if design.phase.lower() in ["phase 1", "phase i"]:
            exclusion_criteria.append({
                "id": f"E{len(exclusion_criteria)+1}",
                "criterion": "Any clinically significant disease that may compromise safety",
                "category": "safety",
                "rationale": "Phase 1 safety assessment requires healthy baseline",
                "priority": "required",
                "impact": "high"
            })
        
        # Calculate estimated metrics
        screen_success = self._estimate_screen_success(area, inclusion_criteria, exclusion_criteria)
        
        return {
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "study_design": {
                "indication": design.indication,
                "phase": design.phase,
                "population": design.population
            },
            "recruitment_metrics": {
                "estimated_screen_success_rate": screen_success,
                "estimated_enrollment_rate": round(screen_success * 0.7, 2),
                "complexity_score": self._calculate_complexity(inclusion_criteria, exclusion_criteria),
                "key_barriers": self._identify_barriers(exclusion_criteria)
            }
        }
    
    def _estimate_screen_success(self, area: str, inclusion: List[Dict], exclusion: List[Dict]) -> float:
        """Estimate screening success rate based on criteria complexity."""
        base_rates = {
            "diabetes": 0.40,
            "oncology": 0.35,
            "cardiovascular": 0.45,
            "general": 0.50
        }
        
        base_rate = base_rates.get(area, 0.45)
        
        # Adjust for number of criteria
        total_criteria = len(inclusion) + len(exclusion)
        if total_criteria > 15:
            base_rate -= 0.10
        elif total_criteria > 10:
            base_rate -= 0.05
        
        # Adjust for restrictive lab values
        restrictive_labs = sum(1 for e in exclusion if e.get("category") == "laboratory")
        base_rate -= restrictive_labs * 0.02
        
        return round(max(0.10, min(0.70, base_rate)), 2)
    
    def _calculate_complexity(self, inclusion: List[Dict], exclusion: List[Dict]) -> Dict:
        """Calculate complexity metrics for criteria set."""
        total = len(inclusion) + len(exclusion)
        
        categories = {}
        for c in inclusion + exclusion:
            cat = c.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_criteria": total,
            "inclusion_count": len(inclusion),
            "exclusion_count": len(exclusion),
            "category_distribution": categories,
            "complexity_level": "high" if total > 20 else "medium" if total > 10 else "low"
        }
    
    def _identify_barriers(self, exclusion: List[Dict]) -> List[str]:
        """Identify potential recruitment barriers from exclusion criteria."""
        barriers = []
        
        high_impact = [e for e in exclusion if e.get("impact") == "high"]
        for criterion in high_impact:
            cat = criterion.get("category")
            if cat == "laboratory":
                barriers.append(f"Restrictive laboratory criteria: {criterion['criterion'][:50]}...")
            elif cat == "medical_history":
                barriers.append(f"Medical history exclusion: {criterion['criterion'][:50]}...")
            elif cat == "concomitant_meds":
                barriers.append(f"Medication restrictions")
        
        return barriers[:3]  # Top 3 barriers


class CriteriaOptimizer:
    """Optimize existing criteria for better recruitment."""
    
    def __init__(self):
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> List[Dict]:
        """Load optimization rules and strategies."""
        return [
            {
                "issue": "narrow_age_range",
                "pattern": ["age", "18-65", "18-70"],
                "suggestion": "Consider widening upper age limit to 75-80 if safety profile allows",
                "impact": "medium",
                "risk": "low"
            },
            {
                "issue": "restrictive_hb1ac",
                "pattern": ["hba1c", "7.0", "11.0"],
                "suggestion": "HbA1c 7.0-11.0% may be restrictive; consider 7.5-10.5%",
                "impact": "high",
                "risk": "low"
            },
            {
                "issue": "strict_egfr",
                "pattern": ["egfr", "> 60", ">= 60"],
                "suggestion": "Consider eGFR > 30 or > 45 mL/min if renal elimination is not major pathway",
                "impact": "medium",
                "risk": "medium"
            },
            {
                "issue": "long_washout",
                "pattern": ["washout", "4 weeks", "8 weeks"],
                "suggestion": "Evaluate if shorter washout period is acceptable based on drug half-life",
                "impact": "medium",
                "risk": "low"
            },
            {
                "issue": "concomitant_restrictions",
                "pattern": ["no concomitant", "prohibited medications"],
                "suggestion": "Review if all prohibited medications are truly contraindicated",
                "impact": "high",
                "risk": "medium"
            }
        ]
    
    def optimize(self, criteria: Dict[str, Any], 
                 enrollment_target: int,
                 current_enrollment: int,
                 retention_rate: float = 0.85) -> Dict[str, Any]:
        """Optimize criteria to improve enrollment."""
        
        optimized_inclusion = []
        optimized_exclusion = []
        optimization_notes = []
        
        enrollment_gap = enrollment_target - current_enrollment
        enrollment_rate = current_enrollment / enrollment_target if enrollment_target > 0 else 0
        
        # Determine optimization intensity based on enrollment gap
        if enrollment_rate < 0.5:
            optimization_level = "aggressive"
        elif enrollment_rate < 0.75:
            optimization_level = "moderate"
        else:
            optimization_level = "minimal"
        
        # Process inclusion criteria
        for criterion in criteria.get("inclusion_criteria", []):
            opt_crit = self._optimize_criterion(criterion, optimization_level, "inclusion")
            optimized_inclusion.append(opt_crit)
            if opt_crit.get("modified"):
                optimization_notes.append(f"Modified I{criterion['id']}: {opt_crit.get('modification_note', '')}")
        
        # Process exclusion criteria
        for criterion in criteria.get("exclusion_criteria", []):
            opt_crit = self._optimize_criterion(criterion, optimization_level, "exclusion")
            optimized_exclusion.append(opt_crit)
            if opt_crit.get("modified"):
                optimization_notes.append(f"Modified E{criterion['id']}: {opt_crit.get('modification_note', '')}")
        
        # Calculate improved metrics
        new_complexity = self._calculate_complexity(optimized_inclusion, optimized_exclusion)
        
        return {
            "inclusion_criteria": [{k: v for k, v in c.items() if k != "modified" and k != "modification_note"} 
                                   for c in optimized_inclusion],
            "exclusion_criteria": [{k: v for k, v in c.items() if k != "modified" and k != "modification_note"} 
                                   for c in optimized_exclusion],
            "optimization_summary": {
                "optimization_level": optimization_level,
                "enrollment_gap": enrollment_gap,
                "original_criteria_count": len(criteria.get("inclusion_criteria", [])) + len(criteria.get("exclusion_criteria", [])),
                "optimized_criteria_count": len(optimized_inclusion) + len(optimized_exclusion),
                "modifications_made": len(optimization_notes)
            },
            "optimization_notes": optimization_notes,
            "projected_improvements": {
                "screen_success_rate_improvement": "+15-25%" if optimization_level == "aggressive" else "+5-15%",
                "estimated_new_screen_success": "0.45-0.55" if optimization_level == "aggressive" else "0.35-0.45",
                "retention_impact": "Monitor for any impact on retention"
            },
            "recommendations": self._generate_recommendations(optimization_level, enrollment_gap)
        }
    
    def _optimize_criterion(self, criterion: Dict, level: str, crit_type: str) -> Dict:
        """Apply optimization rules to a single criterion."""
        optimized = criterion.copy()
        text = criterion.get("criterion", "").lower()
        
        # Check against optimization rules
        for rule in self.optimization_rules:
            if any(pattern.lower() in text for pattern in rule["pattern"]):
                if level == "aggressive" or (level == "moderate" and rule["risk"] == "low"):
                    optimized["flexibility"] = rule["suggestion"]
                    optimized["modified"] = True
                    optimized["modification_note"] = rule["suggestion"]
                    
                    # Apply specific modifications
                    if rule["issue"] == "narrow_age_range" and "65" in text:
                        optimized["criterion"] = criterion["criterion"].replace("65", "75")
                    elif rule["issue"] == "restrictive_hb1ac":
                        optimized["criterion"] = text.replace("7.0", "7.5").replace("11.0", "10.5")
        
        return optimized
    
    def _generate_recommendations(self, level: str, gap: int) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if level == "aggressive":
            recommendations.extend([
                "Consider protocol amendment to widen key eligibility criteria",
                "Evaluate regional differences in eligibility - some criteria may vary by country",
                "Consider adaptive enrichment design to include broader population",
                "Implement central eligibility review to ensure consistent application"
            ])
        elif level == "moderate":
            recommendations.extend([
                "Monitor enrollment by criterion to identify specific barriers",
                "Consider eligibility waiver process for minor deviations",
                "Expand recruitment to additional sites if criteria cannot be relaxed"
            ])
        else:
            recommendations.extend([
                "Continue current approach with close monitoring",
                "Consider patient engagement strategies to improve enrollment"
            ])
        
        return recommendations
    
    def analyze_complexity(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze criteria complexity and identify issues."""
        inclusion = criteria.get("inclusion_criteria", [])
        exclusion = criteria.get("exclusion_criteria", [])
        
        total = len(inclusion) + len(exclusion)
        
        # Categorize criteria
        categories = {}
        for c in inclusion + exclusion:
            cat = c.get("category", "uncategorized")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Identify potential issues
        issues = []
        
        if total > 25:
            issues.append({
                "severity": "high",
                "issue": "Excessive criteria count",
                "description": f"{total} total criteria may create enrollment barriers",
                "recommendation": "Consolidate related criteria or remove non-essential items"
            })
        
        # Check for subjective criteria
        subjective_terms = ["significant", "severe", "clinically meaningful", "in the opinion of"]
        subjective_count = sum(
            1 for c in inclusion + exclusion 
            if any(term in c.get("criterion", "").lower() for term in subjective_terms)
        )
        
        if subjective_count > 3:
            issues.append({
                "severity": "medium",
                "issue": "Subjective criteria detected",
                "description": f"{subjective_count} criteria contain subjective language",
                "recommendation": "Provide objective definitions or scoring systems"
            })
        
        # Check for laboratory burden
        lab_criteria = categories.get("laboratory", 0)
        if lab_criteria > 5:
            issues.append({
                "severity": "medium",
                "issue": "High laboratory burden",
                "description": f"{lab_criteria} laboratory criteria may increase screen failures",
                "recommendation": "Review if all laboratory parameters are essential"
            })
        
        return {
            "complexity_score": {
                "total_criteria": total,
                "complexity_level": "high" if total > 20 else "medium" if total > 10 else "low",
                "category_distribution": categories
            },
            "issues_identified": issues,
            "assessment": "Criteria set requires optimization" if issues else "Criteria set appears reasonable"
        }
    
    def _calculate_complexity(self, inclusion: List[Dict], exclusion: List[Dict]) -> Dict:
        """Calculate complexity metrics."""
        total = len(inclusion) + len(exclusion)
        categories = {}
        for c in inclusion + exclusion:
            cat = c.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_criteria": total,
            "inclusion_count": len(inclusion),
            "exclusion_count": len(exclusion),
            "category_distribution": categories,
            "complexity_level": "high" if total > 20 else "medium" if total > 10 else "low"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Generate and optimize clinical trial inclusion/exclusion criteria"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate criteria from study design")
    gen_parser.add_argument("--indication", required=True, help="Therapeutic indication")
    gen_parser.add_argument("--phase", required=True, help="Study phase (Phase 1-4)")
    gen_parser.add_argument("--population", default="adults", help="Target population")
    gen_parser.add_argument("--duration", default="", help="Study duration")
    gen_parser.add_argument("--output", required=True, help="Output file path")
    gen_parser.add_argument("--age-min", type=int, default=18, help="Minimum age")
    gen_parser.add_argument("--age-max", type=int, default=75, help="Maximum age")
    
    # Optimize command
    opt_parser = subparsers.add_parser("optimize", help="Optimize existing criteria")
    opt_parser.add_argument("--input", required=True, help="Input criteria JSON file")
    opt_parser.add_argument("--enrollment-target", type=int, required=True, help="Target enrollment")
    opt_parser.add_argument("--current-enrollment", type=int, required=True, help="Current enrollment")
    opt_parser.add_argument("--output", required=True, help="Output file path")
    
    # Analyze command
    ana_parser = subparsers.add_parser("analyze", help="Analyze criteria complexity")
    ana_parser.add_argument("--input", required=True, help="Input criteria JSON file")
    ana_parser.add_argument("--output", required=True, help="Output file path")
    
    # Benchmark command (placeholder)
    ben_parser = subparsers.add_parser("benchmark", help="Compare with competitor trials")
    ben_parser.add_argument("--input", required=True, help="Input criteria JSON file")
    ben_parser.add_argument("--condition", required=True, help="Medical condition")
    ben_parser.add_argument("--output", required=True, help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "generate":
            design = StudyDesign(
                indication=args.indication,
                phase=args.phase,
                population=args.population,
                study_duration=args.duration,
                age_range={"min": args.age_min, "max": args.age_max}
            )
            generator = CriteriaGenerator()
            result = generator.generate(design)
            
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Generated criteria saved to {args.output}")
            print(f"Estimated screen success rate: {result['recruitment_metrics']['estimated_screen_success_rate']}")
            
        elif args.command == "optimize":
            with open(args.input, 'r') as f:
                criteria = json.load(f)
            
            optimizer = CriteriaOptimizer()
            result = optimizer.optimize(
                criteria,
                enrollment_target=args.enrollment_target,
                current_enrollment=args.current_enrollment
            )
            
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Optimized criteria saved to {args.output}")
            print(f"Modifications made: {result['optimization_summary']['modifications_made']}")
            print(f"Optimization level: {result['optimization_summary']['optimization_level']}")
            
        elif args.command == "analyze":
            with open(args.input, 'r') as f:
                criteria = json.load(f)
            
            optimizer = CriteriaOptimizer()
            result = optimizer.analyze_complexity(criteria)
            
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Analysis saved to {args.output}")
            print(f"Complexity level: {result['complexity_score']['complexity_level']}")
            print(f"Issues found: {len(result['issues_identified'])}")
            
        elif args.command == "benchmark":
            # Placeholder for benchmark functionality
            with open(args.input, 'r') as f:
                criteria = json.load(f)
            
            result = {
                "note": "Benchmark functionality requires ClinicalTrials.gov API integration",
                "input_criteria": criteria.get("study_design", {}),
                "condition": args.condition,
                "recommendation": "Use clinicaltrials-gov-parser skill to fetch competitor trials"
            }
            
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Benchmark report saved to {args.output}")
            print("Note: Full benchmarking requires ClinicalTrials.gov API integration")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
