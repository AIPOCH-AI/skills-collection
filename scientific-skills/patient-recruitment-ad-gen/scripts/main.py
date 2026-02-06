#!/usr/bin/env python3
"""
Patient Recruitment Ad Generator
Generates IRB/EC compliant patient recruitment advertisements for clinical trials.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Optional


def generate_headline(disease: str, phase: str, intervention: str) -> str:
    """Generate an ethical, compliant headline."""
    headlines = [
        f"Research Study for {disease}: Volunteers Needed",
        f"Clinical Trial Opportunity: {disease} Research",
        f"Participate in {disease} Research - Volunteers Wanted",
        f"Help Advance {disease} Treatment - Join Our Study",
    ]
    return headlines[0]


def generate_summary(disease: str, phase: str, intervention: str) -> str:
    """Generate study summary in plain language."""
    phase_desc = {
        "Phase I": "early-stage research to evaluate safety",
        "Phase II": "research to evaluate effectiveness and safety",
        "Phase III": "research comparing the treatment to standard care",
        "Phase IV": "post-approval research to gather additional information"
    }
    
    phase_text = phase_desc.get(phase, "clinical research")
    
    return (
        f"We are conducting {phase_text} for people with {disease}. "
        f"This study involves {intervention.lower()}. "
        f"Your participation may help advance medical knowledge and potentially "
        f"improve future treatments for {disease}."
    )


def generate_eligibility(population: str) -> str:
    """Generate eligibility section."""
    return (
        f"You may be eligible if you:\n"
        f"- Are {population}\n"
        f"- Are willing to follow study procedures\n"
        f"- Meet additional study-specific criteria (to be discussed with study staff)\n\n"
        f"Not everyone who volunteers will qualify. A screening visit will determine eligibility."
    )


def generate_procedures(duration: str, intervention: str) -> str:
    """Generate procedures section."""
    return (
        f"If you qualify and choose to participate:\n"
        f"- Time commitment: {duration}\n"
        f"- You will receive: {intervention}\n"
        f"- Regular health monitoring throughout the study\n"
        f"- All study-related procedures and visits are provided at no cost\n\n"
        f"Detailed information will be provided before you decide to participate."
    )


def generate_rights_protections(irb: str) -> str:
    """Generate rights and protections section."""
    return (
        f"Your Rights and Protections:\n"
        f"- Participation is completely voluntary\n"
        f"- You may withdraw from the study at any time without penalty\n"
        f"- Your decision will not affect your regular medical care\n"
        f"- Your personal information will be kept confidential\n"
        f"- The study is reviewed by an Institutional Review Board (IRB #: {irb})\n"
        f"- You will receive complete information before giving consent"
    )


def generate_risks_benefits() -> str:
    """Generate risks and benefits section."""
    return (
        f"Potential Risks and Benefits:\n"
        f"- The study treatment may or may not benefit you directly\n"
        f"- There may be side effects, which will be explained to you in detail\n"
        f"- You will be closely monitored for any adverse effects\n"
        f"- Your participation may contribute to medical knowledge that helps others\n"
        f"- Alternative treatments remain available to you"
    )


def generate_compensation(compensation: Optional[str]) -> str:
    """Generate compensation section."""
    if compensation:
        return (
            "Compensation:\n"
            "You may receive " + compensation + " for your time and travel. "
            "Details will be provided during the informed consent process."
        )
    return ""


def generate_contact(pi: str, contact: str, location: str) -> str:
    """Generate contact section."""
    return (
        f"For More Information:\n"
        f"Principal Investigator: {pi}\n"
        f"Location: {location}\n"
        f"Contact: {contact}\n\n"
        f"Questions about your rights as a research participant? "
        f"Contact the IRB at the number provided in the full informed consent document."
    )


def generate_ad(params: Dict[str, str]) -> str:
    """Generate complete recruitment advertisement."""
    
    sections = [
        ("=" * 60),
        generate_headline(
            params["disease_condition"],
            params["study_phase"],
            params["intervention_type"]
        ),
        ("=" * 60),
        "",
        "ABOUT THIS STUDY",
        "-" * 40,
        generate_summary(
            params["disease_condition"],
            params["study_phase"],
            params["intervention_type"]
        ),
        "",
        "WHO CAN PARTICIPATE",
        "-" * 40,
        generate_eligibility(params["target_population"]),
        "",
        "WHAT'S INVOLVED",
        "-" * 40,
        generate_procedures(
            params["study_duration"],
            params["intervention_type"]
        ),
        "",
        "RISKS AND BENEFITS",
        "-" * 40,
        generate_risks_benefits(),
        "",
        "YOUR RIGHTS",
        "-" * 40,
        generate_rights_protections(params["irb_reference"]),
    ]
    
    # Add compensation if provided
    if params.get("compensation"):
        sections.extend([
            "",
            generate_compensation(params["compensation"])
        ])
    
    sections.extend([
        "",
        "CONTACT US",
        "-" * 40,
        generate_contact(
            params["pi_name"],
            params["contact_info"],
            params["site_location"]
        ),
        "",
        ("=" * 60),
        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
        "This is a research study. Not a treatment guarantee.",
        ("=" * 60),
    ])
    
    return "\n".join(sections)


def generate_json_output(params: Dict[str, str]) -> Dict:
    """Generate structured JSON output for programmatic use."""
    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "skill": "patient-recruitment-ad-gen"
        },
        "study": {
            "disease_condition": params["disease_condition"],
            "phase": params["study_phase"],
            "intervention": params["intervention_type"],
            "irb_reference": params["irb_reference"]
        },
        "content": {
            "headline": generate_headline(
                params["disease_condition"],
                params["study_phase"],
                params["intervention_type"]
            ),
            "summary": generate_summary(
                params["disease_condition"],
                params["study_phase"],
                params["intervention_type"]
            ),
            "eligibility": generate_eligibility(params["target_population"]),
            "procedures": generate_procedures(
                params["study_duration"],
                params["intervention_type"]
            ),
            "rights": generate_rights_protections(params["irb_reference"]),
            "risks_benefits": generate_risks_benefits(),
            "compensation": generate_compensation(params.get("compensation")),
            "contact": generate_contact(
                params["pi_name"],
                params["contact_info"],
                params["site_location"]
            )
        },
        "compliance_notes": [
            "Ensure IRB/EC approval before distribution",
            "Verify all information matches approved protocol",
            "Include IRB contact for questions about participant rights",
            "Do not modify without IRB/EC approval",
            "Keep copy of approved version for records"
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate IRB-compliant patient recruitment advertisements"
    )
    
    parser.add_argument("--disease", required=True, help="Target disease/condition")
    parser.add_argument("--phase", required=True, 
                       choices=["Phase I", "Phase II", "Phase III", "Phase IV"],
                       help="Study phase")
    parser.add_argument("--intervention", required=True, 
                       help="Intervention type (drug, device, procedure, etc.)")
    parser.add_argument("--population", required=True, 
                       help="Target population description")
    parser.add_argument("--duration", required=True, 
                       help="Study duration and time commitment")
    parser.add_argument("--location", required=True, 
                       help="Study site location")
    parser.add_argument("--pi", required=True, 
                       help="Principal Investigator name")
    parser.add_argument("--contact", required=True, 
                       help="Contact information (phone/email)")
    parser.add_argument("--irb", required=True, 
                       help="IRB/EC approval number")
    parser.add_argument("--compensation", default=None,
                       help="Participant compensation (if any)")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON instead of formatted text")
    
    args = parser.parse_args()
    
    params = {
        "disease_condition": args.disease,
        "study_phase": args.phase,
        "intervention_type": args.intervention,
        "target_population": args.population,
        "study_duration": args.duration,
        "site_location": args.location,
        "pi_name": args.pi,
        "contact_info": args.contact,
        "irb_reference": args.irb,
        "compensation": args.compensation
    }
    
    if args.json:
        output = generate_json_output(params)
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(generate_ad(params))


if __name__ == "__main__":
    main()
