#!/usr/bin/env python3
"""
Adverse Event Narrative Generator
Generates CIOMS-compliant narratives for ICSR reporting
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional


class CIOMSNarrativeGenerator:
    """Generator for CIOMS-compliant adverse event narratives"""
    
    def __init__(self, case_data: Dict[str, Any]):
        self.case_data = case_data
        self.narrative_sections = []
    
    def generate(self) -> str:
        """Generate complete CIOMS narrative"""
        self.narrative_sections = [
            self._generate_header(),
            self._generate_patient_demographics(),
            self._generate_medical_history(),
            self._generate_concomitant_medications(),
            self._generate_suspect_drugs(),
            self._generate_adverse_events(),
            self._generate_diagnostic_tests(),
            self._generate_treatment(),
            self._generate_dechallenge_rechallenge(),
            self._generate_outcome(),
            self._generate_causality(),
            self._generate_reporter_comments()
        ]
        
        # Filter out empty sections and join
        sections = [s for s in self.narrative_sections if s.strip()]
        return "\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """Generate case header"""
        case_id = self.case_data.get('case_id', 'Unknown')
        report_date = self.case_data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
        return f"CASE IDENTIFIER: {case_id}\nDATE OF REPORT: {report_date}"
    
    def _generate_patient_demographics(self) -> str:
        """Generate patient demographics section"""
        parts = ["PATIENT DEMOGRAPHICS:"]
        
        age = self.case_data.get('patient_age', '')
        sex = self.case_data.get('patient_sex', '')
        
        if age and sex:
            parts.append(f"A {age}-old {sex.lower()}.")
        elif age:
            parts.append(f"Age: {age}.")
        elif sex:
            parts.append(f"Sex: {sex}.")
        
        # Additional characteristics
        characteristics = []
        if 'weight_kg' in self.case_data:
            characteristics.append(f"weight {self.case_data['weight_kg']} kg")
        if 'height_cm' in self.case_data:
            characteristics.append(f"height {self.case_data['height_cm']} cm")
        if 'ethnicity' in self.case_data:
            characteristics.append(f"ethnicity: {self.case_data['ethnicity']}")
        
        if characteristics:
            parts.append(f"Physical characteristics: {', '.join(characteristics)}.")
        
        if 'special_population' in self.case_data:
            parts.append(f"Special population: {self.case_data['special_population']}.")
        
        return "\n".join(parts)
    
    def _generate_medical_history(self) -> str:
        """Generate medical history section"""
        history = self.case_data.get('medical_history', [])
        if not history:
            return ""
        
        if isinstance(history, str):
            history = [history]
        
        parts = ["RELEVANT MEDICAL HISTORY:"]
        for condition in history:
            parts.append(f"- {condition}")
        
        return "\n".join(parts)
    
    def _generate_concomitant_medications(self) -> str:
        """Generate concomitant medications section"""
        conmeds = self.case_data.get('concomitant_drugs', [])
        if not conmeds:
            return ""
        
        if isinstance(conmeds, str):
            conmeds = [{'drug_name': conmeds}]
        
        parts = ["CONCOMITANT MEDICATIONS:"]
        for med in conmeds:
            if isinstance(med, str):
                parts.append(f"- {med}")
            else:
                drug_info = med.get('drug_name', 'Unknown')
                if 'indication' in med:
                    drug_info += f" for {med['indication']}"
                if 'dose' in med:
                    drug_info += f", {med['dose']}"
                if 'frequency' in med:
                    drug_info += f" {med['frequency']}"
                parts.append(f"- {drug_info}")
        
        return "\n".join(parts)
    
    def _generate_suspect_drugs(self) -> str:
        """Generate suspect drug(s) section"""
        drugs = self.case_data.get('suspect_drugs', [])
        if not drugs:
            return ""
        
        parts = ["SUSPECT DRUG(S):"]
        
        for drug in drugs:
            drug_lines = []
            
            name = drug.get('drug_name', 'Unknown')
            indication = drug.get('indication', '')
            
            drug_desc = f"Drug: {name}"
            if indication:
                drug_desc += f" (indicated for {indication})"
            drug_lines.append(drug_desc)
            
            # Dosing details
            dose_parts = []
            if 'dose' in drug:
                dose_parts.append(drug['dose'])
            if 'frequency' in drug:
                dose_parts.append(drug['frequency'])
            if 'route' in drug:
                dose_parts.append(f"via {drug['route']}")
            
            if dose_parts:
                drug_lines.append(f"  Dosage: {' '.join(dose_parts)}")
            
            # Dates
            if 'start_date' in drug:
                drug_lines.append(f"  Therapy start: {drug['start_date']}")
            if 'stop_date' in drug:
                drug_lines.append(f"  Therapy stop: {drug['stop_date']}")
            
            # Lot number
            if 'lot_number' in drug:
                drug_lines.append(f"  Lot/Batch: {drug['lot_number']}")
            
            parts.extend(drug_lines)
            parts.append("")  # Empty line between drugs
        
        return "\n".join(parts).strip()
    
    def _generate_adverse_events(self) -> str:
        """Generate adverse event description section"""
        events = self.case_data.get('adverse_events', [])
        if not events:
            return ""
        
        if isinstance(events, str):
            events = [{'meddra_pt': events}]
        
        parts = ["ADVERSE EVENT(S):"]
        
        for i, event in enumerate(events, 1):
            if isinstance(event, str):
                event = {'meddra_pt': event}
            
            event_lines = []
            event_name = event.get('meddra_pt', event.get('reaction', 'Unknown'))
            
            event_lines.append(f"{i}. {event_name}")
            
            if 'onset_date' in event:
                event_lines.append(f"   Onset date: {event['onset_date']}")
            if 'onset_latency' in event:
                event_lines.append(f"   Time to onset: {event['onset_latency']}")
            if 'severity' in event:
                event_lines.append(f"   Severity: {event['severity']}")
            if 'seriousness' in event:
                event_lines.append(f"   Seriousness criteria: {event['seriousness']}")
            if 'description' in event:
                event_lines.append(f"   Description: {event['description']}")
            
            parts.extend(event_lines)
        
        return "\n".join(parts)
    
    def _generate_diagnostic_tests(self) -> str:
        """Generate diagnostic tests section"""
        tests = self.case_data.get('diagnostic_tests', [])
        if not tests:
            return ""
        
        parts = ["DIAGNOSTIC TESTS AND RESULTS:"]
        
        for test in tests:
            if isinstance(test, str):
                parts.append(f"- {test}")
            else:
                test_desc = test.get('test', 'Unknown test')
                if 'value' in test:
                    test_desc += f": {test['value']}"
                    if 'reference_range' in test:
                        test_desc += f" (reference: {test['reference_range']})"
                if 'date' in test:
                    test_desc += f" on {test['date']}"
                parts.append(f"- {test_desc}")
        
        return "\n".join(parts)
    
    def _generate_treatment(self) -> str:
        """Generate treatment section"""
        treatment = self.case_data.get('treatment', [])
        if not treatment:
            return ""
        
        if isinstance(treatment, str):
            treatment = [treatment]
        
        parts = ["TREATMENT OF ADVERSE EVENT:"]
        for item in treatment:
            parts.append(f"- {item}")
        
        return "\n".join(parts)
    
    def _generate_dechallenge_rechallenge(self) -> str:
        """Generate dechallenge/rechallenge section"""
        parts = []
        
        dechallenge = self.case_data.get('dechallenge')
        rechallenge = self.case_data.get('rechallenge')
        
        if dechallenge or rechallenge:
            parts.append("DECHALLENGE AND RECHALLENGE:")
            
            if dechallenge:
                parts.append(f"Dechallenge: {dechallenge}")
            
            if rechallenge:
                parts.append(f"Rechallenge: {rechallenge}")
        
        return "\n".join(parts)
    
    def _generate_outcome(self) -> str:
        """Generate outcome section"""
        outcome = self.case_data.get('outcome')
        if not outcome:
            return ""
        
        parts = [f"OUTCOME: {outcome}"]
        
        if 'outcome_date' in self.case_data:
            parts.append(f"Date of outcome: {self.case_data['outcome_date']}")
        
        if 'sequelae' in self.case_data:
            parts.append(f"Sequelae: {self.case_data['sequelae']}")
        
        return "\n".join(parts)
    
    def _generate_causality(self) -> str:
        """Generate causality assessment section"""
        causality = self.case_data.get('causality')
        if not causality:
            return ""
        
        parts = [f"CAUSALITY ASSESSMENT: {causality}"]
        
        if 'causality_rationale' in self.case_data:
            parts.append(f"Rationale: {self.case_data['causality_rationale']}")
        
        return "\n".join(parts)
    
    def _generate_reporter_comments(self) -> str:
        """Generate reporter comments section"""
        comments = self.case_data.get('reporter_comments')
        if not comments:
            return ""
        
        return f"REPORTER COMMENTS:\n{comments}"


def validate_case_data(case_data: Dict[str, Any]) -> List[str]:
    """Validate required fields in case data"""
    errors = []
    
    # Required fields
    if not case_data.get('case_id'):
        errors.append("Missing required field: case_id")
    
    if not case_data.get('patient_age') and not case_data.get('patient_sex'):
        errors.append("Missing patient demographics (age or sex)")
    
    if not case_data.get('suspect_drugs'):
        errors.append("Missing required field: suspect_drugs")
    
    if not case_data.get('adverse_events'):
        errors.append("Missing required field: adverse_events")
    
    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Generate CIOMS-compliant adverse event narrative for ICSR'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSON file containing case data'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate input without generating narrative'
    )
    
    args = parser.parse_args()
    
    # Read input file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            case_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate
    errors = validate_case_data(case_data)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    
    if args.validate_only:
        print("Validation passed.")
        sys.exit(0)
    
    # Generate narrative
    generator = CIOMSNarrativeGenerator(case_data)
    narrative = generator.generate()
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(narrative)
        print(f"Narrative written to: {args.output}")
    else:
        print(narrative)


if __name__ == '__main__':
    main()
