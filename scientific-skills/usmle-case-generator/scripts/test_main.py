#!/usr/bin/env python3
"""
Unit tests for USMLE Case Generator
"""

import unittest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import generate_case, format_case_template, generate_random_vitals, generate_patient_demographics
from main import CASE_TEMPLATES, DifficultyLevel, Specialty


class TestUSMLECaseGenerator(unittest.TestCase):
    """Test cases for USMLE Case Generator"""
    
    def test_generate_case_default(self):
        """Test case generation with default parameters"""
        result = generate_case()
        
        self.assertEqual(result["status"], "success")
        self.assertIn("case", result)
        self.assertIn("metadata", result["case"])
        self.assertIn("vignette", result["case"])
        self.assertIn("question", result["case"])
    
    def test_generate_case_with_specialty(self):
        """Test case generation with specified specialty"""
        result = generate_case(specialty="Cardiology")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["case"]["metadata"]["specialty"], "Cardiology")
    
    def test_generate_case_with_difficulty(self):
        """Test case generation with specified difficulty"""
        result = generate_case(difficulty="Step 1")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["case"]["metadata"]["difficulty"], "Step 1")
    
    def test_generate_case_invalid_specialty(self):
        """Test error handling for invalid specialty"""
        result = generate_case(specialty="InvalidSpecialty")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertEqual(result["error"]["type"], "invalid_specialty")
        self.assertIn("supported_specialties", result["error"])
    
    def test_case_structure(self):
        """Test that generated case has correct structure"""
        result = generate_case(specialty="Neurology")
        
        # Check metadata
        metadata = result["case"]["metadata"]
        self.assertIn("specialty", metadata)
        self.assertIn("difficulty", metadata)
        self.assertIn("topic", metadata)
        self.assertIn("generated_at", metadata)
        
        # Check vignette
        vignette = result["case"]["vignette"]
        self.assertIn("chief_complaint", vignette)
        self.assertIn("history_present_illness", vignette)
        self.assertIn("physical_examination", vignette)
        self.assertIn("vitals", vignette)
        self.assertIn("diagnostic_studies", vignette)
        
        # Check question
        question = result["case"]["question"]
        self.assertIn("stem", question)
        self.assertIn("options", question)
        self.assertEqual(len(question["options"]), 5)
        self.assertIn("correct_answer", question)
        self.assertIn("explanation", question)
        self.assertIn("learning_objectives", question)
    
    def test_all_specialties_available(self):
        """Test that all defined specialties have templates"""
        for specialty in Specialty:
            self.assertIn(specialty.value, CASE_TEMPLATES)
            self.assertGreater(len(CASE_TEMPLATES[specialty.value]), 0)
    
    def test_generate_multiple_cases_unique(self):
        """Test that multiple cases are different"""
        result1 = generate_case(specialty="Cardiology")
        result2 = generate_case(specialty="Cardiology")
        
        # Should have different content due to randomization
        self.assertNotEqual(
            result1["case"]["vignette"]["history_present_illness"],
            result2["case"]["vignette"]["history_present_illness"]
        )
    
    def test_format_case_template(self):
        """Test template formatting"""
        template = CASE_TEMPLATES["Cardiology"][0]
        result = format_case_template(template, "Cardiology", "Step 2")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["case"]["metadata"]["specialty"], "Cardiology")
        
        # Check that vitals are formatted
        vitals = result["case"]["vignette"]["vitals"]
        self.assertIn("BP", vitals)
        self.assertIn("HR", vitals)
    
    def test_random_vitals_format(self):
        """Test vitals generation format"""
        vitals = generate_random_vitals()
        
        self.assertIn("bp", vitals)
        self.assertIn("hr", vitals)
        self.assertIn("rr", vitals)
        self.assertIn("spo2", vitals)
        
        # Check BP format (e.g., "120/80")
        bp_parts = vitals["bp"].split("/")
        self.assertEqual(len(bp_parts), 2)
        self.assertTrue(bp_parts[0].isdigit())
        self.assertTrue(bp_parts[1].isdigit())
    
    def test_patient_demographics(self):
        """Test patient demographics generation"""
        age, gender = generate_patient_demographics()
        
        self.assertTrue(25 <= age <= 85)
        self.assertIn(gender, ["male", "female"])
    
    def test_question_options_format(self):
        """Test that options are properly formatted"""
        result = generate_case(specialty="Pulmonology")
        options = result["case"]["question"]["options"]
        
        # Each option should start with a letter (A-E)
        for i, option in enumerate(options):
            expected_letter = chr(65 + i)  # A, B, C, D, E
            self.assertTrue(option.startswith(f"{expected_letter}."))
    
    def test_correct_answer_valid(self):
        """Test that correct answer is one of the options"""
        result = generate_case(specialty="Emergency Medicine")
        correct = result["case"]["question"]["correct_answer"]
        options = result["case"]["question"]["options"]
        
        # Correct answer should be A, B, C, D, or E
        self.assertIn(correct, ["A", "B", "C", "D", "E"])
        
        # Should match one of the options
        option_letters = [opt[0] for opt in options]
        self.assertIn(correct, option_letters)
    
    def test_specialty_coverage(self):
        """Test all specialties can generate cases"""
        for specialty in Specialty:
            result = generate_case(specialty=specialty.value)
            self.assertEqual(result["status"], "success", f"Failed for {specialty.value}")
            self.assertEqual(result["case"]["metadata"]["specialty"], specialty.value)


class TestCommandLineInterface(unittest.TestCase):
    """Test command-line interface"""
    
    def test_cli_import(self):
        """Test that main module can be imported and has main function"""
        from main import main
        self.assertTrue(callable(main))


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity of case templates"""
    
    def test_all_templates_have_required_fields(self):
        """Test that all templates have required fields"""
        required_fields = [
            "template", "chief_complaint", "history", "physical",
            "vitals", "studies", "question", "options", "correct",
            "explanation", "learning_objectives"
        ]
        
        for specialty, templates in CASE_TEMPLATES.items():
            for template in templates:
                for field in required_fields:
                    self.assertIn(field, template, f"Missing {field} in {specialty}")
    
    def test_all_templates_have_five_options(self):
        """Test that all questions have exactly 5 options (A-E)"""
        for specialty, templates in CASE_TEMPLATES.items():
            for template in templates:
                self.assertEqual(len(template["options"]), 5, f"{specialty} template should have 5 options")


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
