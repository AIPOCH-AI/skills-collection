#!/usr/bin/env python3
"""
eCRF Designer
Design clinical trial CRFs with proper validation rules.
"""

import argparse
import json


class eCRFDesigner:
    """Design electronic Case Report Forms."""
    
    FIELD_TYPES = {
        "text": {"validation": ["max_length", "regex"], "example": "Free text"},
        "number": {"validation": ["min", "max", "decimal_places"], "example": "123.45"},
        "integer": {"validation": ["min", "max"], "example": "42"},
        "date": {"validation": ["min_date", "max_date"], "example": "2024-01-15"},
        "choice": {"validation": ["options"], "example": "Single select"},
        "multichoice": {"validation": ["options", "max_selections"], "example": "Multi select"},
        "yesno": {"validation": [], "example": "Yes/No"},
        "calculated": {"validation": ["formula"], "example": "Auto-calculated"}
    }
    
    CRF_TEMPLATES = {
        "demographics": {
            "fields": [
                {"name": "subject_id", "type": "text", "required": True, "label": "Subject ID"},
                {"name": "birth_date", "type": "date", "required": True, "label": "Date of Birth"},
                {"name": "gender", "type": "choice", "options": ["Male", "Female", "Other"], "label": "Gender"},
                {"name": "race", "type": "choice", "options": ["Asian", "Black", "White", "Other"], "label": "Race"}
            ]
        },
        "adverse_event": {
            "fields": [
                {"name": "ae_description", "type": "text", "required": True, "label": "AE Description"},
                {"name": "severity", "type": "choice", "options": ["Mild", "Moderate", "Severe"], "label": "Severity"},
                {"name": "start_date", "type": "date", "required": True, "label": "Start Date"},
                {"name": "related", "type": "yesno", "label": "Related to Study Drug?"}
            ]
        },
        "efficacy": {
            "fields": [
                {"name": "visit_date", "type": "date", "required": True, "label": "Visit Date"},
                {"name": "tumor_size", "type": "number", "min": 0, "label": "Tumor Size (mm)"},
                {"name": "response", "type": "choice", "options": ["CR", "PR", "SD", "PD"], "label": "Response"}
            ]
        }
    }
    
    def generate_crf(self, template_name, custom_fields=None):
        """Generate CRF from template."""
        crf = {
            "form_name": template_name,
            "version": "1.0",
            "fields": []
        }
        
        if template_name in self.CRF_TEMPLATES:
            crf["fields"] = self.CRF_TEMPLATES[template_name]["fields"].copy()
        
        if custom_fields:
            crf["fields"].extend(custom_fields)
        
        return crf
    
    def add_validation(self, field, rules):
        """Add validation rules to field."""
        field["validation"] = rules
        return field
    
    def export_json(self, crf, output_file):
        """Export CRF to JSON."""
        with open(output_file, 'w') as f:
            json.dump(crf, f, indent=2)
    
    def print_crf(self, crf):
        """Print CRF structure."""
        print(f"\n{'='*60}")
        print(f"eCRF: {crf['form_name']} (v{crf['version']})")
        print(f"{'='*60}\n")
        
        for field in crf["fields"]:
            print(f"Field: {field['name']}")
            print(f"  Label: {field['label']}")
            print(f"  Type: {field['type']}")
            print(f"  Required: {field.get('required', False)}")
            if "options" in field:
                print(f"  Options: {', '.join(field['options'])}")
            print()
        
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="eCRF Designer")
    parser.add_argument("--template", "-t", choices=["demographics", "adverse_event", "efficacy"],
                       default="demographics", help="CRF template")
    parser.add_argument("--output", "-o", default="crf.json", help="Output file")
    parser.add_argument("--list-types", action="store_true", help="List field types")
    
    args = parser.parse_args()
    
    designer = eCRFDesigner()
    
    if args.list_types:
        print("\nAvailable field types:")
        for ftype, info in designer.FIELD_TYPES.items():
            print(f"  {ftype}: {info['example']}")
        return
    
    crf = designer.generate_crf(args.template)
    designer.print_crf(crf)
    designer.export_json(crf, args.output)
    print(f"CRF exported to: {args.output}")


if __name__ == "__main__":
    main()
