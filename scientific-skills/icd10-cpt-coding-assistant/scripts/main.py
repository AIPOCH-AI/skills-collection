#!/usr/bin/env python3
"""
ICD-10 & CPT Coding Assistant

Parses clinical notes and recommends diagnosis and procedure codes
with confidence scoring.

Usage:
    python main.py --input clinical_note.txt [--format json|text]
    python main.py --interactive
"""

import re
import json
import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys


@dataclass
class ICD10Code:
    """Represents an ICD-10 diagnosis code recommendation."""
    code: str
    description: str
    confidence: float
    evidence: List[str]
    alternatives: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CPTCode:
    """Represents a CPT procedure code recommendation."""
    code: str
    description: str
    confidence: float
    evidence: List[str]
    category: str  # E/M, Surgery, Radiology, etc.
    time: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CodingResult:
    """Complete coding analysis result."""
    icd10_codes: List[ICD10Code]
    cpt_codes: List[CPTCode]
    warnings: List[str]
    note_summary: str
    
    def to_dict(self) -> Dict:
        return {
            "icd10_codes": [c.to_dict() for c in self.icd10_codes],
            "cpt_codes": [c.to_dict() for c in self.cpt_codes],
            "warnings": self.warnings,
            "note_summary": self.note_summary
        }


class ClinicalNoteParser:
    """Parses clinical notes to extract relevant medical information."""
    
    def __init__(self):
        self.sections = {}
        
    def parse(self, text: str) -> Dict:
        """Parse clinical note into structured sections."""
        text = text.strip()
        
        # Try to identify SOAP sections
        sections = {
            "subjective": self._extract_section(text, ["SUBJECTIVE", "HPI", "History"]),
            "objective": self._extract_section(text, ["OBJECTIVE", "EXAM", "Physical Exam"]),
            "assessment": self._extract_section(text, ["ASSESSMENT", "DIAGNOSIS", "IMPRESSION"]),
            "plan": self._extract_section(text, ["PLAN", "TREATMENT PLAN"]),
            "full_text": text
        }
        
        # Extract symptoms, findings, and diagnoses
        return {
            "sections": sections,
            "symptoms": self._extract_symptoms(text),
            "diagnoses": self._extract_diagnoses(text),
            "procedures": self._extract_procedures(text),
            "vitals": self._extract_vitals(text),
            "medications": self._extract_medications(text)
        }
    
    def _extract_section(self, text: str, headers: List[str]) -> str:
        """Extract a section by its header."""
        for header in headers:
            pattern = rf'(?:^|\n)\s*{header}[:\s]*\n(.*?)(?=\n\s*(?:[A-Z/\s]+[:\s]*\n|$))'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract reported symptoms from text."""
        symptom_keywords = [
            r'\bpain\b', r'\bfever\b', r'\bcough\b', r'\bshortness of breath\b',
            r'\bfatigue\b', r'\bnausea\b', r'\bvomiting\b', r'\bdiarrhea\b',
            r'\bheadache\b', r'\bdizziness\b', r'\bchest pain\b', r'\babdominal pain\b',
            r'\bwheezing\b', r'\bcongestion\b', r'\bsore throat\b'
        ]
        
        found_symptoms = []
        for keyword in symptom_keywords:
            matches = re.finditer(keyword, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].strip()
                found_symptoms.append(context)
        
        return found_symptoms[:10]  # Limit to top 10
    
    def _extract_diagnoses(self, text: str) -> List[str]:
        """Extract diagnoses/assessments from text."""
        diagnoses = []
        
        # Look for diagnosis indicators
        patterns = [
            r'(?:diagnosis|assessment|impression|dx)[:\s]*([^\n]+)',
            r'\b([A-Z][a-z]+(?:\s+[a-z]+){0,5})\s*\(\s*ICD-?10\s*[:\s-]\s*([A-Z]\d{2}(?:\.\d{1,2})?)\s*\)',
            r'(?:chief complaint|cc)[:\s]*([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                diagnoses.append(match.group(1).strip())
        
        return list(set(diagnoses))  # Remove duplicates
    
    def _extract_procedures(self, text: str) -> List[str]:
        """Extract procedures/services mentioned."""
        procedure_indicators = [
            r'\b(performed|conducted|administered|ordered)\s+([a-z\s]+?)(?:\.|,)',
            r'\b(procedure|surgery|injection|vaccination)\b',
            r'office visit', r'consultation', r'follow.?up', r'physical exam'
        ]
        
        procedures = []
        for indicator in procedure_indicators:
            matches = re.finditer(indicator, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 40)
                procedures.append(text[start:end].strip())
        
        return list(set(procedures))
    
    def _extract_vitals(self, text: str) -> Dict[str, str]:
        """Extract vital signs."""
        vitals = {}
        
        vital_patterns = {
            "bp": r'(?:BP|blood pressure)[:\s]*(\d{2,3}/\d{2,3})',
            "hr": r'(?:HR|heart rate|pulse)[:\s]*(\d{2,3})',
            "temp": r'(?:temp|temperature)[:\s]*([\d.]+)',
            "rr": r'(?:RR|respiratory rate)[:\s]*(\d{1,2})',
            "spo2": r'(?:SpO2|O2 sat|oxygen saturation)[:\s]*([\d.]+)'
        }
        
        for key, pattern in vital_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vitals[key] = match.group(1)
        
        return vitals
    
    def _extract_medications(self, text: str) -> List[str]:
        """Extract medication mentions."""
        # Simple medication extraction
        med_pattern = r'\b([A-Z][a-z]+(?:\s+[a-z]+){0,2})\s+(\d+\s*(?:mg|mcg|g|ml|units?))'
        matches = re.finditer(med_pattern, text)
        return [f"{m.group(1)} {m.group(2)}" for m in matches]


class ICD10Recommender:
    """Recommends ICD-10 diagnosis codes based on clinical information."""
    
    def __init__(self):
        self.code_database = self._load_icd10_database()
    
    def _load_icd10_database(self) -> Dict:
        """Load common ICD-10 codes."""
        # Common codes by category
        return {
            "respiratory": {
                "J06.9": ("Upper respiratory infection, unspecified", ["cold", "uri", "upper respiratory"]),
                "J20.9": ("Acute bronchitis, unspecified", ["bronchitis", "cough", "wheezing"]),
                "J44.9": ("COPD, unspecified", ["copd", "emphysema", "chronic bronchitis"]),
                "J45.901": ("Asthma, unspecified", ["asthma", "wheezing"]),
                "J18.9": ("Pneumonia, unspecified organism", ["pneumonia", "infiltrate"]),
            },
            "cardiovascular": {
                "I10": ("Essential hypertension", ["hypertension", "htn", "high blood pressure"]),
                "I25.10": ("Atherosclerotic heart disease", ["cad", "coronary artery disease", "atherosclerosis"]),
                "I50.9": ("Heart failure, unspecified", ["chf", "heart failure", "congestive heart failure"]),
                "I48.91": ("Atrial fibrillation, unspecified", ["afib", "atrial fibrillation", "irregular heartbeat"]),
            },
            "gastrointestinal": {
                "K21.9": ("GERD without esophagitis", ["gerd", "acid reflux", "heartburn"]),
                "K29.70": ("Gastritis, unspecified", ["gastritis", "stomach inflammation"]),
                "K59.00": ("Constipation, unspecified", ["constipation"]),
                "K52.9": ("Gastroenteritis, unspecified", ["gastroenteritis", "stomach bug", "diarrhea"]),
            },
            "musculoskeletal": {
                "M25.561": ("Pain in right knee", ["knee pain", "right knee"]),
                "M25.562": ("Pain in left knee", ["knee pain", "left knee"]),
                "M54.5": ("Low back pain", ["back pain", "lower back", "lumbago"]),
                "M79.601": ("Pain in right arm", ["arm pain", "right arm"]),
                "M79.602": ("Pain in left arm", ["arm pain", "left arm"]),
            },
            "infectious": {
                "B34.9": ("Viral infection, unspecified", ["viral infection", "virus"]),
                "A99": ("Unspecified viral hemorrhagic fever", ["fever", "viral"]),
                "Z20.828": ("Contact with contagious disease", ["exposure", "contact"]),
            },
            "endocrine": {
                "E11.9": ("Type 2 diabetes without complications", ["diabetes", "dm2", "type 2 diabetes"]),
                "E10.9": ("Type 1 diabetes without complications", ["type 1 diabetes", "dm1", "juvenile diabetes"]),
                "E78.5": ("Hyperlipidemia, unspecified", ["hyperlipidemia", "high cholesterol", "dyslipidemia"]),
                "E03.9": ("Hypothyroidism, unspecified", ["hypothyroidism", "underactive thyroid"]),
            },
            "mental": {
                "F32.9": ("Major depressive disorder, single episode", ["depression", "depressed", "mdd"]),
                "F41.9": ("Anxiety disorder, unspecified", ["anxiety", "anxious", "gad"]),
                "F43.10": ("Post-traumatic stress disorder", ["ptsd", "post traumatic"]),
                "G47.9": ("Sleep disorder, unspecified", ["insomnia", "sleep disorder", "sleep disturbance"]),
            },
            "general": {
                "R50.9": ("Fever, unspecified", ["fever", "febrile", "pyrexia"]),
                "R05": ("Cough", ["cough"]),
                "R06.02": ("Shortness of breath", ["sob", "shortness of breath", "dyspnea"]),
                "R10.9": ("Unspecified abdominal pain", ["abdominal pain", "stomach pain", "belly pain"]),
                "R51": ("Headache", ["headache", "head pain"]),
                "R53.83": ("Fatigue", ["fatigue", "tired", "exhaustion"]),
                "Z00.00": ("Encounter for general adult medical exam", ["annual exam", "physical", "checkup"]),
            }
        }
    
    def recommend(self, parsed_note: Dict) -> List[ICD10Code]:
        """Generate ICD-10 code recommendations."""
        recommendations = []
        text = parsed_note["sections"]["full_text"].lower()
        
        # Score each potential code
        code_scores = []
        for category, codes in self.code_database.items():
            for code, (description, keywords) in codes.items():
                score, evidence = self._calculate_code_score(code, description, keywords, text, parsed_note)
                if score > 0.3:  # Minimum threshold
                    code_scores.append((code, description, score, evidence))
        
        # Sort by score and return top recommendations
        code_scores.sort(key=lambda x: x[2], reverse=True)
        
        for code, description, score, evidence in code_scores[:5]:
            # Find alternative codes in same category
            alternatives = self._find_alternatives(code)
            
            recommendations.append(ICD10Code(
                code=code,
                description=description,
                confidence=round(score, 2),
                evidence=evidence[:3],
                alternatives=alternatives
            ))
        
        return recommendations
    
    def _calculate_code_score(self, code: str, description: str, keywords: List[str], 
                              text: str, parsed_note: Dict) -> Tuple[float, List[str]]:
        """Calculate confidence score for a code match."""
        score = 0.0
        evidence = []
        
        # Check keywords in full text
        for keyword in keywords:
            if keyword.lower() in text:
                score += 0.3
                # Find the context
                pattern = r'.{0,30}' + re.escape(keyword) + r'.{0,30}'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in list(matches)[:1]:  # Just take first match
                    evidence.append(match.group(0).strip())
        
        # Boost score if found in assessment section
        assessment = parsed_note["sections"]["assessment"].lower()
        for keyword in keywords:
            if keyword.lower() in assessment:
                score += 0.4
        
        # Boost score if symptoms match
        for symptom in parsed_note.get("symptoms", []):
            symptom_lower = symptom.lower()
            for keyword in keywords:
                if keyword.lower() in symptom_lower:
                    score += 0.2
        
        return min(score, 1.0), evidence
    
    def _find_alternatives(self, code: str) -> List[str]:
        """Find alternative codes in the same category."""
        for category, codes in self.code_database.items():
            if code in codes:
                # Return other codes in same category
                return [c for c in codes.keys() if c != code][:2]
        return []


class CPTRecommender:
    """Recommends CPT procedure codes based on clinical information."""
    
    def __init__(self):
        self.code_database = self._load_cpt_database()
    
    def _load_cpt_database(self) -> Dict:
        """Load common CPT codes."""
        return {
            "evaluation_management": {
                "99211": ("Office visit, established patient, minimal", "5 min", 
                          ["brief", "minimal", "nurse visit"]),
                "99212": ("Office visit, established patient, straightforward", "10 min",
                          ["straightforward", "minor", "simple"]),
                "99213": ("Office visit, established patient, low complexity", "15 min",
                          ["low complexity", "stable chronic", "prescription refill"]),
                "99214": ("Office visit, established patient, moderate complexity", "25 min",
                          ["moderate complexity", "worsening", "new problem", "multiple issues"]),
                "99215": ("Office visit, established patient, high complexity", "40 min",
                          ["high complexity", "severe", "complicated", "extensive counseling"]),
                "99201": ("Office visit, new patient, straightforward", "10 min",
                          ["new patient", "minor problem", "straightforward"]),
                "99202": ("Office visit, new patient, low complexity", "20 min",
                          ["new patient", "low complexity"]),
                "99203": ("Office visit, new patient, moderate complexity", "30 min",
                          ["new patient", "moderate complexity"]),
                "99204": ("Office visit, new patient, comprehensive", "45 min",
                          ["new patient", "comprehensive", "detailed history"]),
                "99205": ("Office visit, new patient, high complexity", "60 min",
                          ["new patient", "high complexity", "extensive"]),
            },
            "preventive": {
                "99381": ("Initial preventive exam, new patient 18-39", "",
                          ["preventive", "annual physical", "new patient", "18-39"]),
                "99382": ("Initial preventive exam, new patient 40-64", "",
                          ["preventive", "annual physical", "new patient", "40-64"]),
                "99383": ("Initial preventive exam, new patient 65+", "",
                          ["preventive", "annual physical", "new patient", "65"]),
                "99391": ("Periodic preventive exam, established patient 18-39", "",
                          ["preventive", "annual physical", "established", "18-39"]),
                "99392": ("Periodic preventive exam, established patient 40-64", "",
                          ["preventive", "annual physical", "established", "40-64"]),
                "99393": ("Periodic preventive exam, established patient 65+", "",
                          ["preventive", "annual physical", "established", "65"]),
            },
            "procedures": {
                "36415": ("Venipuncture for blood draw", "",
                          ["blood draw", "venipuncture", "lab work"]),
                "81001": ("Urinalysis, automated", "",
                          ["urinalysis", "urine test", "ua"]),
                "80053": ("Comprehensive metabolic panel", "",
                          ["cmp", "metabolic panel", "comprehensive"]),
                "80061": ("Lipid panel", "",
                          ["lipid panel", "cholesterol test", "lipids"]),
                "83036": ("Hemoglobin A1C", "",
                          ["a1c", "hba1c", "hemoglobin a1c"]),
                "84443": ("TSH test", "",
                          ["tsh", "thyroid stimulating hormone"]),
            },
            "vaccines": {
                "90471": ("Immunization admin, one vaccine", "",
                          ["vaccine", "immunization", "injection", "flu shot"]),
                "90630": ("Influenza vaccine", "",
                          ["flu vaccine", "influenza"]),
                "90715": ("Tdap vaccine", "",
                          ["tdap", "tetanus", "pertussis"]),
            }
        }
    
    def recommend(self, parsed_note: Dict) -> List[CPTCode]:
        """Generate CPT code recommendations."""
        recommendations = []
        text = parsed_note["sections"]["full_text"].lower()
        
        # Check for visit type indicators
        is_new_patient = self._is_new_patient(text)
        complexity = self._assess_complexity(text, parsed_note)
        
        # E/M code recommendation
        em_code = self._recommend_em_code(is_new_patient, complexity)
        if em_code:
            recommendations.append(em_code)
        
        # Procedure recommendations
        for category, codes in self.code_database.items():
            if category == "evaluation_management":
                continue
            
            for code, (description, time_str, keywords) in codes.items():
                score, evidence = self._calculate_code_score(code, description, keywords, text)
                if score > 0.5:
                    recommendations.append(CPTCode(
                        code=code,
                        description=description,
                        confidence=round(score, 2),
                        evidence=evidence[:2],
                        category=category,
                        time=time_str if time_str else None
                    ))
        
        return recommendations
    
    def _is_new_patient(self, text: str) -> bool:
        """Determine if this is a new patient encounter."""
        new_indicators = ["new patient", "initial visit", "first visit", "established"]
        new_count = sum(1 for indicator in new_indicators[:3] if indicator in text)
        est_count = 1 if "established" in text else 0
        return new_count > est_count
    
    def _assess_complexity(self, text: str, parsed_note: Dict) -> str:
        """Assess visit complexity level."""
        text_lower = text.lower()
        
        # High complexity indicators
        high_indicators = ["high complexity", "severe", "complicated", "multiple problems", 
                          "extensive counseling", "hospital admission", "emergency"]
        if any(ind in text_lower for ind in high_indicators):
            return "high"
        
        # Moderate complexity indicators
        mod_indicators = ["moderate", "worsening", "new problem", "chronic conditions",
                         "prescription management", "diagnostic tests ordered"]
        if any(ind in text_lower for ind in mod_indicators):
            return "moderate"
        
        # Low complexity indicators
        low_indicators = ["stable", "routine", "follow-up", "prescription refill"]
        if any(ind in text_lower for ind in low_indicators):
            return "low"
        
        # Check number of diagnoses
        if len(parsed_note.get("diagnoses", [])) >= 3:
            return "moderate"
        
        return "low"
    
    def _recommend_em_code(self, is_new_patient: bool, complexity: str) -> Optional[CPTCode]:
        """Recommend appropriate E/M code."""
        em_codes = {
            True: {  # New patient
                "low": "99202",
                "moderate": "99203",
                "high": "99204"
            },
            False: {  # Established patient
                "low": "99213",
                "moderate": "99214",
                "high": "99215"
            }
        }
        
        code = em_codes[is_new_patient].get(complexity, "99213")
        code_info = self.code_database["evaluation_management"].get(code)
        
        if code_info:
            desc, time_str, _ = code_info
            return CPTCode(
                code=code,
                description=desc,
                confidence=0.75,
                evidence=[f"{complexity} complexity visit"],
                category="evaluation_management",
                time=time_str
            )
        return None
    
    def _calculate_code_score(self, code: str, description: str, keywords: List[str], 
                              text: str) -> Tuple[float, List[str]]:
        """Calculate confidence score for a CPT code match."""
        score = 0.0
        evidence = []
        
        for keyword in keywords:
            if keyword.lower() in text:
                score += 0.35
                pattern = r'.{0,20}' + re.escape(keyword) + r'.{0,20}'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in list(matches)[:1]:
                    evidence.append(match.group(0).strip())
        
        return min(score, 1.0), evidence


class CodingAssistant:
    """Main coding assistant class."""
    
    def __init__(self):
        self.parser = ClinicalNoteParser()
        self.icd10_recommender = ICD10Recommender()
        self.cpt_recommender = CPTRecommender()
    
    def analyze(self, clinical_note: str) -> CodingResult:
        """Analyze clinical note and return coding recommendations."""
        # Parse the note
        parsed = self.parser.parse(clinical_note)
        
        # Generate recommendations
        icd10_codes = self.icd10_recommender.recommend(parsed)
        cpt_codes = self.cpt_recommender.recommend(parsed)
        
        # Generate warnings
        warnings = self._generate_warnings(parsed, icd10_codes, cpt_codes)
        
        # Generate summary
        summary = self._generate_summary(parsed)
        
        return CodingResult(
            icd10_codes=icd10_codes,
            cpt_codes=cpt_codes,
            warnings=warnings,
            note_summary=summary
        )
    
    def _generate_warnings(self, parsed: Dict, icd10_codes: List[ICD10Code], 
                          cpt_codes: List[CPTCode]) -> List[str]:
        """Generate warnings about the coding recommendations."""
        warnings = []
        
        # Check for low confidence
        low_conf_icd = [c for c in icd10_codes if c.confidence < 0.5]
        if low_conf_icd:
            warnings.append(f"{len(low_conf_icd)} ICD-10 code(s) have low confidence - manual review recommended")
        
        low_conf_cpt = [c for c in cpt_codes if c.confidence < 0.5]
        if low_conf_cpt:
            warnings.append(f"{len(low_conf_cpt)} CPT code(s) have low confidence - manual review recommended")
        
        # Check for missing documentation
        if not parsed["sections"]["assessment"]:
            warnings.append("No assessment/diagnosis section found - documentation may be incomplete")
        
        if not parsed["sections"]["plan"]:
            warnings.append("No plan section found - may impact procedure code selection")
        
        # Check for complexity indicators
        text = parsed["sections"]["full_text"].lower()
        if "chronic" in text and not any(c.code.startswith("Z") for c in icd10_codes):
            warnings.append("Chronic conditions mentioned - ensure proper chronic disease coding")
        
        return warnings
    
    def _generate_summary(self, parsed: Dict) -> str:
        """Generate a brief summary of the clinical note."""
        parts = []
        
        if parsed["diagnoses"]:
            parts.append(f"Diagnoses: {len(parsed['diagnoses'])} identified")
        
        if parsed["symptoms"]:
            parts.append(f"Symptoms: {len(parsed['symptoms'])} documented")
        
        if parsed["vitals"]:
            parts.append(f"Vitals: {len(parsed['vitals'])} recorded")
        
        return "; ".join(parts) if parts else "Clinical note analyzed"


def format_output(result: CodingResult, output_format: str = "json") -> str:
    """Format the coding result for output."""
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2)
    
    # Text format
    lines = []
    lines.append("=" * 60)
    lines.append("MEDICAL CODING RECOMMENDATIONS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Note Summary: {result.note_summary}")
    lines.append("")
    
    lines.append("-" * 40)
    lines.append("ICD-10 DIAGNOSIS CODES")
    lines.append("-" * 40)
    if result.icd10_codes:
        for code in result.icd10_codes:
            lines.append(f"\nCode: {code.code}")
            lines.append(f"Description: {code.description}")
            lines.append(f"Confidence: {code.confidence:.0%}")
            if code.evidence:
                lines.append(f"Evidence: {'; '.join(code.evidence[:2])}")
            if code.alternatives:
                lines.append(f"Alternatives: {', '.join(code.alternatives)}")
    else:
        lines.append("No ICD-10 codes recommended")
    
    lines.append("")
    lines.append("-" * 40)
    lines.append("CPT PROCEDURE CODES")
    lines.append("-" * 40)
    if result.cpt_codes:
        for code in result.cpt_codes:
            lines.append(f"\nCode: {code.code}")
            lines.append(f"Description: {code.description}")
            lines.append(f"Confidence: {code.confidence:.0%}")
            if code.time:
                lines.append(f"Typical Time: {code.time}")
            if code.evidence:
                lines.append(f"Evidence: {'; '.join(code.evidence[:2])}")
    else:
        lines.append("No CPT codes recommended")
    
    if result.warnings:
        lines.append("")
        lines.append("-" * 40)
        lines.append("WARNINGS")
        lines.append("-" * 40)
        for warning in result.warnings:
            lines.append(f"⚠️  {warning}")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("DISCLAIMER: All codes require verification by certified medical coder")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="ICD-10 & CPT Coding Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input note.txt
  python main.py --input note.txt --format json
  python main.py --interactive
        """
    )
    parser.add_argument("--input", "-i", help="Path to clinical note file")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                       help="Output format (default: text)")
    parser.add_argument("--interactive", "-I", action="store_true",
                       help="Interactive mode")
    
    args = parser.parse_args()
    
    assistant = CodingAssistant()
    
    if args.interactive:
        print("ICD-10 & CPT Coding Assistant - Interactive Mode")
        print("Enter clinical notes (press Ctrl+D or type 'END' on new line to finish):")
        print("-" * 60)
        
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
        except EOFError:
            pass
        
        text = "\n".join(lines)
        if text.strip():
            result = assistant.analyze(text)
            print("\n" + format_output(result, args.format))
    
    elif args.input:
        try:
            with open(args.input, 'r') as f:
                text = f.read()
            result = assistant.analyze(text)
            print(format_output(result, args.format))
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
