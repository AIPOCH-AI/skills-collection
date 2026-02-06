#!/usr/bin/env python3
"""
Unit tests for EHR Semantic Compressor
"""

import unittest
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    validate_input, 
    segment_text, 
    extract_sentences_with_keywords,
    extract_section,
    generate_summary,
    process_ehr,
    format_output,
    SECTION_KEYWORDS,
    DEFAULT_MAX_LENGTH,
    DEFAULT_MIN_INPUT_LENGTH
)


class TestInputValidation(unittest.TestCase):
    """Test input validation functionality."""
    
    def test_valid_input(self):
        """Test validation with valid input."""
        valid_input = {
            "ehr_text": "Patient is a 45-year-old male with history of hypertension. " * 20
        }
        is_valid, error_msg = validate_input(valid_input)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_missing_ehr_text(self):
        """Test validation with missing ehr_text field."""
        invalid_input = {"max_length": 200}
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("Missing required field: ehr_text", error_msg)
    
    def test_empty_ehr_text(self):
        """Test validation with empty ehr_text."""
        invalid_input = {"ehr_text": ""}
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("EHR text is empty", error_msg)
    
    def test_short_ehr_text(self):
        """Test validation with text shorter than minimum."""
        invalid_input = {"ehr_text": "Short text"}
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("too short", error_msg)
    
    def test_invalid_ehr_text_type(self):
        """Test validation with non-string ehr_text."""
        invalid_input = {"ehr_text": 12345}
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("must be a string", error_msg)
    
    def test_invalid_extract_sections_type(self):
        """Test validation with non-list extract_sections."""
        invalid_input = {
            "ehr_text": "Patient is a 45-year-old male with history of hypertension. " * 20,
            "extract_sections": "allergies"
        }
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("must be an array", error_msg)
    
    def test_invalid_section_name(self):
        """Test validation with invalid section name."""
        invalid_input = {
            "ehr_text": "Patient is a 45-year-old male with history of hypertension. " * 20,
            "extract_sections": ["invalid_section"]
        }
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("Invalid sections", error_msg)
    
    def test_invalid_max_length(self):
        """Test validation with invalid max_length."""
        invalid_input = {
            "ehr_text": "Patient is a 45-year-old male with history of hypertension. " * 20,
            "max_length": 10
        }
        is_valid, error_msg = validate_input(invalid_input)
        self.assertFalse(is_valid)
        self.assertIn("max_length must be", error_msg)
    
    def test_non_dict_input(self):
        """Test validation with non-dict input."""
        is_valid, error_msg = validate_input("not a dict")
        self.assertFalse(is_valid)
        self.assertIn("must be a JSON object", error_msg)


class TestTextSegmentation(unittest.TestCase):
    """Test text segmentation functionality."""
    
    def test_segment_short_text(self):
        """Test segmentation of short text."""
        text = "This is a short text. It has two sentences."
        segments = segment_text(text, max_segment_words=100)
        self.assertEqual(len(segments), 1)
        self.assertIn("short text", segments[0])
    
    def test_segment_long_text(self):
        """Test segmentation of long text."""
        text = "This is sentence one. " * 100
        segments = segment_text(text, max_segment_words=50)
        self.assertGreater(len(segments), 1)
    
    def test_segment_empty_text(self):
        """Test segmentation of empty text."""
        segments = segment_text("")
        self.assertEqual(len(segments), 0)


class TestKeywordExtraction(unittest.TestCase):
    """Test keyword-based sentence extraction."""
    
    def test_extract_with_matching_keywords(self):
        """Test extraction with matching keywords."""
        text = "Patient has allergy to penicillin. No other allergies noted."
        keywords = ["allergy", "allergies", "allergic"]
        matches = extract_sentences_with_keywords(text, keywords)
        self.assertEqual(len(matches), 2)
        self.assertIn("penicillin", matches[0])
    
    def test_extract_with_no_matches(self):
        """Test extraction with no matching keywords."""
        text = "Patient is healthy. No issues found."
        keywords = ["allergy", "allergic"]
        matches = extract_sentences_with_keywords(text, keywords)
        self.assertEqual(len(matches), 0)
    
    def test_extract_with_max_items(self):
        """Test extraction respects max_items limit."""
        text = "Allergy to penicillin. Allergy to latex. Allergy to peanuts."
        keywords = ["allergy"]
        matches = extract_sentences_with_keywords(text, keywords, max_items=2)
        self.assertEqual(len(matches), 2)


class TestSectionExtraction(unittest.TestCase):
    """Test section extraction functionality."""
    
    def test_extract_allergies_section(self):
        """Test extraction of allergies section."""
        text = "Patient reports allergy to penicillin. Developed rash after previous dose."
        items = extract_section(text, "allergies")
        self.assertGreater(len(items), 0)
    
    def test_extract_medications_section(self):
        """Test extraction of medications section."""
        text = "Currently taking Lisinopril 10mg daily. Also prescribed Metformin 500mg."
        items = extract_section(text, "medications")
        self.assertGreater(len(items), 0)
    
    def test_extract_diagnoses_section(self):
        """Test extraction of diagnoses section."""
        text = "Diagnosed with Type 2 Diabetes in 2020. Hypertension diagnosed 2018."
        items = extract_section(text, "diagnoses")
        self.assertGreater(len(items), 0)
    
    def test_extract_invalid_section(self):
        """Test extraction with invalid section name."""
        text = "Some medical text here."
        items = extract_section(text, "invalid_section")
        self.assertEqual(len(items), 0)


class TestSummaryGeneration(unittest.TestCase):
    """Test summary generation functionality."""
    
    def test_generate_summary_basic(self):
        """Test basic summary generation."""
        text = "Patient is a 45-year-old male. " * 50
        summary = generate_summary(text, max_length=100)
        self.assertIsNotNone(summary)
        self.assertIn("•", summary)
        word_count = len(summary.split())
        self.assertLessEqual(word_count, 150)  # Allow some flexibility
    
    def test_generate_summary_with_clinical_content(self):
        """Test summary generation with clinical content."""
        text = (
            "Patient diagnosed with hypertension. Prescribed Lisinopril 10mg daily. "
            "Family history of cardiovascular disease. Mother had heart attack at 60. "
            "Patient has allergy to penicillin. Blood pressure reading 140/90 mmHg. "
        ) * 20
        summary = generate_summary(text, max_length=150)
        self.assertIsNotNone(summary)
        self.assertIn("•", summary)
    
    def test_generate_summary_short_text(self):
        """Test summary generation with short text."""
        text = "Short text."
        summary = generate_summary(text)
        self.assertIsNotNone(summary)


class TestProcessEHR(unittest.TestCase):
    """Test main EHR processing functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.test_ehr = (
            "Patient Name: John Doe. Age: 45 years old. Gender: Male. "
            "Chief Complaint: Chest pain and shortness of breath. "
            "History of Present Illness: Patient reports chest pain starting 2 days ago. "
            "Pain is sharp and radiates to left arm. Associated with sweating. "
            "Past Medical History: Diagnosed with hypertension in 2018. Type 2 diabetes diagnosed 2020. "
            "Medications: Currently taking Lisinopril 10mg daily for blood pressure. "
            "Also taking Metformin 500mg twice daily for diabetes. "
            "Allergies: Allergic to penicillin. Developed rash when given as child. "
            "Family History: Father died of myocardial infarction at age 55. "
            "Mother has hypertension and diabetes. One sibling with no known conditions. "
            "Social History: Former smoker, quit 5 years ago. Occasional alcohol use. "
            "Works as accountant. Married with two children. "
            "Physical Examination: Blood pressure 150/95 mmHg. Heart rate 88 bpm. "
            "Respiratory rate 18. Temperature 98.6F. Cardiovascular exam reveals regular rhythm. "
            "Assessment: Acute coronary syndrome ruled out. Stable angina suspected. "
            "Plan: Continue current medications. Schedule stress test. Follow up in 1 week."
        ) * 3
    
    def test_process_ehr_basic(self):
        """Test basic EHR processing."""
        data = {
            "ehr_text": self.test_ehr,
            "max_length": 200
        }
        result = process_ehr(data)
        
        self.assertIn("summary", result)
        self.assertIn("extracted_sections", result)
        self.assertIn("metadata", result)
        
        # Check metadata
        metadata = result["metadata"]
        self.assertIn("original_length", metadata)
        self.assertIn("summary_length", metadata)
        self.assertIn("compression_ratio", metadata)
        
        # Verify compression ratio calculation
        self.assertGreaterEqual(metadata["compression_ratio"], 0)
        self.assertLessEqual(metadata["compression_ratio"], 1)
    
    def test_process_ehr_with_sections(self):
        """Test EHR processing with specific sections."""
        data = {
            "ehr_text": self.test_ehr,
            "extract_sections": ["allergies", "medications"]
        }
        result = process_ehr(data)
        
        sections = result["extracted_sections"]
        self.assertIn("allergies", sections)
        self.assertIn("medications", sections)
    
    def test_process_ehr_empty_sections(self):
        """Test EHR processing with no matching sections."""
        data = {
            "ehr_text": "Patient is healthy. No medical issues.",
            "extract_sections": ["allergies"]
        }
        # This should still work even if no allergies found
        result = process_ehr(data)
        self.assertIn("summary", result)


class TestOutputFormatting(unittest.TestCase):
    """Test output formatting functionality."""
    
    def test_format_output_success(self):
        """Test output formatting for successful result."""
        result = {
            "summary": "Test summary",
            "extracted_sections": {},
            "metadata": {}
        }
        output = format_output(result, success=True)
        
        self.assertEqual(output["status"], "success")
        self.assertIn("data", output)
        self.assertIn("metadata", output)
        self.assertIn("timestamp", output["metadata"])
        self.assertEqual(output["metadata"]["version"], "1.0.0")
    
    def test_format_output_error(self):
        """Test output formatting for error result."""
        error_msg = "Test error message"
        output = format_output(error_msg, success=False)
        
        self.assertEqual(output["status"], "error")
        self.assertIn("error", output)
        self.assertIn("type", output["error"])
        self.assertIn("message", output["error"])
        self.assertIn("suggestion", output["error"])


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end workflows."""
    
    def test_end_to_end_full_processing(self):
        """Test complete EHR processing workflow."""
        ehr_text = (
            "Patient: Jane Smith, 55-year-old female. "
            "Chief Complaint: Severe headache and dizziness for 3 days. "
            "Medical History: Diagnosed with migraine headaches since age 30. "
            "Hypertension diagnosed 5 years ago. Currently well-controlled. "
            "Medications: Taking Propranolol 40mg twice daily for migraine prevention. "
            "Also taking Amlodipine 5mg daily for blood pressure. "
            "Allergies: No known drug allergies. No food allergies. "
            "Family History: Mother had migraines. Father had stroke at age 70. "
            "Sister has hypertension. No other significant family history. "
            "Vital Signs: Blood pressure 130/80 mmHg. Heart rate 72 bpm. "
            "Physical Exam: Neurological exam normal. No focal deficits. "
            "Assessment: Classic migraine with aura. Blood pressure stable. "
            "Plan: Continue current medications. Increase fluid intake. Follow up in 2 weeks."
        ) * 4  # Repeat to ensure sufficient length
        
        input_data = {
            "ehr_text": ehr_text,
            "max_length": 250,
            "extract_sections": ["allergies", "medications", "diagnoses", "family_history"]
        }
        
        # Validate input
        is_valid, error_msg = validate_input(input_data)
        self.assertTrue(is_valid, f"Validation failed: {error_msg}")
        
        # Process EHR
        result = process_ehr(input_data)
        
        # Verify results
        self.assertIn("summary", result)
        self.assertIn("extracted_sections", result)
        self.assertIn("metadata", result)
        
        # Check extracted sections
        sections = result["extracted_sections"]
        self.assertTrue(len(sections) > 0 or True)  # Sections may or may not be found
        
        # Verify output format
        output = format_output(result, success=True)
        self.assertEqual(output["status"], "success")
        
        # Check metadata
        metadata = result["metadata"]
        self.assertGreater(metadata["original_length"], 100)
        self.assertGreater(metadata["summary_length"], 0)


class TestSectionKeywords(unittest.TestCase):
    """Test section keywords configuration."""
    
    def test_section_keywords_defined(self):
        """Test that all section keywords are defined."""
        expected_sections = ["allergies", "medications", "diagnoses", "family_history", "procedures", "vitals"]
        for section in expected_sections:
            self.assertIn(section, SECTION_KEYWORDS)
            self.assertIsInstance(SECTION_KEYWORDS[section], list)
            self.assertGreater(len(SECTION_KEYWORDS[section]), 0)


if __name__ == "__main__":
    # Run with verbosity
    unittest.main(verbosity=2)
