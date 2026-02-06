#!/usr/bin/env python3
"""
Prior Authorization Letter Generator
Generates insurance prior authorization request letters with clinical justification.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PriorAuthRequest:
    """Data class for prior authorization request."""
    patient_name: str
    patient_id: str
    patient_dob: str
    provider_name: str
    provider_npi: str
    provider_address: str
    provider_phone: str
    service_type: str
    service_description: str
    cpt_code: Optional[str]
    icd10_codes: List[str]
    clinical_justification: str
    insurance_carrier: str
    insurance_address: str
    request_date: str = ""
    
    def __post_init__(self):
        if not self.request_date:
            self.request_date = datetime.now().strftime("%B %d, %Y")


class PriorAuthLetterGenerator:
    """Generator for prior authorization letters."""
    
    SERVICE_TEMPLATES = {
        "procedure": {
            "title": "Prior Authorization Request - Medical Procedure",
            "intro_phrase": "is medically necessary to treat the patient's condition",
        },
        "medication": {
            "title": "Prior Authorization Request - Prescription Medication", 
            "intro_phrase": "is medically necessary and appropriate for this patient's condition",
        },
        "dme": {
            "title": "Prior Authorization Request - Durable Medical Equipment",
            "intro_phrase": "is medically necessary for the patient's daily functioning and care",
        },
        "imaging": {
            "title": "Prior Authorization Request - Advanced Imaging",
            "intro_phrase": "is medically necessary for accurate diagnosis and treatment planning",
        },
    }
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or os.path.join(
            os.path.dirname(__file__), "..", "references"
        )
    
    def generate_letter(self, request: PriorAuthRequest) -> str:
        """Generate a prior authorization letter as formatted text."""
        template = self.SERVICE_TEMPLATES.get(
            request.service_type, self.SERVICE_TEMPLATES["procedure"]
        )
        
        letter_parts = []
        
        # Header
        letter_parts.extend([
            request.provider_name,
            request.provider_address,
            f"Phone: {request.provider_phone}",
            f"NPI: {request.provider_npi}",
            "",
            request.request_date,
            "",
            request.insurance_carrier,
            request.insurance_address,
            "",
            "RE: Prior Authorization Request",
            f"Patient: {request.patient_name}",
            f"Member ID: {request.patient_id}",
            f"Date of Birth: {request.patient_dob}",
            "",
            "-" * 60,
            "",
        ])
        
        # Body
        letter_parts.extend([
            f"To Whom It May Concern:",
            "",
            f"I am writing to request prior authorization for the following service:",
            "",
            f"Service: {request.service_description}",
        ])
        
        if request.cpt_code:
            letter_parts.append(f"CPT/HCPCS Code: {request.cpt_code}")
        
        letter_parts.extend([
            f"ICD-10 Diagnosis Code(s): {', '.join(request.icd10_codes)}",
            "",
            "CLINICAL JUSTIFICATION:",
            "",
        ])
        
        # Add clinical justification with proper formatting
        justification_lines = request.clinical_justification.strip().split('\n')
        for line in justification_lines:
            letter_parts.append(line)
        
        # Standard closing
        letter_parts.extend([
            "",
            f"Based on my clinical assessment, the requested {request.service_description} {template['intro_phrase']}. "
            "Alternative treatments have been considered and are not appropriate for this patient due to the specific clinical circumstances outlined above.",
            "",
            "Please contact my office if additional information is required to process this authorization request. "
            "I am available to discuss this case during normal business hours.",
            "",
            "Thank you for your prompt attention to this matter.",
            "",
            "Sincerely,",
            "",
            "",
            "_______________________________",
            f"{request.provider_name}, M.D.",
            f"NPI: {request.provider_npi}",
            "",
            "-" * 60,
            "",
            "Attachments: Clinical notes, Lab results, Supporting documentation (if applicable)",
        ])
        
        return '\n'.join(letter_parts)
    
    def save_letter(self, letter_text: str, output_path: str) -> str:
        """Save the letter to a file."""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(letter_text)
        
        return output_path
    
    def generate_from_json(self, json_path: str, output_path: str) -> str:
        """Generate letter from JSON input file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle icd10_codes as string or list
        icd10_codes = data.get('icd10_codes', data.get('icd10_code', []))
        if isinstance(icd10_codes, str):
            icd10_codes = [code.strip() for code in icd10_codes.split(',')]
        
        request = PriorAuthRequest(
            patient_name=data['patient_name'],
            patient_id=data['patient_id'],
            patient_dob=data.get('patient_dob', ''),
            provider_name=data['provider_name'],
            provider_npi=data['provider_npi'],
            provider_address=data.get('provider_address', ''),
            provider_phone=data.get('provider_phone', ''),
            service_type=data.get('service_type', 'procedure'),
            service_description=data.get('service_description', data.get('service_type', '')),
            cpt_code=data.get('cpt_code'),
            icd10_codes=icd10_codes,
            clinical_justification=data.get('clinical_justification', data.get('justification', '')),
            insurance_carrier=data['insurance_carrier'],
            insurance_address=data.get('insurance_address', ''),
        )
        
        letter_text = self.generate_letter(request)
        return self.save_letter(letter_text, output_path)


def create_sample_input(output_path: str):
    """Create a sample input JSON file."""
    sample_data = {
        "patient_name": "John Smith",
        "patient_id": "INS123456789",
        "patient_dob": "1980-05-15",
        "provider_name": "Dr. Sarah Johnson",
        "provider_npi": "1234567890",
        "provider_address": "123 Medical Center Drive, Suite 200, City, State 12345",
        "provider_phone": "(555) 123-4567",
        "service_type": "procedure",
        "service_description": "Laparoscopic Cholecystectomy",
        "cpt_code": "47562",
        "icd10_codes": ["K80.20"],
        "clinical_justification": """The patient presents with symptomatic cholelithiasis with recurrent biliary colic. 

Key clinical findings:
- Multiple episodes of right upper quadrant pain over the past 3 months
- Ultrasound confirmed gallstones with no evidence of common bile duct obstruction
- Patient has failed conservative management with dietary modifications
- Pain episodes are increasingly frequent and severe, affecting quality of life
- No contraindications to laparoscopic approach

Surgical intervention is indicated to prevent complications including acute cholecystitis, pancreatitis, and bile duct obstruction.""",
        "insurance_carrier": "Blue Cross Blue Shield",
        "insurance_address": "Prior Authorization Department, P.O. Box 12345, City, State 12345"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate prior authorization request letters for insurance companies"
    )
    parser.add_argument(
        '--input', '-i',
        help='Path to JSON input file with patient and service details'
    )
    parser.add_argument(
        '--output', '-o',
        default='prior_auth_letter.txt',
        help='Output file path (default: prior_auth_letter.txt)'
    )
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create a sample input JSON file for reference'
    )
    parser.add_argument(
        '--sample-output',
        default='sample_input.json',
        help='Path for sample input file (used with --create-sample)'
    )
    
    args = parser.parse_args()
    
    if args.create_sample:
        path = create_sample_input(args.sample_output)
        print(f"Sample input file created: {path}")
        print("Edit this file with actual patient information and run again with --input")
        return 0
    
    if not args.input:
        print("Error: --input is required (or use --create-sample to generate a template)")
        parser.print_help()
        return 1
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    try:
        generator = PriorAuthLetterGenerator()
        output_path = generator.generate_from_json(args.input, args.output)
        print(f"Prior authorization letter generated: {output_path}")
        return 0
    except KeyError as e:
        print(f"Error: Missing required field in input file: {e}")
        print("Required fields: patient_name, patient_id, provider_name, provider_npi,")
        print("                  insurance_carrier, clinical_justification")
        return 1
    except Exception as e:
        print(f"Error generating letter: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
