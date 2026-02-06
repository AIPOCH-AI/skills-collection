#!/usr/bin/env python3
"""Medical CV/Resume Builder - CV generation for medical professionals."""

import json

class MedicalCVBuilder:
    """Builds medical CVs."""
    
    def build(self, experiences: list, education: list, cv_type: str = "cv") -> dict:
        """Generate CV."""
        
        cv_sections = [
            "# CURRICULUM VITAE\n",
            "## EDUCATION",
        ]
        
        for edu in education:
            cv_sections.append(f"- {edu}")
        
        cv_sections.append("\n## EXPERIENCE")
        for exp in experiences:
            cv_sections.append(f"- {exp}")
        
        cv_markdown = "\n".join(cv_sections)
        
        return {
            "cv_markdown": cv_markdown,
            "sections": ["Education", "Experience"],
            "type": cv_type
        }

def main():
    builder = MedicalCVBuilder()
    result = builder.build(
        ["Resident Physician, 2020-2023", "Research Fellow, 2019-2020"],
        ["MD, Harvard Medical School", "BS, Biology"]
    )
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
