#!/usr/bin/env python3
"""
Unit tests for prior-auth-letter-drafter
"""

import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    validate_input, generate_letter, generate_patient_section,
    generate_provider_section, generate_clinical_rationale,
    format_output, process_data
)


class TestInputValidation(unittest.TestCase):
    """Test input validation."""
    
    def setUp(self):
        self.valid_input = {
            "patient": {
                "name": "John Doe",
                "dob": "1980-05-15",
                "insurance_id": "ABC123456",
                "diagnosis": "Rheumatoid Arthritis"
            },
            "provider": {
                "name": "Dr. Sarah Smith",
                "npi": "1234567890",
                "phone": "555-0123",
                "fax": "555-0124"
            },
            "request": {
                "type": "medication",
                "name": "Adalimumab",
                "dosage": "40mg every 2 weeks",
                "duration": "12 months",
                "diagnosis_codes": ["M05.9"],
                "failed_therapies": ["Methotrexate", "Sulfasalazine"]
            }
        }
    
    def test_validate_input_valid(self):
        """Test with valid complete input."""
        is_valid, error_msg = validate_input(self.valid_input)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_validate_input_missing_patient_section(self):
        """Test missing patient section."""
        invalid_input = {
            "provider": self.valid_input["provider"],
            "request": self.valid_input["request"]
        }
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("patient", error_msg)
    
    def test_validate_input_missing_patient_name(self):
        """Test missing patient name."""
        invalid_input = self.valid_input.copy()
        invalid_input["patient"] = {
            "dob": "1980-05-15",
            "insurance_id": "ABC123456"
        }
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("name", error_msg)
    
    def test_validate_input_missing_provider_npi(self):
        """Test missing provider NPI."""
        invalid_input = self.valid_input.copy()
        invalid_input["provider"] = {
            "name": "Dr. Smith"
        }
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("npi", error_msg)
    
    def test_validate_input_missing_request_type(self):
        """Test missing request type."""
        invalid_input = self.valid_input.copy()
        invalid_input["request"] = {
            "name": "Adalimumab",
            "diagnosis_codes": ["M05.9"]
        }
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("type", error_msg)


class TestLetterGeneration(unittest.TestCase):
    """Test letter generation functions."""
    
    def setUp(self):
        self.patient = {
            "name": "John Doe",
            "dob": "1980-05-15",
            "insurance_id": "ABC123456",
            "diagnosis": "Rheumatoid Arthritis"
        }
        self.provider = {
            "name": "Dr. Sarah Smith",
            "npi": "1234567890",
            "phone": "555-0123",
            "fax": "555-0124"
        }
        self.request = {
            "type": "medication",
            "name": "Adalimumab",
            "dosage": "40mg every 2 weeks",
            "duration": "12 months",
            "diagnosis_codes": ["M05.9"],
            "failed_therapies": ["Methotrexate", "Sulfasalazine"],
            "clinical_notes": "Patient shows active disease despite therapy."
        }
    
    def test_generate_patient_section(self):
        """Test patient section generation."""
        result = generate_patient_section(self.patient)
        self.assertIn("John Doe", result)
        self.assertIn("1980-05-15", result)
        self.assertIn("ABC123456", result)
        self.assertIn("Rheumatoid Arthritis", result)
    
    def test_generate_provider_section(self):
        """Test provider section generation."""
        result = generate_provider_section(self.provider)
        self.assertIn("Dr. Sarah Smith", result)
        self.assertIn("1234567890", result)
        self.assertIn("555-0123", result)
        self.assertIn("555-0124", result)
    
    def test_generate_clinical_rationale_with_failed_therapies(self):
        """Test clinical rationale with failed therapies."""
        result = generate_clinical_rationale(self.request)
        self.assertIn("INADEQUATE RESPONSE", result)
        self.assertIn("Methotrexate", result)
        self.assertIn("Sulfasalazine", result)
        self.assertIn("CLINICAL ASSESSMENT", result)
    
    def test_generate_clinical_rationale_without_failed_therapies(self):
        """Test clinical rationale without failed therapies."""
        request = self.request.copy()
        request["failed_therapies"] = []
        result = generate_clinical_rationale(request)
        self.assertNotIn("INADEQUATE RESPONSE", result)
    
    def test_generate_complete_letter(self):
        """Test complete letter generation."""
        data = {
            "patient": self.patient,
            "provider": self.provider,
            "request": self.request,
            "include_references": True
        }
        result = generate_letter(data)
        
        self.assertIn("letter", result)
        self.assertIn("checklist", result)
        self.assertIn("PRIOR AUTHORIZATION REQUEST", result["letter"])
        self.assertIn("John Doe", result["letter"])
        self.assertIn("Adalimumab", result["letter"])
        self.assertIn("M05.9", result["letter"])
        self.assertIn("SUPPORTING LITERATURE", result["letter"])
        self.assertTrue(len(result["checklist"]) > 0)
    
    def test_generate_letter_without_references(self):
        """Test letter generation without guideline references."""
        data = {
            "patient": self.patient,
            "provider": self.provider,
            "request": self.request,
            "include_references": False
        }
        result = generate_letter(data)
        self.assertNotIn("SUPPORTING LITERATURE", result["letter"])


class TestOutputFormatting(unittest.TestCase):
    """Test output formatting."""
    
    def test_format_output_success(self):
        """Test successful output formatting."""
        result = {"letter": "test letter", "checklist": ["item1"]}
        output = format_output(result, success=True)
        
        self.assertEqual(output["status"], "success")
        self.assertIn("data", output)
        self.assertIn("metadata", output)
        self.assertIn("timestamp", output["metadata"])
        self.assertIn("version", output["metadata"])
    
    def test_format_output_error(self):
        """Test error output formatting."""
        error_msg = "Validation failed"
        output = format_output(error_msg, success=False)
        
        self.assertEqual(output["status"], "error")
        self.assertIn("error", output)
        self.assertIn("type", output["error"])
        self.assertIn("message", output["error"])
        self.assertIn("suggestion", output["error"])
    
    def test_process_data(self):
        """Test main processing function."""
        data = {
            "patient": {"name": "John", "dob": "1980-01-01", "insurance_id": "ABC"},
            "provider": {"name": "Dr. Smith", "npi": "123"},
            "request": {"type": "medication", "name": "Drug", "diagnosis_codes": ["Z00.0"]}
        }
        result = process_data(data)
        
        self.assertIn("letter", result)
        self.assertIn("checklist", result)
        self.assertIn("timestamp", result)


class TestChecklistGeneration(unittest.TestCase):
    """Test documentation checklist generation."""
    
    def test_checklist_with_medication(self):
        """Test checklist for medication request."""
        from main import generate_checklist
        request = {
            "type": "medication",
            "failed_therapies": ["Drug A", "Drug B"]
        }
        checklist = generate_checklist(request)
        
        self.assertTrue(len(checklist) > 0)
        self.assertTrue(any("Medication history" in item for item in checklist))
        self.assertTrue(any("failed" in item.lower() for item in checklist))
    
    def test_checklist_without_failed_therapies(self):
        """Test checklist without failed therapies."""
        from main import generate_checklist
        request = {
            "type": "medication",
            "failed_therapies": []
        }
        checklist = generate_checklist(request)
        
        self.assertFalse(any("failed" in item.lower() for item in checklist))


if __name__ == "__main__":
    unittest.main(verbosity=2)
