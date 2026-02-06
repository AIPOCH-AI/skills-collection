#!/usr/bin/env python3
"""
Medical Scribe Dictation - Convert physician dictation to structured SOAP notes.

This module provides functionality to:
- Process transcribed medical dictation
- Generate structured SOAP notes
- Handle medical terminology normalization
- Validate clinical completeness
"""

import re
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import warnings

# Optional dependencies with graceful degradation
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class VitalSigns:
    """Represents patient vital signs."""
    temperature: Optional[str] = None
    heart_rate: Optional[str] = None
    blood_pressure: Optional[str] = None
    respiratory_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    weight: Optional[str] = None
    height: Optional[str] = None
    bmi: Optional[str] = None


@dataclass
class SOAPNote:
    """Structured SOAP note data class."""
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    
    # Subjective
    chief_complaint: str = ""
    history_present_illness: str = ""
    review_of_systems: str = ""
    past_medical_history: str = ""
    medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    social_history: str = ""
    family_history: str = ""
    
    # Objective
    vital_signs: VitalSigns = field(default_factory=VitalSigns)
    physical_examination: str = ""
    diagnostic_studies: str = ""
    
    # Assessment
    primary_diagnosis: str = ""
    differential_diagnoses: List[str] = field(default_factory=list)
    clinical_reasoning: str = ""
    
    # Plan
    diagnostic_plan: str = ""
    therapeutic_plan: str = ""
    patient_education: str = ""
    follow_up: str = ""
    
    # Metadata
    specialty: str = "general"
    confidence_score: float = 0.0
    warnings: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert SOAP note to markdown format."""
        sections = [
            f"# Clinical Note - {self.date}",
            "",
            "## Subjective",
            "",
            f"**Chief Complaint:** {self.chief_complaint or 'Not documented'}",
            "",
            f"**History of Present Illness:** {self.history_present_illness or 'Not documented'}",
            "",
        ]
        
        if self.review_of_systems:
            sections.extend([
                "**Review of Systems:**",
                self.review_of_systems,
                ""
            ])
        
        if self.past_medical_history:
            sections.extend([
                "**Past Medical History:**",
                self.past_medical_history,
                ""
            ])
        
        if self.medications:
            sections.extend([
                "**Current Medications:**",
                "\n".join(f"- {med}" for med in self.medications),
                ""
            ])
        
        if self.allergies:
            sections.extend([
                "**Allergies:**",
                "\n".join(f"- {allergy}" for allergy in self.allergies),
                ""
            ])
        
        if self.social_history:
            sections.extend([
                "**Social History:**",
                self.social_history,
                ""
            ])
        
        if self.family_history:
            sections.extend([
                "**Family History:**",
                self.family_history,
                ""
            ])
        
        # Objective
        sections.extend([
            "## Objective",
            ""
        ])
        
        vital_signs_text = self._format_vital_signs()
        if vital_signs_text:
            sections.extend([
                "**Vital Signs:**",
                vital_signs_text,
                ""
            ])
        
        if self.physical_examination:
            sections.extend([
                "**Physical Examination:**",
                self.physical_examination,
                ""
            ])
        
        if self.diagnostic_studies:
            sections.extend([
                "**Diagnostic Studies:**",
                self.diagnostic_studies,
                ""
            ])
        
        # Assessment
        sections.extend([
            "## Assessment",
            ""
        ])
        
        if self.primary_diagnosis:
            sections.extend([
                f"**Primary Diagnosis:** {self.primary_diagnosis}",
                ""
            ])
        
        if self.differential_diagnoses:
            sections.extend([
                "**Differential Diagnoses:**",
                "\n".join(f"- {dx}" for dx in self.differential_diagnoses),
                ""
            ])
        
        if self.clinical_reasoning:
            sections.extend([
                "**Clinical Reasoning:**",
                self.clinical_reasoning,
                ""
            ])
        
        # Plan
        sections.extend([
            "## Plan",
            ""
        ])
        
        if self.diagnostic_plan:
            sections.extend([
                "**Diagnostic:**",
                self.diagnostic_plan,
                ""
            ])
        
        if self.therapeutic_plan:
            sections.extend([
                "**Therapeutic:**",
                self.therapeutic_plan,
                ""
            ])
        
        if self.patient_education:
            sections.extend([
                "**Patient Education:**",
                self.patient_education,
                ""
            ])
        
        if self.follow_up:
            sections.extend([
                "**Follow-up:**",
                self.follow_up,
                ""
            ])
        
        # Metadata
        if self.warnings:
            sections.extend([
                "---",
                "",
                "**⚠️ Validation Warnings:**",
                "\n".join(f"- {w}" for w in self.warnings),
                ""
            ])
        
        sections.extend([
            "---",
            "",
            f"*Note generated with confidence score: {self.confidence_score:.2f}*",
            "",
            "*This note was generated by AI and requires physician review before finalization.*"
        ])
        
        return "\n".join(sections)
    
    def _format_vital_signs(self) -> str:
        """Format vital signs for display."""
        vs = self.vital_signs
        parts = []
        if vs.temperature:
            parts.append(f"Temperature: {vs.temperature}")
        if vs.heart_rate:
            parts.append(f"Heart Rate: {vs.heart_rate}")
        if vs.blood_pressure:
            parts.append(f"Blood Pressure: {vs.blood_pressure}")
        if vs.respiratory_rate:
            parts.append(f"Respiratory Rate: {vs.respiratory_rate}")
        if vs.oxygen_saturation:
            parts.append(f"O₂ Saturation: {vs.oxygen_saturation}")
        if vs.weight:
            parts.append(f"Weight: {vs.weight}")
        if vs.height:
            parts.append(f"Height: {vs.height}")
        if vs.bmi:
            parts.append(f"BMI: {vs.bmi}")
        return " | ".join(parts) if parts else ""


class MedicalTerminologyProcessor:
    """Processes and normalizes medical terminology."""
    
    # Common medical abbreviations and their expansions
    ABBREVIATIONS = {
        "c/o": "complaining of",
        "w/": "with",
        "w/o": "without",
        "s/p": "status post",
        "r/o": "rule out",
        "h/o": "history of",
        "b/l": "bilateral",
        "u/l": "unilateral",
        "d/t": "due to",
        "secondary to": "secondary to",
        "c-section": "cesarean section",
        "bmi": "body mass index",
        "bp": "blood pressure",
        "hr": "heart rate",
        "rr": "respiratory rate",
        "o2sat": "oxygen saturation",
        "spo2": "oxygen saturation",
        "temp": "temperature",
        "htn": "hypertension",
        "dm": "diabetes mellitus",
        "cad": "coronary artery disease",
        "chf": "congestive heart failure",
        "copd": "chronic obstructive pulmonary disease",
        "uti": "urinary tract infection",
        "aki": "acute kidney injury",
        "ckd": "chronic kidney disease",
        "mi": "myocardial infarction",
        "cva": "cerebrovascular accident",
        "tia": "transient ischemic attack",
        "pe": "pulmonary embolism",
        "dvt": "deep vein thrombosis",
        "afib": "atrial fibrillation",
        "hf": "heart failure",
        "aki": "acute kidney injury",
        "ards": "acute respiratory distress syndrome",
        "ards": "acute respiratory distress syndrome",
    }
    
    # Drug name patterns (simplified)
    DRUG_SUFFIXES = [
        "mycin", "cillin", "xaban", "nib", "mab", "zolam", "pram", "sartan",
        "statin", "pril", "sone", "nide", "micin", "cycline", "azole"
    ]
    
    def normalize_text(self, text: str) -> str:
        """Normalize medical abbreviations in text."""
        text_lower = text.lower()
        
        # Expand common abbreviations
        for abbr, expansion in self.ABBREVIATIONS.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            text = pattern.sub(expansion, text)
        
        return text
    
    def extract_medications(self, text: str) -> List[str]:
        """Extract medication mentions from text."""
        medications = []
        
        # Pattern for common medication formats
        # Matches: "Lisinopril 10mg", "metformin", "Amoxicillin-Clavulanate"
        med_patterns = [
            r'\b([A-Z][a-z]+(?:-[A-Z]?[a-z]+)?\s+\d+\s*(?:mg|mcg|g|ml|units?))\b',
            r'\b([a-z]+(?:mycin|cillin|zolam|sartan|statin|pril|sone|nide))\b',
            r'\b(aspirin|ibuprofen|acetaminophen|lisinopril|metformin|atorvastatin)\b',
        ]
        
        for pattern in med_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            medications.extend(matches)
        
        return list(set(medications))
    
    def extract_vital_signs(self, text: str) -> VitalSigns:
        """Extract vital signs from text using regex patterns."""
        vs = VitalSigns()
        
        # Temperature patterns
        temp_match = re.search(r'(\d+\.?\d*)\s*(?:degrees?|°)?\s*[Ff]', text)
        if temp_match:
            vs.temperature = f"{temp_match.group(1)}°F"
        else:
            temp_match = re.search(r'(\d+\.?\d*)\s*(?:degrees?|°)?\s*[Cc]', text)
            if temp_match:
                vs.temperature = f"{temp_match.group(1)}°C"
        
        # Blood pressure
        bp_match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mm\s*Hg)?', text)
        if bp_match:
            vs.blood_pressure = f"{bp_match.group(1)}/{bp_match.group(2)} mmHg"
        
        # Heart rate
        hr_match = re.search(r'(?:heart rate|hr|pulse)\s*(?:of|is|was)?\s*(\d+)', text, re.IGNORECASE)
        if hr_match:
            vs.heart_rate = f"{hr_match.group(1)} bpm"
        
        # Respiratory rate
        rr_match = re.search(r'(?:respiratory rate|rr|respirations?)\s*(?:of|is|was)?\s*(\d+)', text, re.IGNORECASE)
        if rr_match:
            vs.respiratory_rate = f"{rr_match.group(1)} /min"
        
        # O2 saturation
        o2_match = re.search(r'(?:o2\s*sat|spo2|oxygen)\s*(?:of|is|was)?\s*(\d+)%?', text, re.IGNORECASE)
        if o2_match:
            vs.oxygen_saturation = f"{o2_match.group(1)}%"
        
        return vs


class MedicalScribe:
    """Main medical scribe class for processing dictation."""
    
    def __init__(self, specialty: str = "general", llm_provider: Optional[str] = None):
        self.specialty = specialty
        self.terminology_processor = MedicalTerminologyProcessor()
        self.llm_provider = llm_provider
        
        # Initialize LLM client if available
        self.llm_client = None
        if llm_provider == "openai" and OPENAI_AVAILABLE:
            self.llm_client = openai.OpenAI()
        elif llm_provider == "anthropic" and ANTHROPIC_AVAILABLE:
            self.llm_client = Anthropic()
    
    def process_dictation(self, text: str) -> SOAPNote:
        """
        Process medical dictation and generate SOAP note.
        
        Args:
            text: Raw transcribed dictation text
            
        Returns:
            SOAPNote: Structured SOAP note object
        """
        # Normalize terminology
        normalized_text = self.terminology_processor.normalize_text(text)
        
        # If LLM available, use it for intelligent parsing
        if self.llm_client and self.llm_provider:
            return self._process_with_llm(normalized_text)
        else:
            # Fallback to rule-based parsing
            return self._process_rule_based(normalized_text)
    
    def _process_with_llm(self, text: str) -> SOAPNote:
        """Process dictation using LLM for intelligent extraction."""
        prompt = self._build_extraction_prompt(text)
        
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a medical scribe AI. Extract clinical information and format as structured JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4096,
                    system="You are a medical scribe AI. Extract clinical information and format as structured JSON.",
                    messages=[{"role": "user", "content": prompt}]
                )
                # Extract JSON from response
                content = response.content[0].text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in LLM response")
            else:
                return self._process_rule_based(text)
            
            return self._build_soap_from_dict(result)
            
        except Exception as e:
            warnings.warn(f"LLM processing failed: {e}. Falling back to rule-based parsing.")
            return self._process_rule_based(text)
    
    def _build_extraction_prompt(self, text: str) -> str:
        """Build prompt for LLM extraction."""
        return f"""Extract clinical information from the following medical dictation and format as JSON with this structure:

{{
    "chief_complaint": "...",
    "history_present_illness": "...",
    "review_of_systems": "...",
    "past_medical_history": "...",
    "medications": ["..."],
    "allergies": ["..."],
    "social_history": "...",
    "family_history": "...",
    "vital_signs": {{
        "temperature": "...",
        "heart_rate": "...",
        "blood_pressure": "...",
        "respiratory_rate": "...",
        "oxygen_saturation": "..."
    }},
    "physical_examination": "...",
    "diagnostic_studies": "...",
    "primary_diagnosis": "...",
    "differential_diagnoses": ["..."],
    "clinical_reasoning": "...",
    "diagnostic_plan": "...",
    "therapeutic_plan": "...",
    "patient_education": "...",
    "follow_up": "..."
}}

Dictation text:
{text}

Respond ONLY with valid JSON."""
    
    def _build_soap_from_dict(self, data: Dict) -> SOAPNote:
        """Build SOAPNote from dictionary."""
        note = SOAPNote(specialty=self.specialty)
        
        # Subjective
        note.chief_complaint = data.get("chief_complaint", "")
        note.history_present_illness = data.get("history_present_illness", "")
        note.review_of_systems = data.get("review_of_systems", "")
        note.past_medical_history = data.get("past_medical_history", "")
        note.medications = data.get("medications", [])
        note.allergies = data.get("allergies", [])
        note.social_history = data.get("social_history", "")
        note.family_history = data.get("family_history", "")
        
        # Objective - vital signs
        vs_data = data.get("vital_signs", {})
        note.vital_signs = VitalSigns(
            temperature=vs_data.get("temperature"),
            heart_rate=vs_data.get("heart_rate"),
            blood_pressure=vs_data.get("blood_pressure"),
            respiratory_rate=vs_data.get("respiratory_rate"),
            oxygen_saturation=vs_data.get("oxygen_saturation")
        )
        note.physical_examination = data.get("physical_examination", "")
        note.diagnostic_studies = data.get("diagnostic_studies", "")
        
        # Assessment
        note.primary_diagnosis = data.get("primary_diagnosis", "")
        note.differential_diagnoses = data.get("differential_diagnoses", [])
        note.clinical_reasoning = data.get("clinical_reasoning", "")
        
        # Plan
        note.diagnostic_plan = data.get("diagnostic_plan", "")
        note.therapeutic_plan = data.get("therapeutic_plan", "")
        note.patient_education = data.get("patient_education", "")
        note.follow_up = data.get("follow_up", "")
        
        # Validate and add warnings
        note.warnings = self._validate_note(note)
        note.confidence_score = self._calculate_confidence(note)
        
        return note
    
    def _process_rule_based(self, text: str) -> SOAPNote:
        """Process dictation using rule-based parsing."""
        note = SOAPNote(specialty=self.specialty)
        
        # Extract vital signs
        note.vital_signs = self.terminology_processor.extract_vital_signs(text)
        
        # Extract medications
        note.medications = self.terminology_processor.extract_medications(text)
        
        # Simple section detection based on keywords
        text_lower = text.lower()
        
        # Chief complaint - look for common patterns
        cc_patterns = [
            r'chief complaint[:\s]+([^\.]+)',
            r'cc[:\s]+([^\.]+)',
            r'patient (?:presents|comes) (?:with|for) ([^\.]+)',
        ]
        for pattern in cc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                note.chief_complaint = match.group(1).strip()
                break
        
        # Assessment/Diagnosis
        dx_patterns = [
            r'assessment[:\s]+([^.]+)',
            r'impression[:\s]+([^.]+)',
            r'diagnosis[:\s]+([^.]+)',
        ]
        for pattern in dx_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                note.primary_diagnosis = match.group(1).strip()
                break
        
        # Plan
        plan_patterns = [
            r'plan[:\s]+(.+?)(?=\n\n|$)',
            r'treatment plan[:\s]+(.+?)(?=\n\n|$)',
        ]
        for pattern in plan_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                note.therapeutic_plan = match.group(1).strip()
                break
        
        # If no structured sections found, put all in HPI
        if not note.chief_complaint and not note.primary_diagnosis:
            note.history_present_illness = text
        
        # Validate and calculate confidence
        note.warnings = self._validate_note(note)
        note.confidence_score = self._calculate_confidence(note)
        
        return note
    
    def _validate_note(self, note: SOAPNote) -> List[str]:
        """Validate SOAP note completeness and flag issues."""
        warnings = []
        
        # Check required elements
        if not note.chief_complaint:
            warnings.append("Chief complaint not identified")
        if not note.history_present_illness and not note.chief_complaint:
            warnings.append("Limited clinical history documented")
        if not note.primary_diagnosis and not note.assessment:
            warnings.append("No assessment/diagnosis identified")
        if not note.therapeutic_plan and not note.diagnostic_plan:
            warnings.append("No plan documented")
        
        # Check vital signs completeness
        vs = note.vital_signs
        if not any([vs.temperature, vs.heart_rate, vs.blood_pressure]):
            warnings.append("Vital signs incomplete or missing")
        
        return warnings
    
    def _calculate_confidence(self, note: SOAPNote) -> float:
        """Calculate confidence score based on completeness."""
        score = 0.0
        
        # Subjective completeness (30%)
        if note.chief_complaint:
            score += 0.10
        if note.history_present_illness:
            score += 0.10
        if note.medications or note.allergies:
            score += 0.10
        
        # Objective completeness (20%)
        vs_fields = [note.vital_signs.temperature, note.vital_signs.heart_rate, 
                     note.vital_signs.blood_pressure]
        score += sum(0.07 for f in vs_fields if f) * 0.2
        if note.physical_examination:
            score += 0.05
        
        # Assessment completeness (25%)
        if note.primary_diagnosis:
            score += 0.15
        if note.differential_diagnoses:
            score += 0.05
        if note.clinical_reasoning:
            score += 0.05
        
        # Plan completeness (25%)
        if note.therapeutic_plan:
            score += 0.15
        if note.follow_up:
            score += 0.10
        
        return min(score, 1.0)


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text using Whisper (if available).
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except ImportError:
        raise RuntimeError(
            "Audio transcription requires 'openai-whisper' package. "
            "Install with: pip install openai-whisper"
        )


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Medical Scribe - Convert physician dictation to SOAP notes"
    )
    parser.add_argument("--input", "-i", help="Input text or path to text file")
    parser.add_argument("--audio", "-a", help="Path to audio file (requires whisper)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--specialty", "-s", default="general", 
                        help="Medical specialty (default: general)")
    parser.add_argument("--llm", choices=["openai", "anthropic"],
                        help="LLM provider for advanced parsing")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    
    args = parser.parse_args()
    
    # Get input text
    if args.audio:
        print(f"Transcribing audio: {args.audio}")
        text = transcribe_audio(args.audio)
    elif args.input:
        if Path(args.input).exists():
            text = Path(args.input).read_text()
        else:
            text = args.input
    else:
        # Read from stdin
        import sys
        text = sys.stdin.read()
    
    if not text.strip():
        print("Error: No input provided", file=sys.stderr)
        sys.exit(1)
    
    # Process dictation
    print("Processing dictation...")
    scribe = MedicalScribe(specialty=args.specialty, llm_provider=args.llm)
    note = scribe.process_dictation(text)
    
    # Generate output
    if args.format == "json":
        import json
        output = json.dumps({
            "chief_complaint": note.chief_complaint,
            "history_present_illness": note.history_present_illness,
            "medications": note.medications,
            "vital_signs": {
                "temperature": note.vital_signs.temperature,
                "heart_rate": note.vital_signs.heart_rate,
                "blood_pressure": note.vital_signs.blood_pressure,
                "respiratory_rate": note.vital_signs.respiratory_rate,
                "oxygen_saturation": note.vital_signs.oxygen_saturation,
            },
            "assessment": note.primary_diagnosis,
            "plan": note.therapeutic_plan,
            "confidence": note.confidence_score,
            "warnings": note.warnings,
        }, indent=2)
    else:
        output = note.to_markdown()
    
    # Output results
    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to: {args.output}")
    else:
        print(output)
    
    print(f"\nConfidence Score: {note.confidence_score:.2%}")
    if note.warnings:
        print(f"⚠️  {len(note.warnings)} validation warning(s) - physician review required")


if __name__ == "__main__":
    main()
