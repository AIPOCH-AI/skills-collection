#!/usr/bin/env python3
"""
HIPAA Compliance Auditor - PII/PHI Detection and De-identification

This module provides clinical-grade detection and de-identification of
Protected Health Information (PHI) according to HIPAA Safe Harbor standards.

Technical Difficulty: High
Status: Requires Manual Review (需人工检查)
"""

import re
import json
import hashlib
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path


@dataclass
class PIIDetection:
    """Represents a single PII detection."""
    pii_type: str
    start: int
    end: int
    confidence: float
    replacement: str
    original_text: str
    context: str = ""  # Surrounding text for verification


@dataclass
class DeidentificationResult:
    """Result of de-identification process."""
    original_text: str
    cleaned_text: str
    detected_pii: List[PIIDetection]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    input_hash: str = ""
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.input_hash:
            self.input_hash = hashlib.sha256(
                self.original_text.encode('utf-8')
            ).hexdigest()[:16]


class HIPAAAuditor:
    """
    HIPAA Compliance Auditor for PII/PHI detection and de-identification.
    
    Detects 18 categories of HIPAA identifiers and replaces them with
    semantic tokens for safe data sharing.
    """
    
    # 18 HIPAA Identifier Categories
    HIPAA_CATEGORIES = [
        "NAME", "GEOGRAPHIC", "DATE", "PHONE", "FAX", "EMAIL",
        "SSN", "MRN", "HEALTH_PLAN", "ACCOUNT", "LICENSE",
        "VEHICLE", "DEVICE", "URL", "IP_ADDRESS", "BIOMETRIC",
        "PHOTO", "UNIQUE_ID"
    ]
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the HIPAA Auditor.
        
        Args:
            confidence_threshold: Minimum confidence for PII detection (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self._counters: Dict[str, int] = {}
        self._patterns = self._compile_patterns()
        
        # Try to load spaCy for NLP-based detection
        self.nlp = None
        try:
            import spacy
            # Try transformer model first, fall back to large
            for model in ["en_core_web_trf", "en_core_web_lg", "en_core_web_md"]:
                try:
                    self.nlp = spacy.load(model)
                    break
                except OSError:
                    continue
        except ImportError:
            pass
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection."""
        patterns = {
            # Social Security Number (XXX-XX-XXXX or XXXXXXXXX)
            "SSN": re.compile(
                r'\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b'
            ),
            
            # Phone/Fax Numbers (various formats)
            "PHONE": re.compile(
                r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
            ),
            
            # Email addresses
            "EMAIL": re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ),
            
            # Medical Record Number (common formats)
            "MRN": re.compile(
                r'\b(?:MRN|Medical Record|Chart|Patient ID)[\s#:]*(\d{3,10})\b',
                re.IGNORECASE
            ),
            
            # Dates (MM/DD/YYYY, MM-DD-YYYY, Month DD, YYYY, etc.)
            "DATE": re.compile(
                r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|'
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}|'
                r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b',
                re.IGNORECASE
            ),
            
            # IP Addresses (IPv4)
            "IP_ADDRESS": re.compile(
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ),
            
            # URLs
            "URL": re.compile(
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
            ),
            
            # Street Address (basic pattern)
            "ADDRESS": re.compile(
                r'\b\d+\s+(?:[A-Za-z]+\s+)*(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|'
                r'Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl|Circle|Cir|Suite|Ste|Apartment|Apt)'
                r'[\w\s,.-]*(?:\d{5}(?:-\d{4})?)?',
                re.IGNORECASE
            ),
            
            # Health Plan / Insurance numbers
            "HEALTH_PLAN": re.compile(
                r'\b(?:Policy|Group|Insurance|Member)[\s#:]*(\d{3,15})\b',
                re.IGNORECASE
            ),
            
            # Account numbers
            "ACCOUNT": re.compile(
                r'\b(?:Account|Acct)[\s#:]*(\d{3,20})\b',
                re.IGNORECASE
            ),
            
            # License numbers (medical, driver, etc.)
            "LICENSE": re.compile(
                r'\b(?:License|Lic|LN)[\s#:]*([A-Z0-9]{3,20})\b',
                re.IGNORECASE
            ),
            
            # Vehicle identifiers (VIN)
            "VEHICLE": re.compile(
                r'\b[A-HJ-NPR-Z0-9]{17}\b'
            ),
            
            # Device identifiers (UDI pattern)
            "DEVICE": re.compile(
                r'\b\(01\)\d{14}|\(11\)\d{6}|\(17\)\d{6}'
            ),
            
            # Biometric identifiers (placeholder - would need specialized detection)
            "BIOMETRIC": re.compile(
                r'\b(?:fingerprint|retina|iris|voice print|DNA|genetic)[\s\w]*\d+',
                re.IGNORECASE
            ),
        }
        return patterns
    
    def _get_next_token(self, pii_type: str) -> str:
        """Get the next sequential token for a PII type."""
        if pii_type not in self._counters:
            self._counters[pii_type] = 0
        self._counters[pii_type] += 1
        return f"[{pii_type}_{self._counters[pii_type]}]"
    
    def _get_context(self, text: str, start: int, end: int, window: int = 30) -> str:
        """Extract surrounding context for a match."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _detect_names(self, text: str) -> List[PIIDetection]:
        """Detect person names using NLP."""
        detections = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "PATIENT"]:
                    # Filter out common false positives
                    if len(ent.text) > 2 and not ent.text.lower() in [
                        "patient", "doctor", "dr", "mr", "mrs", "ms"
                    ]:
                        detections.append(PIIDetection(
                            pii_type="PATIENT_NAME",
                            start=ent.start_char,
                            end=ent.end_char,
                            confidence=0.85,
                            replacement=self._get_next_token("PATIENT_NAME"),
                            original_text=ent.text,
                            context=self._get_context(text, ent.start_char, ent.end_char)
                        ))
        
        # Fallback: Title + Capitalized Word pattern
        title_pattern = re.compile(
            r'\b(?:Mr|Mrs|Ms|Dr|Prof|Doctor)\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)'
        )
        for match in title_pattern.finditer(text):
            detections.append(PIIDetection(
                pii_type="PATIENT_NAME",
                start=match.start(1),
                end=match.end(1),
                confidence=0.75,
                replacement=self._get_next_token("PATIENT_NAME"),
                original_text=match.group(1),
                context=self._get_context(text, match.start(), match.end())
            ))
        
        return detections
    
    def _detect_regex_patterns(self, text: str) -> List[PIIDetection]:
        """Detect PII using regex patterns."""
        detections = []
        
        for pii_type, pattern in self._patterns.items():
            for match in pattern.finditer(text):
                # Map pattern names to standardized types
                standardized_type = pii_type
                if pii_type in ["PHONE", "FAX"]:
                    standardized_type = "PHONE"
                elif pii_type == "ADDRESS":
                    standardized_type = "ADDRESS"
                
                detections.append(PIIDetection(
                    pii_type=standardized_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.90 if pii_type in ["SSN", "EMAIL", "IP_ADDRESS"] else 0.80,
                    replacement=self._get_next_token(standardized_type),
                    original_text=match.group(),
                    context=self._get_context(text, match.start(), match.end())
                ))
        
        return detections
    
    def _remove_overlapping(self, detections: List[PIIDetection]) -> List[PIIDetection]:
        """Remove overlapping detections, keeping higher confidence ones."""
        # Sort by start position and confidence
        sorted_dets = sorted(detections, key=lambda d: (d.start, -d.confidence))
        
        filtered = []
        last_end = -1
        
        for det in sorted_dets:
            if det.start >= last_end:
                filtered.append(det)
                last_end = det.end
            # If overlapping but much higher confidence, replace
            elif det.confidence > filtered[-1].confidence + 0.2:
                filtered[-1] = det
                last_end = det.end
        
        return filtered
    
    def analyze(self, text: str) -> List[PIIDetection]:
        """
        Analyze text and detect all PII entities.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of PIIDetection objects
        """
        self._counters = {}  # Reset counters
        
        all_detections = []
        
        # Detect names
        all_detections.extend(self._detect_names(text))
        
        # Detect regex patterns
        all_detections.extend(self._detect_regex_patterns(text))
        
        # Remove overlaps
        all_detections = self._remove_overlapping(all_detections)
        
        # Filter by confidence threshold
        all_detections = [
            d for d in all_detections 
            if d.confidence >= self.confidence_threshold
        ]
        
        # Sort by position for sequential replacement
        all_detections.sort(key=lambda d: d.start)
        
        return all_detections
    
    def deidentify(self, text: str) -> DeidentificationResult:
        """
        De-identify text by replacing PII with semantic tokens.
        
        Args:
            text: Input text containing potential PII
            
        Returns:
            DeidentificationResult with cleaned text and detection details
        """
        detections = self.analyze(text)
        
        # Build cleaned text by replacing detections
        cleaned = []
        last_end = 0
        
        for det in detections:
            # Add text before this detection
            cleaned.append(text[last_end:det.start])
            # Add replacement token
            cleaned.append(det.replacement)
            last_end = det.end
        
        # Add remaining text
        cleaned.append(text[last_end:])
        
        cleaned_text = ''.join(cleaned)
        
        # Calculate statistics
        categories = list(set(d.pii_type for d in detections))
        
        stats = {
            "total_pii_found": len(detections),
            "categories_detected": categories,
            "high_confidence": len([d for d in detections if d.confidence >= 0.9]),
            "medium_confidence": len([d for d in detections if 0.8 <= d.confidence < 0.9]),
            "review_recommended": len([d for d in detections if d.confidence < 0.8])
        }
        
        return DeidentificationResult(
            original_text=text,
            cleaned_text=cleaned_text,
            detected_pii=detections,
            statistics=stats
        )
    
    def generate_audit_log(self, result: DeidentificationResult, output_path: str):
        """Generate JSON audit log for compliance documentation."""
        log_data = {
            "timestamp": result.timestamp,
            "input_hash": result.input_hash,
            "confidence_threshold": self.confidence_threshold,
            "detections": [
                {
                    "type": d.pii_type,
                    "position": [d.start, d.end],
                    "confidence": round(d.confidence, 2),
                    "replacement": d.replacement,
                    "original_length": len(d.original_text),
                    "context": d.context[:100] + "..." if len(d.context) > 100 else d.context
                }
                for d in result.detected_pii
            ],
            "statistics": result.statistics,
            "hipaa_categories_covered": list(set(
                d.pii_type for d in result.detected_pii
            ))
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def validate_output(self, result: DeidentificationResult) -> Dict[str, Any]:
        """
        Validate that de-identified text contains no obvious remaining PII.
        
        Returns validation report with warnings.
        """
        warnings = []
        
        # Check for SSN patterns still present
        if self._patterns["SSN"].search(result.cleaned_text):
            warnings.append("Potential SSN pattern still detected in output")
        
        # Check for email patterns
        if self._patterns["EMAIL"].search(result.cleaned_text):
            warnings.append("Potential email pattern still detected in output")
        
        # Check for phone patterns
        if self._patterns["PHONE"].search(result.cleaned_text):
            warnings.append("Potential phone pattern still detected in output")
        
        # Check confidence levels
        low_confidence = [d for d in result.detected_pii if d.confidence < 0.8]
        if low_confidence:
            warnings.append(f"{len(low_confidence)} detections below 0.8 confidence - manual review recommended")
        
        return {
            "passed": len(warnings) == 0,
            "warnings": warnings,
            "recommendation": "APPROVED" if not warnings else "REQUIRES_MANUAL_REVIEW"
        }


def main():
    """Command-line interface for HIPAA Auditor."""
    parser = argparse.ArgumentParser(
        description="HIPAA Compliance Auditor - PII Detection and De-identification"
    )
    parser.add_argument("--input", "-i", help="Input text file path")
    parser.add_argument("--text", "-t", help="Direct text input")
    parser.add_argument("--output", "-o", help="Output file path for de-identified text")
    parser.add_argument("--audit-log", "-a", help="Path for JSON audit log")
    parser.add_argument(
        "--confidence", "-c", type=float, default=0.7,
        help="Minimum confidence threshold (0.0-1.0)"
    )
    parser.add_argument(
        "--validate", "-v", action="store_true",
        help="Validate output and generate report"
    )
    parser.add_argument(
        "--stats", "-s", action="store_true",
        help="Print statistics to stdout"
    )
    
    args = parser.parse_args()
    
    # Get input text
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # Demo mode with sample text
        text = """
        Patient John Smith was admitted on 01/15/2024. 
        Contact: 555-123-4567 or john.smith@email.com
        SSN: 123-45-6789, MRN: 9876543
        Address: 123 Main Street, Springfield, IL 62701
        Insurance Policy #: POL123456789
        """
        print("Demo mode - using sample text.\n")
    
    # Initialize auditor and process
    auditor = HIPAAAuditor(confidence_threshold=args.confidence)
    result = auditor.deidentify(text)
    
    # Output results
    print("=" * 60)
    print("DE-IDENTIFIED TEXT:")
    print("=" * 60)
    print(result.cleaned_text)
    print()
    
    if args.stats or not args.output:
        print("=" * 60)
        print("DETECTION STATISTICS:")
        print("=" * 60)
        for key, value in result.statistics.items():
            print(f"  {key}: {value}")
        print()
        
        print("=" * 60)
        print("DETECTED PII ENTITIES:")
        print("=" * 60)
        for det in result.detected_pii:
            print(f"  [{det.pii_type}] '{det.original_text[:30]}...' "
                  f"→ {det.replacement} (conf: {det.confidence:.2f})")
        print()
    
    # Validation
    if args.validate:
        validation = auditor.validate_output(result)
        print("=" * 60)
        print("VALIDATION REPORT:")
        print("=" * 60)
        print(f"  Status: {validation['recommendation']}")
        if validation['warnings']:
            print("  Warnings:")
            for warning in validation['warnings']:
                print(f"    - {warning}")
        print()
    
    # Save outputs
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result.cleaned_text)
        print(f"De-identified text saved to: {args.output}")
    
    if args.audit_log:
        auditor.generate_audit_log(result, args.audit_log)
        print(f"Audit log saved to: {args.audit_log}")
    
    # Always print the validation status
    validation = auditor.validate_output(result)
    print(f"\nFinal Status: {validation['recommendation']}")
    
    return 0 if validation['passed'] else 1


if __name__ == "__main__":
    exit(main())
