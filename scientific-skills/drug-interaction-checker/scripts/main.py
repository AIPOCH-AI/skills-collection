#!/usr/bin/env python3
"""
Drug Interaction Checker

Checks for drug-drug interactions between multiple medications.
Provides severity classification, mechanism explanations, and clinical recommendations.

Usage:
    python main.py --drugs "Drug1" "Drug2" "Drug3"
    python main.py --drugs "Warfarin" "Aspirin" --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class SeverityLevel(Enum):
    """Interaction severity levels"""
    CRITICAL = "Critical"
    MAJOR = "Major"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


@dataclass
class DrugInteraction:
    """Represents a single drug interaction"""
    drug_a: str
    drug_b: str
    severity: SeverityLevel
    mechanism: str
    effect: str
    recommendation: str
    evidence_level: str = "Established"


@dataclass
class InteractionResult:
    """Complete interaction check result"""
    drugs_checked: List[str]
    interactions: List[DrugInteraction]
    summary: Dict[str, int]
    warnings: List[str]


class DrugInteractionChecker:
    """Main class for checking drug interactions"""
    
    # CYP450 metabolic pathways - common substrates, inhibitors, inducers
    CYP450_DATA = {
        "CYP3A4": {
            "substrates": ["simvastatin", "atorvastatin", "lovastatin", "amlodipine", "nifedipine", 
                          "diltiazem", "verapamil", "cyclosporine", "tacrolimus", "midazolam",
                          "triazolam", "alprazolam", "sildenafil", "warfarin", "quinidine"],
            "inhibitors": ["ketoconazole", "itraconazole", "fluconazole", "clarithromycin", 
                          "erythromycin", "ritonavir", "grapefruit"],
            "inducers": ["rifampin", "rifampicin", "carbamazepine", "phenytoin", "phenobarbital", 
                        "st_johns_wort", "efavirenz"]
        },
        "CYP2C9": {
            "substrates": ["warfarin", "phenytoin", "tolbutamide", "losartan", "irbesartan",
                          "celecoxib", "flurbiprofen", "glipizide", "glyburide"],
            "inhibitors": ["fluconazole", "amiodarone", "miconazole", "voriconazole"],
            "inducers": ["rifampin", "carbamazepine", "phenobarbital", "secobarbital"]
        },
        "CYP2C19": {
            "substrates": ["omeprazole", "lansoprazole", "pantoprazole", "clopidogrel", 
                          "diazepam", "phenytoin", "propranolol", "warfarin"],
            "inhibitors": ["omeprazole", "fluconazole", "fluvoxamine", "ticlopidine"],
            "inducers": ["rifampin", "carbamazepine"]
        },
        "CYP2D6": {
            "substrates": ["metoprolol", "propranolol", "codeine", "tramadol", "dextromethorphan",
                          "haloperidol", "risperidone", "paroxetine", "fluoxetine", "tamoxifen"],
            "inhibitors": ["fluoxetine", "paroxetine", "quinidine", "bupropion"],
            "inducers": ["rifampin"]
        },
        "CYP1A2": {
            "substrates": ["caffeine", "theophylline", "tizanidine", "clozapine", "olanzapine",
                          "fluvoxamine"],
            "inhibitors": ["fluvoxamine", "ciprofloxacin", "cimetidine"],
            "inducers": ["smoking", "chargrilled_food", "rifampin", "carbamazepine"]
        }
    }
    
    # Known direct drug interactions
    DIRECT_INTERACTIONS = {
        ("warfarin", "aspirin"): {
            "severity": SeverityLevel.CRITICAL,
            "mechanism": "Pharmacodynamic synergism - both affect hemostasis",
            "effect": "Significantly increased bleeding risk (GI, intracranial)",
            "recommendation": "Avoid combination unless absolutely necessary; monitor INR and for bleeding"
        },
        ("warfarin", "ibuprofen"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Pharmacodynamic synergism + displacement from protein binding",
            "effect": "Increased bleeding risk, potential GI ulceration",
            "recommendation": "Avoid NSAIDs; use acetaminophen for pain if possible"
        },
        ("warfarin", "amiodarone"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "CYP2C9 inhibition + CYP1A2/CYP3A4 inhibition",
            "effect": "Increased warfarin plasma levels, increased INR",
            "recommendation": "Reduce warfarin dose by 30-50% when starting amiodarone"
        },
        ("simvastatin", "amlodipine"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "CYP3A4 inhibition by amlodipine",
            "effect": "Increased simvastatin levels, increased myopathy/rhabdomyolysis risk",
            "recommendation": "Limit simvastatin to 20mg/day when combined with amlodipine"
        },
        ("simvastatin", "atorvastatin"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Additive effect - both are statins",
            "effect": "Increased risk of myopathy, rhabdomyolysis, liver toxicity",
            "recommendation": "Never combine two statins"
        },
        ("metformin", "contrast_media"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Reduced renal clearance + potential nephrotoxicity",
            "effect": "Risk of lactic acidosis, especially with impaired renal function",
            "recommendation": "Hold metformin 48 hours before/after contrast administration"
        },
        ("aspirin", "ibuprofen"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Pharmacodynamic antagonism - ibuprofen blocks aspirin antiplatelet effect",
            "effect": "Reduced cardioprotective effect of aspirin",
            "recommendation": "If both needed, take aspirin 2 hours before or 8 hours after ibuprofen"
        },
        ("lisinopril", "spironolactone"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Dual blockade of RAAS + potassium retention",
            "effect": "Hyperkalemia risk, especially with renal impairment",
            "recommendation": "Monitor potassium closely; avoid in severe renal dysfunction"
        },
        ("lisinopril", "potassium_supplement"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "ACE inhibitors reduce potassium excretion",
            "effect": "Hyperkalemia",
            "recommendation": "Monitor potassium levels, especially with renal impairment"
        },
        ("digoxin", "amiodarone"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Reduced digoxin clearance + displacement from tissue binding",
            "effect": "Increased digoxin levels, toxicity risk (arrhythmias, nausea)",
            "recommendation": "Reduce digoxin dose by 50% when starting amiodarone; monitor levels"
        },
        ("digoxin", "furosemide"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Hypokalemia potentiates digoxin toxicity",
            "effect": "Increased risk of digoxin toxicity (arrhythmias)",
            "recommendation": "Monitor potassium and digoxin levels"
        },
        ("theophylline", "ciprofloxacin"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "CYP1A2 inhibition",
            "effect": "Increased theophylline levels, toxicity (seizures, arrhythmias)",
            "recommendation": "Reduce theophylline dose; monitor levels"
        },
        ("clopidogrel", "omeprazole"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "CYP2C19 inhibition reduces clopidogrel activation",
            "effect": "Reduced antiplatelet effect, increased cardiovascular event risk",
            "recommendation": "Use pantoprazole instead (less CYP2C19 inhibition)"
        },
        ("methotrexate", "ibuprofen"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Reduced renal clearance of methotrexate",
            "effect": "Increased methotrexate toxicity (bone marrow suppression, mucositis)",
            "recommendation": "Avoid NSAIDs with high-dose methotrexate"
        },
        ("lithium", "furosemide"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Reduced lithium clearance",
            "effect": "Increased lithium levels, toxicity (tremor, confusion, seizures)",
            "recommendation": "Monitor lithium levels closely; consider alternative diuretic"
        },
        ("lithium", "ibuprofen"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Reduced lithium clearance via prostaglandin inhibition",
            "effect": "Increased lithium levels, toxicity",
            "recommendation": "Avoid combination or monitor lithium levels frequently"
        },
        ("tramadol", "fluoxetine"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Serotonin syndrome risk (serotonergic agents)",
            "effect": "Agitation, confusion, tachycardia, hyperthermia, clonus",
            "recommendation": "Use with caution; monitor for serotonin syndrome symptoms"
        },
        ("tramadol", "trazodone"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Additive serotonergic effect",
            "effect": "Serotonin syndrome risk",
            "recommendation": "Monitor for serotonin syndrome; consider alternative analgesic"
        },
        ("tramadol", "amitriptyline"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "CYP2D6 inhibition + additive CNS depression",
            "effect": "Increased tramadol levels, enhanced sedation",
            "recommendation": "Monitor for excessive sedation; consider dose adjustment"
        },
        ("alcohol", "metformin"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Increased risk of lactic acidosis + potentiation of hypoglycemia",
            "effect": "Lactic acidosis, hypoglycemia unawareness",
            "recommendation": "Limit alcohol intake; avoid binge drinking"
        },
        ("alcohol", "warfarin"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Variable effect on metabolism + hepatic enzyme induction",
            "effect": "Unpredictable INR changes",
            "recommendation": "Limit alcohol; maintain consistent intake if used"
        },
        ("aspirin", "alcohol"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Additive gastric irritation + bleeding risk",
            "effect": "Increased GI bleeding risk, gastric ulceration",
            "recommendation": "Avoid or limit alcohol; take aspirin with food"
        }
    }
    
    # Drug class interactions
    CLASS_INTERACTIONS = {
        ("warfarin", "nsaid"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Pharmacodynamic synergism + GI mucosal damage",
            "effect": "Increased bleeding risk, GI ulceration/perforation",
            "recommendation": "Avoid NSAIDs; use acetaminophen or COX-2 inhibitors with caution"
        },
        ("ace_inhibitor", "arb"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Dual RAAS blockade",
            "effect": "Hyperkalemia, hypotension, renal impairment",
            "recommendation": "Avoid routine combination; monitor renal function and potassium"
        },
        ("ace_inhibitor", "potassium_sparing_diuretic"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Additive potassium retention",
            "effect": "Hyperkalemia",
            "recommendation": "Monitor potassium levels within 1 week of starting combination"
        },
        ("ssri", "triptan"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Additive serotonergic effect",
            "effect": "Serotonin syndrome (rare but serious)",
            "recommendation": "Use lowest effective doses; monitor for serotonin syndrome"
        },
        ("ssri", "nsaid"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Impaired platelet function (SSRIs reduce serotonin uptake by platelets)",
            "effect": "Increased bleeding risk",
            "recommendation": "Monitor for bleeding; use PPI if GI risk factors present"
        },
        ("opioid", "benzodiazepine"): {
            "severity": SeverityLevel.CRITICAL,
            "mechanism": "Additive CNS and respiratory depression",
            "effect": "Profound sedation, respiratory depression, death",
            "recommendation": "Avoid combination if possible; if used together, limit dose/duration, monitor"
        },
        ("statin", "fibrate"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Additive myotoxicity",
            "effect": "Increased risk of myopathy, rhabdomyolysis",
            "recommendation": "Use fenofibrate preferentially; avoid gemfibrozil; monitor CK"
        },
        ("statin", "azole_antifungal"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "CYP3A4 inhibition (for simvastatin, atorvastatin)",
            "effect": "Increased statin levels, myopathy risk",
            "recommendation": "Hold statin during azole therapy or use pravastatin/rosuvastatin"
        },
        ("diuretic", "nsaid"): {
            "severity": SeverityLevel.MODERATE,
            "mechanism": "Reduced diuretic/natriuretic effect, renal function impairment",
            "effect": "Antihypertensive effect reduced, fluid retention, AKI",
            "recommendation": "Monitor BP, renal function; use lowest NSAID dose short-term"
        },
        ("anticoagulant", "antiplatelet"): {
            "severity": SeverityLevel.MAJOR,
            "mechanism": "Additive effect on hemostasis",
            "effect": "Significantly increased bleeding risk",
            "recommendation": "Combination only when benefit outweighs risk; close monitoring"
        }
    }
    
    DRUG_CLASS_MAPPING = {
        # NSAIDs
        "ibuprofen": "nsaid", "naproxen": "nsaid", "diclofenac": "nsaid",
        "celecoxib": "nsaid", "meloxicam": "nsaid", "ketorolac": "nsaid",
        "indomethacin": "nsaid", "piroxicam": "nsaid",
        # ACE inhibitors
        "lisinopril": "ace_inhibitor", "enalapril": "ace_inhibitor",
        "captopril": "ace_inhibitor", "ramipril": "ace_inhibitor",
        "perindopril": "ace_inhibitor", "benazepril": "ace_inhibitor",
        # ARBs
        "losartan": "arb", "valsartan": "arb", "irbesartan": "arb",
        "candesartan": "arb", "olmesartan": "arb", "telmisartan": "arb",
        # Statins
        "simvastatin": "statin", "atorvastatin": "statin", "rosuvastatin": "statin",
        "pravastatin": "statin", "fluvastatin": "statin", "lovastatin": "statin",
        "pitavastatin": "statin",
        # SSRIs
        "fluoxetine": "ssri", "sertraline": "ssri", "paroxetine": "ssri",
        "citalopram": "ssri", "escitalopram": "ssri", "fluvoxamine": "ssri",
        # Opioids
        "morphine": "opioid", "codeine": "opioid", "oxycodone": "opioid",
        "hydrocodone": "opioid", "tramadol": "opioid", "fentanyl": "opioid",
        # Benzodiazepines
        "alprazolam": "benzodiazepine", "diazepam": "benzodiazepine",
        "lorazepam": "benzodiazepine", "clonazepam": "benzodiazepine",
        "temazepam": "benzodiazepine", "midazolam": "benzodiazepine",
        # Potassium sparing diuretics
        "spironolactone": "potassium_sparing_diuretic", "eplerenone": "potassium_sparing_diuretic",
        "triamterene": "potassium_sparing_diuretic", "amiloride": "potassium_sparing_diuretic",
        # Azole antifungals
        "ketoconazole": "azole_antifungal", "fluconazole": "azole_antifungal",
        "itraconazole": "azole_antifungal", "voriconazole": "azole_antifungal",
        "posaconazole": "azole_antifungal",
        # Triptans
        "sumatriptan": "triptan", "rizatriptan": "triptan", "zolmitriptan": "triptan",
        "eletriptan": "triptan", "almotriptan": "triptan", "frovatriptan": "triptan",
        # Anticoagulants
        "warfarin": "anticoagulant", "rivaroxaban": "anticoagulant",
        "apixaban": "anticoagulant", "dabigatran": "anticoagulant",
        "edoxaban": "anticoagulant", "heparin": "anticoagulant",
        # Antiplatelets
        "aspirin": "antiplatelet", "clopidogrel": "antiplatelet",
        "prasugrel": "antiplatelet", "ticagrelor": "antiplatelet",
    }
    
    def __init__(self):
        self.warnings = []
    
    def normalize_drug_name(self, name: str) -> str:
        """Normalize drug name for matching"""
        return name.lower().strip().replace(" ", "_").replace("-", "_")
    
    def get_drug_class(self, drug: str) -> Optional[str]:
        """Get drug class if known"""
        normalized = self.normalize_drug_name(drug)
        return self.DRUG_CLASS_MAPPING.get(normalized)
    
    def check_cyp450_interactions(self, drug_a: str, drug_b: str) -> Optional[DrugInteraction]:
        """Check for CYP450 metabolic interactions"""
        norm_a = self.normalize_drug_name(drug_a)
        norm_b = self.normalize_drug_name(drug_b)
        
        for enzyme, data in self.CYP450_DATA.items():
            substrates = [s.lower() for s in data["substrates"]]
            inhibitors = [i.lower() for i in data["inhibitors"]]
            inducers = [i.lower() for i in data["inducers"]]
            
            # Check if A is substrate and B is inhibitor/inducer
            if norm_a in substrates:
                if norm_b in inhibitors:
                    return DrugInteraction(
                        drug_a=drug_a,
                        drug_b=drug_b,
                        severity=SeverityLevel.MODERATE,
                        mechanism=f"{enzyme} inhibition - {drug_b} inhibits metabolism of {drug_a}",
                        effect=f"Increased {drug_a} plasma levels",
                        recommendation=f"Monitor for {drug_a} toxicity; consider dose reduction"
                    )
                elif norm_b in inducers:
                    return DrugInteraction(
                        drug_a=drug_a,
                        drug_b=drug_b,
                        severity=SeverityLevel.MODERATE,
                        mechanism=f"{enzyme} induction - {drug_b} increases metabolism of {drug_a}",
                        effect=f"Reduced {drug_a} efficacy",
                        recommendation=f"Monitor therapeutic effect; may need dose increase"
                    )
            
            # Check reverse: B is substrate and A is inhibitor/inducer
            if norm_b in substrates:
                if norm_a in inhibitors:
                    return DrugInteraction(
                        drug_a=drug_a,
                        drug_b=drug_b,
                        severity=SeverityLevel.MODERATE,
                        mechanism=f"{enzyme} inhibition - {drug_a} inhibits metabolism of {drug_b}",
                        effect=f"Increased {drug_b} plasma levels",
                        recommendation=f"Monitor for {drug_b} toxicity; consider dose reduction"
                    )
                elif norm_a in inducers:
                    return DrugInteraction(
                        drug_a=drug_a,
                        drug_b=drug_b,
                        severity=SeverityLevel.MODERATE,
                        mechanism=f"{enzyme} induction - {drug_a} increases metabolism of {drug_b}",
                        effect=f"Reduced {drug_b} efficacy",
                        recommendation=f"Monitor therapeutic effect; may need dose increase"
                    )
        
        return None
    
    def check_direct_interaction(self, drug_a: str, drug_b: str) -> Optional[DrugInteraction]:
        """Check for known direct drug interactions"""
        norm_a = self.normalize_drug_name(drug_a)
        norm_b = self.normalize_drug_name(drug_b)
        
        # Try both orderings
        key = (norm_a, norm_b)
        reverse_key = (norm_b, norm_a)
        
        data = None
        if key in self.DIRECT_INTERACTIONS:
            data = self.DIRECT_INTERACTIONS[key]
        elif reverse_key in self.DIRECT_INTERACTIONS:
            data = self.DIRECT_INTERACTIONS[reverse_key]
        
        if data:
            return DrugInteraction(
                drug_a=drug_a,
                drug_b=drug_b,
                severity=data["severity"],
                mechanism=data["mechanism"],
                effect=data["effect"],
                recommendation=data["recommendation"]
            )
        
        return None
    
    def check_class_interactions(self, drug_a: str, drug_b: str) -> Optional[DrugInteraction]:
        """Check for class-based interactions"""
        class_a = self.get_drug_class(drug_a)
        class_b = self.get_drug_class(drug_b)
        
        if not class_a and not class_b:
            return None
        
        norm_a = self.normalize_drug_name(drug_a)
        norm_b = self.normalize_drug_name(drug_b)
        
        # Check all combinations
        combinations = []
        if class_a:
            combinations.append((class_a, norm_b))
        if class_b:
            combinations.append((norm_a, class_b))
        if class_a and class_b:
            combinations.append((class_a, class_b))
        
        for combo in combinations:
            reverse_combo = (combo[1], combo[0])
            
            data = None
            if combo in self.CLASS_INTERACTIONS:
                data = self.CLASS_INTERACTIONS[combo]
            elif reverse_combo in self.CLASS_INTERACTIONS:
                data = self.CLASS_INTERACTIONS[reverse_combo]
            
            if data:
                return DrugInteraction(
                    drug_a=drug_a,
                    drug_b=drug_b,
                    severity=data["severity"],
                    mechanism=data["mechanism"],
                    effect=data["effect"],
                    recommendation=data["recommendation"]
                )
        
        return None
    
    def check_interaction(self, drug_a: str, drug_b: str) -> Optional[DrugInteraction]:
        """Check for any interaction between two drugs"""
        # Priority: Direct > Class > CYP450
        
        direct = self.check_direct_interaction(drug_a, drug_b)
        if direct:
            return direct
        
        class_int = self.check_class_interactions(drug_a, drug_b)
        if class_int:
            return class_int
        
        cyp450 = self.check_cyp450_interactions(drug_a, drug_b)
        if cyp450:
            return cyp450
        
        return None
    
    def check_all_interactions(self, drugs: List[str]) -> InteractionResult:
        """Check all pairwise interactions in a drug list"""
        self.warnings = []
        
        if len(drugs) < 2:
            self.warnings.append("At least 2 drugs required for interaction check")
            return InteractionResult(
                drugs_checked=drugs,
                interactions=[],
                summary={"critical": 0, "major": 0, "moderate": 0, "minor": 0, "unknown": 0},
                warnings=self.warnings
            )
        
        interactions = []
        severity_count = {"critical": 0, "major": 0, "moderate": 0, "minor": 0, "unknown": 0}
        
        # Check all pairs
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                interaction = self.check_interaction(drugs[i], drugs[j])
                if interaction:
                    interactions.append(interaction)
                    severity_key = interaction.severity.value.lower()
                    severity_count[severity_key] = severity_count.get(severity_key, 0) + 1
        
        # Check for duplicate classes (same class warnings)
        class_counts = {}
        for drug in drugs:
            drug_class = self.get_drug_class(drug)
            if drug_class:
                class_counts[drug_class] = class_counts.get(drug_class, 0) + 1
        
        for drug_class, count in class_counts.items():
            if count > 1:
                self.warnings.append(f"Multiple drugs from same class detected: {drug_class} ({count} drugs)")
        
        return InteractionResult(
            drugs_checked=drugs,
            interactions=interactions,
            summary=severity_count,
            warnings=self.warnings
        )


def format_output(result: InteractionResult, output_format: str = "text") -> str:
    """Format the interaction result for display"""
    
    if output_format == "json":
        # Convert to JSON-serializable dict
        result_dict = {
            "drugs_checked": result.drugs_checked,
            "interactions": [
                {
                    "drug_pair": [i.drug_a, i.drug_b],
                    "severity": i.severity.value,
                    "mechanism": i.mechanism,
                    "effect": i.effect,
                    "recommendation": i.recommendation
                }
                for i in result.interactions
            ],
            "summary": result.summary,
            "warnings": result.warnings
        }
        return json.dumps(result_dict, indent=2, ensure_ascii=False)
    
    # Text format
    lines = []
    lines.append("=" * 60)
    lines.append("DRUG INTERACTION CHECK RESULTS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Drugs checked: {', '.join(result.drugs_checked)}")
    lines.append("")
    
    # Summary
    lines.append("-" * 40)
    lines.append("SEVERITY SUMMARY")
    lines.append("-" * 40)
    for severity, count in result.summary.items():
        if count > 0:
            lines.append(f"  {severity.upper()}: {count}")
    total = sum(result.summary.values())
    lines.append(f"  Total interactions found: {total}")
    lines.append("")
    
    # Warnings
    if result.warnings:
        lines.append("-" * 40)
        lines.append("WARNINGS")
        lines.append("-" * 40)
        for warning in result.warnings:
            lines.append(f"  ⚠️  {warning}")
        lines.append("")
    
    # Detailed interactions
    if result.interactions:
        lines.append("-" * 40)
        lines.append("DETAILED INTERACTIONS")
        lines.append("-" * 40)
        lines.append("")
        
        # Sort by severity
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.MAJOR: 1,
            SeverityLevel.MODERATE: 2,
            SeverityLevel.MINOR: 3,
            SeverityLevel.UNKNOWN: 4
        }
        sorted_interactions = sorted(result.interactions, key=lambda x: severity_order[x.severity])
        
        for i, interaction in enumerate(sorted_interactions, 1):
            severity_icon = {
                SeverityLevel.CRITICAL: "🔴",
                SeverityLevel.MAJOR: "🟠",
                SeverityLevel.MODERATE: "🟡",
                SeverityLevel.MINOR: "🟢",
                SeverityLevel.UNKNOWN: "⚪"
            }
            
            lines.append(f"{i}. {severity_icon.get(interaction.severity, '⚪')} {interaction.drug_a} + {interaction.drug_b}")
            lines.append(f"   Severity: {interaction.severity.value}")
            lines.append(f"   Mechanism: {interaction.mechanism}")
            lines.append(f"   Effect: {interaction.effect}")
            lines.append(f"   Recommendation: {interaction.recommendation}")
            lines.append("")
    else:
        lines.append("-" * 40)
        lines.append("No known interactions found between these drugs.")
        lines.append("-" * 40)
        lines.append("")
    
    # Disclaimer
    lines.append("=" * 60)
    lines.append("DISCLAIMER")
    lines.append("=" * 60)
    lines.append("This tool provides information for educational purposes only.")
    lines.append("Always consult a healthcare professional or pharmacist before")
    lines.append("making medication decisions. This is not medical advice.")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def check_interactions(drugs: List[str]) -> dict:
    """
    Main function to check drug interactions.
    Returns a dictionary with results.
    """
    checker = DrugInteractionChecker()
    result = checker.check_all_interactions(drugs)
    
    return {
        "drugs_checked": result.drugs_checked,
        "interactions": [
            {
                "drug_pair": [i.drug_a, i.drug_b],
                "severity": i.severity.value,
                "mechanism": i.mechanism,
                "effect": i.effect,
                "recommendation": i.recommendation
            }
            for i in result.interactions
        ],
        "summary": result.summary,
        "warnings": result.warnings
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check for drug-drug interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --drugs "Warfarin" "Aspirin"
    python main.py --drugs "Metformin" "Simvastatin" "Amlodipine" --format json
        """
    )
    parser.add_argument(
        "--drugs", "-d",
        nargs="+",
        required=True,
        help="List of drug names to check"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    args = parser.parse_args()
    
    # Check interactions
    checker = DrugInteractionChecker()
    result = checker.check_all_interactions(args.drugs)
    
    # Output results
    output = format_output(result, args.format)
    print(output)
    
    # Exit with error code if critical interactions found
    if result.summary.get("critical", 0) > 0:
        sys.exit(2)
    elif result.summary.get("major", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
