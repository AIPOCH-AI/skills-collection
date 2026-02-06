#!/usr/bin/env python3
"""
DICOM Anonymizer - Batch anonymization of medical imaging data

This module provides clinical-grade anonymization of DICOM files,
removing patient identifiable information while preserving image data
for research use. Compliant with HIPAA Safe Harbor standards.

Technical Difficulty: High
Status: Requires Manual Review (需人工检查)
"""

import os
import re
import json
import hashlib
import argparse
import shutil
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Any, Set
from datetime import datetime
from pathlib import Path

# Try to import pydicom
try:
    import pydicom
    from pydicom import dcmread, dcmwrite
    from pydicom.dataset import Dataset, FileDataset
    from pydicom.uid import generate_uid
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False
    print("Warning: pydicom not installed. Install with: pip install pydicom")


@dataclass
class TagAnonymization:
    """Record of a single tag anonymization action."""
    tag: str
    attribute: str
    action: str  # 'cleared', 'hashed', 'replaced', 'preserved'
    original_value: str = ""
    new_value: str = ""


@dataclass
class AnonymizationResult:
    """Result of anonymizing a single DICOM file."""
    input_path: str
    output_path: str
    success: bool
    anonymized_tags: List[TagAnonymization] = field(default_factory=list)
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    original_patient_id_hash: str = ""
    pseudonym: str = ""
    statistics: Dict[str, Any] = field(default_factory=dict)


class DICOMAnonymizer:
    """
    DICOM Anonymizer for removing PHI from medical images.
    
    Anonymizes patient identifiable information from DICOM files while
    preserving essential imaging metadata for research use.
    """
    
    # Standard PHI DICOM Tags to anonymize
    # Format: (Group, Element): (AttributeName, Action)
    PHI_TAGS = {
        # Patient Information
        (0x0010, 0x0010): ("PatientName", "clear"),           # Patient's full name
        (0x0010, 0x0020): ("PatientID", "hash"),              # Patient ID
        (0x0010, 0x0030): ("PatientBirthDate", "clear"),      # Birth date
        (0x0010, 0x0032): ("PatientBirthTime", "clear"),      # Birth time
        (0x0010, 0x0050): ("PatientInsurancePlanCodeSequence", "clear"),
        (0x0010, 0x1000): ("OtherPatientIDs", "clear"),       # Other patient IDs
        (0x0010, 0x1001): ("OtherPatientNames", "clear"),     # Other patient names
        (0x0010, 0x1005): ("PatientBirthName", "clear"),      # Birth name
        (0x0010, 0x1060): ("PatientMotherBirthName", "clear"),# Mother's birth name
        (0x0010, 0x1080): ("MilitaryRank", "clear"),          # Military rank
        (0x0010, 0x1081): ("BranchOfService", "clear"),       # Branch of service
        (0x0010, 0x1090): ("MedicalRecordLocator", "clear"),  # Medical record locator
        (0x0010, 0x2160): ("EthnicGroup", "clear"),           # Ethnic group
        (0x0010, 0x2180): ("Occupation", "clear"),            # Occupation
        (0x0010, 0x21B0): ("AdditionalPatientHistory", "clear"),
        (0x0010, 0x21C0): ("PregnancyStatus", "clear"),
        (0x0010, 0x21D0): ("LastMenstrualDate", "clear"),
        (0x0010, 0x21F0): ("PatientReligiousPreference", "clear"),
        (0x0010, 0x4000): ("PatientComments", "clear"),       # Patient comments
        
        # Institution & Provider Information
        (0x0008, 0x0080): ("InstitutionName", "clear"),       # Institution name
        (0x0008, 0x0081): ("InstitutionAddress", "clear"),    # Institution address
        (0x0008, 0x0090): ("ReferringPhysicianName", "clear"),# Referring physician
        (0x0008, 0x0092): ("ReferringPhysicianAddress", "clear"),
        (0x0008, 0x0094): ("ReferringPhysicianTelephoneNumbers", "clear"),
        (0x0008, 0x1048): ("PhysiciansOfRecord", "clear"),    # Physicians of record
        (0x0008, 0x1049): ("PhysiciansOfRecordIdentificationSequence", "clear"),
        (0x0008, 0x1050): ("PerformingPhysicianName", "clear"),# Performing physician
        (0x0008, 0x1052): ("PerformingPhysicianIdentificationSequence", "clear"),
        (0x0008, 0x1060): ("NameOfPhysiciansReadingStudy", "clear"),
        (0x0008, 0x1062): ("PhysiciansReadingStudyIdentificationSequence", "clear"),
        (0x0008, 0x1070): ("OperatorsName", "clear"),         # Operators name
        (0x0008, 0x1072): ("OperatorIdentificationSequence", "clear"),
        (0x0008, 0x1120): ("ReferencedPatientSequence", "clear"),
        
        # Study Information
        (0x0008, 0x0050): ("AccessionNumber", "hash"),        # Accession number
        (0x0020, 0x0010): ("StudyID", "hash"),                # Study ID
        (0x0008, 0x1110): ("ReferencedStudySequence", "clear"),
        
        # Visit/Admission Information
        (0x0038, 0x0004): ("ReferencedPatientAliasSequence", "clear"),
        (0x0038, 0x0008): ("VisitStatusID", "clear"),
        (0x0038, 0x0010): ("AdmissionID", "clear"),           # Admission ID
        (0x0038, 0x0011): ("IssuerOfAdmissionID", "clear"),
        (0x0038, 0x0014): ("IssuerOfAdmissionIDSequence", "clear"),
        (0x0038, 0x0060): ("ServiceEpisodeID", "clear"),
        (0x0038, 0x0061): ("IssuerOfServiceEpisodeID", "clear"),
        (0x0038, 0x0062): ("ServiceEpisodeDescription", "clear"),
        (0x0038, 0x0400): ("PatientAddress", "clear"),        # Patient address
        (0x0038, 0x0500): ("PatientMotherAddress", "clear"),  # Mother's address
        
        # Scheduling Information
        (0x0032, 0x1032): ("RequestingPhysician", "clear"),   # Requesting physician
        (0x0032, 0x1033): ("RequestingService", "clear"),     # Requesting service
        (0x0040, 0x0006): ("ScheduledPerformingPhysicianName", "clear"),
        (0x0040, 0x0007): ("ScheduledProcedureStepDescription", "clear"),
        (0x0040, 0x000B): ("ScheduledPerformingPhysicianIdentificationSequence", "clear"),
        (0x0040, 0x0010): ("ScheduledStationName", "clear"),
        (0x0040, 0x0011): ("ScheduledProcedureStepLocation", "clear"),
        (0x0040, 0x0012): ("PreMedication", "clear"),
        (0x0040, 0x0275): ("RequestAttributesSequence", "clear"),
        (0x0040, 0x1001): ("RequestedProcedureID", "clear"),
        (0x0040, 0x1003): ("RequestedProcedurePriority", "clear"),
        
        # Device Information
        (0x0018, 0x1000): ("DeviceSerialNumber", "clear"),    # Device serial number
        (0x0018, 0x1002): ("DeviceUID", "clear"),             # Device UID
        (0x0018, 0x1004): ("PlateID", "clear"),               # Plate ID
        (0x0018, 0x1030): ("ProtocolName", "clear"),          # Protocol name
        (0x0008, 0x1010): ("StationName", "clear"),           # Station name
        (0x0008, 0x1140): ("ReferencedImageSequence", "clear"),
        
        # Results/Report Information
        (0x0008, 0x1068): ("InterpretationAuthor", "clear"),
        (0x4008, 0x0114): ("InterpretationApproverSequence", "clear"),
        (0x4008, 0x0115): ("InterpretationDiagnosisDescription", "clear"),
        (0x4008, 0x0116): ("InterpretationDiagnosisCodeSequence", "clear"),
        (0x4008, 0x0117): ("ResultsDistributionListSequence", "clear"),
        
        # Image Comments
        (0x0020, 0x4000): ("ImageComments", "clear"),         # Image comments
        (0x0040, 0x2400): ("ImagingServiceRequestComments", "clear"),
    }
    
    # Tags to preserve (essential imaging metadata)
    PRESERVE_TAGS = {
        (0x0010, 0x0040),  # PatientSex - demographic research
        (0x0010, 0x1010),  # PatientAge - calculated from birth date
        (0x0010, 0x1020),  # PatientSize
        (0x0010, 0x1030),  # PatientWeight
        (0x0008, 0x0060),  # Modality - CT, MR, etc.
        (0x0008, 0x0070),  # Manufacturer
        (0x0008, 0x1090),  # ManufacturerModelName
        (0x0018, 0x0020),  # ScanningSequence
        (0x0018, 0x0021),  # SequenceVariant
        (0x0018, 0x0023),  # MRAcquisitionType
        (0x0018, 0x0050),  # SliceThickness
        (0x0018, 0x0088),  # SpacingBetweenSlices
        (0x0018, 0x0091),  # EchoTrainLength
        (0x0018, 0x0093),  # PercentSampling
        (0x0018, 0x0094),  # PercentPhaseFieldOfView
        (0x0018, 0x0095),  # PixelBandwidth
        (0x0018, 0x1030),  # ProtocolName (can be preserved if generic)
        (0x0018, 0x1250),  # ReceiveCoilName
        (0x0018, 0x1251),  # TransmitCoilName
        (0x0018, 0x1310),  # AcquisitionMatrix
        (0x0018, 0x1312),  # InPlanePhaseEncodingDirection
        (0x0018, 0x1314),  # FlipAngle
        (0x0018, 0x1316),  # SAR
        (0x0018, 0x5100),  # PatientPosition
        (0x0020, 0x0011),  # SeriesNumber
        (0x0020, 0x0013),  # InstanceNumber
        (0x0020, 0x0032),  # ImagePositionPatient
        (0x0020, 0x0037),  # ImageOrientationPatient
        (0x0020, 0x1041),  # SliceLocation
        (0x0028, 0x0010),  # Rows
        (0x0028, 0x0011),  # Columns
        (0x0028, 0x0030),  # PixelSpacing
        (0x0028, 0x0100),  # BitsAllocated
        (0x0028, 0x0101),  # BitsStored
        (0x0028, 0x0102),  # HighBit
        (0x0028, 0x0103),  # PixelRepresentation
    }
    
    # UIDs that should be hashed (not regenerated) to maintain study linkage
    UID_TAGS = {
        (0x0020, 0x000D),  # StudyInstanceUID
        (0x0020, 0x000E),  # SeriesInstanceUID
        (0x0008, 0x1155),  # ReferencedSOPInstanceUID
    }
    
    def __init__(self, preserve_studies: bool = False, 
                 keep_tags: Optional[List[str]] = None,
                 remove_private: bool = True):
        """
        Initialize the DICOM Anonymizer.
        
        Args:
            preserve_studies: If True, maintain study/series relationships using pseudonyms
            keep_tags: List of tag names to preserve (override default anonymization)
            remove_private: Remove private (manufacturer-specific) tags
        """
        self.preserve_studies = preserve_studies
        self.keep_tags = set(keep_tags or [])
        self.remove_private = remove_private
        self._pseudonym_counter = 0
        self._uid_map: Dict[str, str] = {}  # Original UID -> Hashed UID mapping
        self._patient_map: Dict[str, str] = {}  # Original PatientID -> Pseudonym
        
    def _generate_pseudonym(self) -> str:
        """Generate a sequential pseudonym."""
        self._pseudonym_counter += 1
        return f"ANON_{self._pseudonym_counter:06d}"
    
    def _hash_string(self, value: str, length: int = 16) -> str:
        """Generate a deterministic hash for a string."""
        if not value:
            return ""
        hash_obj = hashlib.sha256(value.encode('utf-8'))
        return hash_obj.hexdigest()[:length].upper()
    
    def _hash_uid(self, uid: str) -> str:
        """Hash a UID while maintaining valid UID format."""
        if uid in self._uid_map:
            return self._uid_map[uid]
        
        # Generate a new valid DICOM UID based on hash
        hash_val = hashlib.sha256(uid.encode('utf-8')).hexdigest()[:32]
        # Use a research organization prefix (1.2.826.0.1.3680043.999 = Research Anon)
        new_uid = f"1.2.826.0.1.3680043.999.{int(hash_val[:16], 16) % 10000000000000000}"
        self._uid_map[uid] = new_uid
        return new_uid
    
    def _get_tag_name(self, tag: Tuple[int, int], dataset: Dataset) -> str:
        """Get the human-readable name for a DICOM tag."""
        try:
            elem = dataset[tag]
            return elem.keyword or f"Unknown_{tag[0]:04X}_{tag[1]:04X}"
        except:
            return f"Unknown_{tag[0]:04X}_{tag[1]:04X}"
    
    def _anonymize_tag(self, dataset: Dataset, tag: Tuple[int, int], 
                       action: str, tag_name: str) -> TagAnonymization:
        """Anonymize a single DICOM tag."""
        try:
            if tag not in dataset:
                return TagAnonymization(
                    tag=f"({tag[0]:04X},{tag[1]:04X})",
                    attribute=tag_name,
                    action="not_present",
                    original_value="",
                    new_value=""
                )
            
            original_value = str(dataset[tag].value) if dataset[tag].value else ""
            
            if tag_name in self.keep_tags:
                return TagAnonymization(
                    tag=f"({tag[0]:04X},{tag[1]:04X})",
                    attribute=tag_name,
                    action="preserved",
                    original_value="",
                    new_value=""
                )
            
            if action == "clear":
                new_value = "ANONYMOUS" if tag_name == "PatientName" else ""
                dataset[tag].value = new_value
                return TagAnonymization(
                    tag=f"({tag[0]:04X},{tag[1]:04X})",
                    attribute=tag_name,
                    action="cleared",
                    original_value=original_value[:50],  # Truncate for privacy
                    new_value=new_value
                )
            
            elif action == "hash":
                if tag in self.UID_TAGS and self.preserve_studies:
                    new_value = self._hash_uid(original_value)
                else:
                    new_value = self._hash_string(original_value)
                dataset[tag].value = new_value
                return TagAnonymization(
                    tag=f"({tag[0]:04X},{tag[1]:04X})",
                    attribute=tag_name,
                    action="hashed",
                    original_value="",
                    new_value=new_value
                )
            
            elif action == "replace":
                new_value = self._generate_pseudonym()
                dataset[tag].value = new_value
                return TagAnonymization(
                    tag=f"({tag[0]:04X},{tag[1]:04X})",
                    attribute=tag_name,
                    action="replaced",
                    original_value="",
                    new_value=new_value
                )
            
        except Exception as e:
            return TagAnonymization(
                tag=f"({tag[0]:04X},{tag[1]:04X})",
                attribute=tag_name,
                action=f"error: {str(e)}",
                original_value="",
                new_value=""
            )
    
    def _remove_private_tags(self, dataset: Dataset) -> int:
        """Remove private (manufacturer-specific) tags from dataset."""
        removed_count = 0
        private_tags = []
        
        for tag in dataset.keys():
            if tag.is_private:
                private_tags.append(tag)
        
        for tag in private_tags:
            try:
                del dataset[tag]
                removed_count += 1
            except:
                pass
        
        return removed_count
    
    def _calculate_patient_age(self, birth_date: str, study_date: str) -> Optional[int]:
        """Calculate patient age from birth date and study date."""
        try:
            from datetime import datetime
            # Parse dates (format: YYYYMMDD)
            birth = datetime.strptime(birth_date, "%Y%m%d")
            study = datetime.strptime(study_date, "%Y%m%d")
            age = int((study - birth).days / 365.25)
            return age
        except:
            return None
    
    def anonymize_file(self, input_path: str, output_path: str) -> AnonymizationResult:
        """
        Anonymize a single DICOM file.
        
        Args:
            input_path: Path to input DICOM file
            output_path: Path for anonymized output
            
        Returns:
            AnonymizationResult with details of the operation
        """
        if not HAS_PYDICOM:
            return AnonymizationResult(
                input_path=input_path,
                output_path=output_path,
                success=False,
                error_message="pydicom not installed. Install with: pip install pydicom"
            )
        
        result = AnonymizationResult(
            input_path=input_path,
            output_path=output_path,
            success=False,
            anonymized_tags=[]
        )
        
        try:
            # Read DICOM file
            dataset = dcmread(input_path)
            
            # Track original PatientID for audit
            original_patient_id = ""
            if (0x0010, 0x0020) in dataset:
                original_patient_id = str(dataset[0x0010, 0x0020].value or "")
                result.original_patient_id_hash = self._hash_string(original_patient_id, 32)
            
            # Generate or retrieve pseudonym
            if original_patient_id:
                if original_patient_id not in self._patient_map:
                    self._patient_map[original_patient_id] = self._generate_pseudonym()
                result.pseudonym = self._patient_map[original_patient_id]
            else:
                result.pseudonym = self._generate_pseudonym()
            
            # Calculate and store age before clearing birth date
            if (0x0010, 0x0030) in dataset and (0x0008, 0x0020) in dataset:
                birth_date = str(dataset[0x0010, 0x0030].value or "")
                study_date = str(dataset[0x0008, 0x0020].value or "")
                age = self._calculate_patient_age(birth_date, study_date)
                if age is not None:
                    dataset[0x0010, 0x1010] = age  # PatientAge
            
            # Anonymize PHI tags
            tags_anonymized = 0
            for tag, (tag_name, action) in self.PHI_TAGS.items():
                anon_record = self._anonymize_tag(dataset, tag, action, tag_name)
                if anon_record.action not in ["not_present", "preserved"]:
                    result.anonymized_tags.append(anon_record)
                    tags_anonymized += 1
            
            # Handle UIDs
            if self.preserve_studies:
                # Hash UIDs to maintain study linkage
                for tag in self.UID_TAGS:
                    if tag in dataset:
                        tag_name = self._get_tag_name(tag, dataset)
                        anon_record = self._anonymize_tag(dataset, tag, "hash", tag_name)
                        result.anonymized_tags.append(anon_record)
            else:
                # Generate new UIDs
                if (0x0020, 0x000D) in dataset:  # StudyInstanceUID
                    dataset[0x0020, 0x000D].value = generate_uid()
                if (0x0020, 0x000E) in dataset:  # SeriesInstanceUID
                    dataset[0x0020, 0x000E].value = generate_uid()
                if (0x0008, 0x0018) in dataset:  # SOPInstanceUID
                    dataset[0x0008, 0x0018].value = generate_uid()
            
            # Remove private tags
            private_removed = 0
            if self.remove_private:
                private_removed = self._remove_private_tags(dataset)
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save anonymized file
            dcmwrite(output_path, dataset)
            
            # Update statistics
            result.success = True
            result.statistics = {
                "total_tags_processed": len(self.PHI_TAGS),
                "phi_tags_anonymized": tags_anonymized,
                "private_tags_removed": private_removed,
                "image_data_preserved": True,
                "preserve_studies": self.preserve_studies
            }
            
        except Exception as e:
            result.error_message = str(e)
            result.success = False
        
        return result
    
    def anonymize_directory(self, input_dir: str, output_dir: str, 
                           recursive: bool = True) -> List[AnonymizationResult]:
        """
        Batch anonymize all DICOM files in a directory.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            recursive: Process subdirectories recursively
            
        Returns:
            List of AnonymizationResult for each file processed
        """
        results = []
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            return [AnonymizationResult(
                input_path=input_dir,
                output_path=output_dir,
                success=False,
                error_message=f"Input directory does not exist: {input_dir}"
            )]
        
        # Find all DICOM files
        dicom_extensions = {'.dcm', '.dicom', '.dic', '.img', ''}
        files_to_process = []
        
        if recursive:
            for ext in dicom_extensions:
                files_to_process.extend(input_path.rglob(f"*{ext}"))
        else:
            for ext in dicom_extensions:
                files_to_process.extend(input_path.glob(f"*{ext}"))
        
        # Also check files without extension for DICOM magic bytes
        all_files = set()
        if recursive:
            all_files = set(input_path.rglob("*"))
        else:
            all_files = set(input_path.glob("*"))
        
        for f in all_files:
            if f.is_file() and f not in files_to_process:
                try:
                    with open(f, 'rb') as fp:
                        magic = fp.read(132)
                        if len(magic) >= 132 and magic[128:132] == b'DICM':
                            files_to_process.append(f)
                except:
                    pass
        
        print(f"Found {len(files_to_process)} DICOM files to process")
        
        # Process each file
        for i, file_path in enumerate(files_to_process, 1):
            # Calculate relative path for output
            try:
                rel_path = file_path.relative_to(input_path)
            except ValueError:
                rel_path = file_path.name
            
            out_file = output_path / rel_path
            if not out_file.suffix:
                out_file = out_file.with_suffix('.dcm')
            
            print(f"[{i}/{len(files_to_process)}] Processing: {file_path.name}")
            
            result = self.anonymize_file(str(file_path), str(out_file))
            results.append(result)
        
        return results
    
    def generate_audit_log(self, results: List[AnonymizationResult], 
                          output_path: str):
        """Generate JSON audit log for compliance documentation."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "anonymizer_version": "1.0.0",
            "configuration": {
                "preserve_studies": self.preserve_studies,
                "remove_private": self.remove_private,
                "keep_tags": list(self.keep_tags)
            },
            "summary": {
                "total_files": len(results),
                "successful": len([r for r in results if r.success]),
                "failed": len([r for r in results if not r.success]),
                "unique_patients": len(set(r.pseudonym for r in results if r.pseudonym))
            },
            "files": [
                {
                    "input_path": r.input_path,
                    "output_path": r.output_path,
                    "success": r.success,
                    "pseudonym": r.pseudonym,
                    "original_patient_id_hash": r.original_patient_id_hash,
                    "tags_anonymized": len(r.anonymized_tags),
                    "statistics": r.statistics,
                    "error_message": r.error_message if not r.success else ""
                }
                for r in results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"Audit log saved: {output_path}")


def main():
    """Command-line interface for DICOM Anonymizer."""
    parser = argparse.ArgumentParser(
        description="DICOM Anonymizer - Remove PHI from medical images"
    )
    parser.add_argument("--input", "-i", required=True,
                       help="Input DICOM file or directory path")
    parser.add_argument("--output", "-o", required=True,
                       help="Output DICOM file or directory path")
    parser.add_argument("--batch", "-b", action="store_true",
                       help="Enable batch/directory processing")
    parser.add_argument("--preserve-studies", action="store_true",
                       help="Maintain study relationships with pseudonyms")
    parser.add_argument("--keep-tags", type=str,
                       help="Comma-separated list of tags to preserve")
    parser.add_argument("--remove-private", action="store_true", default=True,
                       help="Remove private/unknown tags")
    parser.add_argument("--audit-log", "-a",
                       help="Path for JSON audit log")
    parser.add_argument("--overwrite", action="store_true",
                       help="Overwrite existing output files")
    
    args = parser.parse_args()
    
    # Parse keep_tags
    keep_tags = None
    if args.keep_tags:
        keep_tags = [t.strip() for t in args.keep_tags.split(",")]
    
    # Initialize anonymizer
    anonymizer = DICOMAnonymizer(
        preserve_studies=args.preserve_studies,
        keep_tags=keep_tags,
        remove_private=args.remove_private
    )
    
    # Process
    if args.batch:
        results = anonymizer.anonymize_directory(args.input, args.output)
        
        # Print summary
        print("\n" + "=" * 60)
        print("BATCH ANONYMIZATION SUMMARY")
        print("=" * 60)
        print(f"Total files: {len(results)}")
        print(f"Successful: {len([r for r in results if r.success])}")
        print(f"Failed: {len([r for r in results if not r.success])}")
        
        # Show failures
        failures = [r for r in results if not r.success]
        if failures:
            print("\nFailed files:")
            for r in failures:
                print(f"  - {r.input_path}: {r.error_message}")
        
        # Generate audit log
        if args.audit_log:
            anonymizer.generate_audit_log(results, args.audit_log)
        
        return 0 if not failures else 1
    else:
        result = anonymizer.anonymize_file(args.input, args.output)
        
        print("\n" + "=" * 60)
        print("ANONYMIZATION RESULT")
        print("=" * 60)
        print(f"Input: {result.input_path}")
        print(f"Output: {result.output_path}")
        print(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
        
        if result.success:
            print(f"Pseudonym: {result.pseudonym}")
            print(f"Tags anonymized: {len(result.anonymized_tags)}")
            print("\nAnonymized tags:")
            for tag in result.anonymized_tags[:10]:  # Show first 10
                print(f"  {tag.tag} {tag.attribute}: {tag.action}")
            if len(result.anonymized_tags) > 10:
                print(f"  ... and {len(result.anonymized_tags) - 10} more")
            
            if result.statistics:
                print("\nStatistics:")
                for key, value in result.statistics.items():
                    print(f"  {key}: {value}")
        else:
            print(f"Error: {result.error_message}")
        
        if args.audit_log:
            anonymizer.generate_audit_log([result], args.audit_log)
        
        return 0 if result.success else 1


if __name__ == "__main__":
    exit(main())
