#!/usr/bin/env python3
"""
Variant Annotation Module
Query and annotate gene variants from ClinVar and dbSNP databases.
Implements ACMG guidelines for pathogenicity classification.
"""

import json
import re
import time
import argparse
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from urllib.parse import quote
import urllib.request
import urllib.error


@dataclass
class ACMGClassification:
    """ACMG classification result for a variant."""
    criteria: List[str] = field(default_factory=list)
    score: float = 0.0
    classification: str = "Uncertain Significance"
    evidence_summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PopulationFrequency:
    """Population frequency data."""
    gnomad_genome_all: Optional[float] = None
    gnomad_exome_all: Optional[float] = None
    gnomad_genome_afr: Optional[float] = None
    gnomad_genome_amr: Optional[float] = None
    gnomad_genome_eas: Optional[float] = None
    gnomad_genome_eur: Optional[float] = None
    gnomad_genome_sas: Optional[float] = None
    thousand_genomes_all: Optional[float] = None
    exac_all: Optional[float] = None


@dataclass
class FunctionalPrediction:
    """Functional prediction results."""
    sift: Optional[str] = None
    sift_score: Optional[float] = None
    polyphen2: Optional[str] = None
    polyphen2_score: Optional[float] = None
    cadd_score: Optional[float] = None
    mutation_taster: Optional[str] = None
    revel_score: Optional[float] = None


@dataclass
class DiseaseAssociation:
    """Disease association from ClinVar."""
    disease: str
    medgen_id: Optional[str] = None
    omim_id: Optional[str] = None
    significance: str = "Uncertain Significance"
    review_status: str = ""


@dataclass
class VariantAnnotation:
    """Complete variant annotation result."""
    # Identifiers
    variant_id: Optional[str] = None
    clinvar_id: Optional[str] = None
    gene: Optional[str] = None
    genes: List[str] = field(default_factory=list)
    
    # Genomic coordinates
    chromosome: Optional[str] = None
    position: Optional[int] = None
    ref_allele: Optional[str] = None
    alt_allele: Optional[str] = None
    build: str = "GRCh38"
    
    # HGVS notations
    hgvs_genomic: Optional[str] = None
    hgvs_cdna: Optional[str] = None
    hgvs_protein: Optional[str] = None
    
    # Clinical data
    clinical_significance: str = "Not Provided"
    clinvar_review_status: str = ""
    clinvar_star_rating: int = 0
    
    # ACMG classification
    acmg: ACMGClassification = field(default_factory=ACMGClassification)
    
    # Disease associations
    disease_associations: List[DiseaseAssociation] = field(default_factory=list)
    
    # Population data
    frequencies: PopulationFrequency = field(default_factory=PopulationFrequency)
    
    # Predictions
    predictions: FunctionalPrediction = field(default_factory=FunctionalPrediction)
    
    # Metadata
    literature_count: int = 0
    last_evaluated: Optional[str] = None
    submitted_variants: List[str] = field(default_factory=list)
    
    # Interpretation
    interpretation_summary: str = ""


class VariantAnnotator:
    """Main variant annotation class."""
    
    # ACMG scoring weights (Richards et al. 2015)
    ACMG_SCORES = {
        # Pathogenic evidence
        "PVS1": 8.0,
        "PS1": 4.0, "PS2": 4.0, "PS3": 4.0, "PS4": 4.0,
        "PM1": 2.0, "PM2": 2.0, "PM3": 2.0, "PM4": 2.0, "PM5": 2.0, "PM6": 2.0,
        "PP1": 1.0, "PP2": 1.0, "PP3": 1.0, "PP4": 1.0, "PP5": 1.0,
        # Benign evidence
        "BA1": -8.0,
        "BS1": -4.0, "BS2": -4.0, "BS3": -4.0, "BS4": -4.0,
        "BP1": -1.0, "BP2": -1.0, "BP3": -1.0, "BP4": -1.0, "BP5": -1.0, "BP6": -1.0, "BP7": -1.0,
    }
    
    # ClinVar star ratings
    STAR_RATINGS = {
        "practice guideline": 4,
        "reviewed by expert panel": 3,
        "criteria provided, multiple submitters, no conflicts": 2,
        "criteria provided, single submitter": 1,
        "criteria provided, conflicting interpretations": 1,
        "no criteria provided": 0,
    }
    
    def __init__(self, api_key: Optional[str] = None, delay: float = 0.34):
        """
        Initialize annotator.
        
        Args:
            api_key: NCBI API key for increased rate limits
            delay: Delay between API requests (default 0.34s = 3/sec)
        """
        self.api_key = api_key
        self.delay = delay
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()
    
    def _ncbi_request(self, url: str) -> Optional[Dict]:
        """Make NCBI API request with rate limiting and error handling."""
        self._rate_limit()
        
        if self.api_key:
            url = f"{url}&api_key={self.api_key}" if "?" in url else f"{url}?api_key={self.api_key}"
        
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "VariantAnnotator/1.0 (academic research)",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(1)
                return self._ncbi_request(url)
            return None
        except Exception:
            return None
    
    def _parse_variant_input(self, variant: str) -> Dict[str, Any]:
        """Parse variant input string into structured data."""
        variant = variant.strip()
        
        # rsID format
        rs_match = re.match(r'^(rs\d+)$', variant, re.IGNORECASE)
        if rs_match:
            return {"type": "rsid", "value": rs_match.group(1)}
        
        # HGVS cDNA format: NM_xxxx:x.c.y
        hgvs_c_match = re.match(r'^(NM_\d+\.?\d*):(c\..+)$', variant)
        if hgvs_c_match:
            return {"type": "hgvs_cdna", "transcript": hgvs_c_match.group(1), 
                    "change": hgvs_c_match.group(2)}
        
        # HGVS protein format
        hgvs_p_match = re.match(r'^(NP_\d+\.?\d*|p\..+)$', variant)
        if hgvs_p_match:
            return {"type": "hgvs_protein", "value": variant}
        
        # HGVS genomic format
        hgvs_g_match = re.match(r'^(NC_\d+\.?\d*):(g\..+)$', variant)
        if hgvs_g_match:
            return {"type": "hgvs_genomic", "value": variant}
        
        # VCF-style format: chr:pos:ref>alt or chr:pos ref>alt
        vcf_match = re.match(r'^(chr)?([\dXYM]+):(\d+)[:\s]([ACGTN]+)[>/]([ACGTN]+)$', variant, re.IGNORECASE)
        if vcf_match:
            return {
                "type": "vcf",
                "chrom": vcf_match.group(2),
                "pos": int(vcf_match.group(3)),
                "ref": vcf_match.group(4),
                "alt": vcf_match.group(5)
            }
        
        # Gene:AA format (e.g., BRCA1:R1699Q)
        gene_aa_match = re.match(r'^([A-Z0-9]+):([A-Z]\d+[A-Z*]?)$', variant, re.IGNORECASE)
        if gene_aa_match:
            return {"type": "gene_aa", "gene": gene_aa_match.group(1), "change": gene_aa_match.group(2)}
        
        return {"type": "unknown", "value": variant}
    
    def _query_clinvar(self, query: str) -> Optional[Dict]:
        """Query ClinVar database via NCBI E-utilities."""
        encoded_query = quote(query)
        
        # ESearch to get IDs
        search_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
            f"db=clinvar&term={encoded_query}&retmode=json&retmax=10"
        )
        
        search_result = self._ncbi_request(search_url)
        if not search_result or not search_result.get('esearchresult', {}).get('idlist'):
            return None
        
        ids = search_result['esearchresult']['idlist']
        if not ids:
            return None
        
        # ESummary to get details
        id_string = ','.join(ids[:5])  # Limit to top 5 results
        summary_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
            f"db=clinvar&id={id_string}&retmode=json"
        )
        
        return self._ncbi_request(summary_url)
    
    def _query_dbsnp(self, rsid: str) -> Optional[Dict]:
        """Query dbSNP database for allele frequency data."""
        encoded_query = quote(rsid)
        
        search_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
            f"db=snp&term={encoded_query}&retmode=json"
        )
        
        search_result = self._ncbi_request(search_url)
        if not search_result or not search_result.get('esearchresult', {}).get('idlist'):
            return None
        
        ids = search_result['esearchresult']['idlist']
        if not ids:
            return None
        
        summary_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
            f"db=snp&id={ids[0]}&retmode=json"
        )
        
        return self._ncbi_request(summary_url)
    
    def _calculate_acmg_score(self, clinvar_data: Dict, allele_freqs: Dict) -> ACMGClassification:
        """Calculate ACMG classification based on available evidence."""
        criteria = []
        score = 0.0
        evidence = {}
        
        # Extract key data
        clinical_sig = clinvar_data.get('clinical_significance', [])
        if isinstance(clinical_sig, str):
            clinical_sig = [clinical_sig]
        
        review_status = clinvar_data.get('review_status', '').lower()
        
        # PM2: Absent from controls (MAF < 0.0001)
        max_freq = 0.0
        for pop, freq in allele_freqs.items():
            if freq and freq > max_freq:
                max_freq = freq
        
        if max_freq < 0.0001:
            criteria.append("PM2")
            score += self.ACMG_SCORES["PM2"]
            evidence["PM2"] = f"Absent from population databases (max MAF: {max_freq:.2e})"
        elif max_freq > 0.05:
            criteria.append("BA1")
            score += self.ACMG_SCORES["BA1"]
            evidence["BA1"] = f"Common variant (MAF: {max_freq:.3f} > 5%)"
        elif max_freq > 0.01:
            criteria.append("BS1")
            score += self.ACMG_SCORES["BS1"]
            evidence["BS1"] = f"Allele frequency greater than expected ({max_freq:.3f})"
        
        # PP5/BP6: ClinVar classification
        if any('pathogenic' in s.lower() for s in clinical_sig):
            if 'expert panel' in review_status or 'practice guideline' in review_status:
                criteria.append("PP5")
                score += self.ACMG_SCORES["PP5"]
                evidence["PP5"] = "Reputable source (expert panel) reports pathogenic"
        elif any('benign' in s.lower() for s in clinical_sig):
            if 'expert panel' in review_status or 'practice guideline' in review_status:
                criteria.append("BP6")
                score += self.ACMG_SCORES["BP6"]
                evidence["BP6"] = "Reputable source (expert panel) reports benign"
        
        # PP3: Computational evidence
        predictions = clinvar_data.get('functional_predictions', {})
        damaging_count = sum(1 for p in ['sift', 'polyphen2'] 
                            if predictions.get(p) in ['deleterious', 'probably_damaging'])
        if damaging_count >= 2:
            criteria.append("PP3")
            score += self.ACMG_SCORES["PP3"]
            evidence["PP3"] = "Multiple computational predictions support pathogenicity"
        
        # Determine classification
        if score >= 10:
            classification = "Pathogenic"
        elif score >= 6:
            classification = "Likely Pathogenic"
        elif score <= -6:
            classification = "Benign"
        elif score <= -1:
            classification = "Likely Benign"
        else:
            classification = "Uncertain Significance"
        
        return ACMGClassification(
            criteria=criteria,
            score=score,
            classification=classification,
            evidence_summary=evidence
        )
    
    def query_variant(self, variant: str) -> Dict[str, Any]:
        """
        Query and annotate a single variant.
        
        Args:
            variant: Variant identifier (rsID, HGVS, VCF-style, etc.)
            
        Returns:
            Dictionary with complete variant annotation
        """
        annotation = VariantAnnotation()
        parsed = self._parse_variant_input(variant)
        
        # Set variant identifier
        if parsed["type"] == "rsid":
            annotation.variant_id = parsed["value"]
        elif parsed["type"] == "vcf":
            annotation.chromosome = parsed["chrom"]
            annotation.position = parsed["pos"]
            annotation.ref_allele = parsed["ref"]
            annotation.alt_allele = parsed["alt"]
        
        # Query ClinVar
        clinvar_result = self._query_clinvar(variant)
        
        if clinvar_result and clinvar_result.get('result'):
            # Process ClinVar data (simplified for this implementation)
            uids = list(clinvar_result['result'].keys())
            if uids:
                clinvar_data = clinvar_result['result'][uids[0]]
                annotation.clinvar_id = uids[0]
                
                # Extract clinical significance
                if 'clinical_significance' in clinvar_data:
                    sig = clinvar_data['clinical_significance']
                    if isinstance(sig, dict):
                        annotation.clinical_significance = sig.get('description', 'Not Provided')
                    else:
                        annotation.clinical_significance = sig
                
                # Extract review status and star rating
                if 'review_status' in clinvar_data:
                    annotation.clinvar_review_status = clinvar_data['review_status']
                    annotation.clinvar_star_rating = self.STAR_RATINGS.get(
                        clinvar_data['review_status'].lower(), 0
                    )
                
                # Extract genes
                if 'genes' in clinvar_data:
                    genes = clinvar_data['genes']
                    if isinstance(genes, list) and len(genes) > 0:
                        annotation.genes = [g.get('symbol', '') for g in genes if g.get('symbol')]
                        annotation.gene = annotation.genes[0] if annotation.genes else None
                
                # Extract HGVS
                if 'hgvs' in clinvar_data:
                    hgvs_list = clinvar_data['hgvs']
                    if isinstance(hgvs_list, list):
                        for hgvs in hgvs_list:
                            if ':c.' in hgvs:
                                annotation.hgvs_cdna = hgvs
                            elif ':g.' in hgvs:
                                annotation.hgvs_genomic = hgvs
                            elif ':p.' in hgvs:
                                annotation.hgvs_protein = hgvs
                
                # Extract diseases
                if 'trait_set' in clinvar_data:
                    traits = clinvar_data['trait_set']
                    if isinstance(traits, list):
                        for trait in traits:
                            if 'trait_name' in trait:
                                disease_assoc = DiseaseAssociation(
                                    disease=trait.get('trait_name', ''),
                                    significance=annotation.clinical_significance,
                                    review_status=annotation.clinvar_review_status
                                )
                                annotation.disease_associations.append(disease_assoc)
        
        # Query dbSNP for frequency data
        if annotation.variant_id:
            dbsnp_result = self._query_dbsnp(annotation.variant_id)
            if dbsnp_result and dbsnp_result.get('result'):
                uids = list(dbsnp_result['result'].keys())
                if uids:
                    snp_data = dbsnp_result['result'][uids[0]]
                    # Extract allele frequency if available
                    if 'allele_freq' in snp_data:
                        freqs = snp_data['allele_freq']
                        if isinstance(freqs, list) and len(freqs) > 0:
                            annotation.frequencies.thousand_genomes_all = float(freqs[0]) if freqs[0] else None
        
        # Calculate ACMG classification
        clinvar_dict = {
            'clinical_significance': [annotation.clinical_significance],
            'review_status': annotation.clinvar_review_status
        }
        allele_freq_dict = {
            'gnomad_all': annotation.frequencies.gnomad_genome_all,
            'thousand_genomes': annotation.frequencies.thousand_genomes_all
        }
        
        annotation.acmg = self._calculate_acmg_score(clinvar_dict, allele_freq_dict)
        
        # Generate interpretation summary
        annotation.interpretation_summary = self._generate_interpretation(annotation)
        
        return asdict(annotation)
    
    def _generate_interpretation(self, annotation: VariantAnnotation) -> str:
        """Generate human-readable interpretation summary."""
        parts = []
        
        # Variant description
        if annotation.gene:
            parts.append(f"Variant in {annotation.gene} gene")
        elif annotation.variant_id:
            parts.append(f"Variant {annotation.variant_id}")
        
        # Clinical significance
        if annotation.clinical_significance != "Not Provided":
            parts.append(f"has {annotation.clinical_significance} clinical significance in ClinVar")
            if annotation.clinvar_star_rating > 0:
                parts.append(f"({annotation.clinvar_star_rating} star rating)")
        
        # ACMG classification
        if annotation.acmg.classification != "Uncertain Significance":
            parts.append(f"ACMG classification: {annotation.acmg.classification}")
            if annotation.acmg.criteria:
                parts.append(f"(criteria: {', '.join(annotation.acmg.criteria)})")
        
        # Disease associations
        if annotation.disease_associations:
            diseases = [d.disease for d in annotation.disease_associations[:3]]
            parts.append(f"Associated with: {', '.join(diseases)}")
        
        return ". ".join(parts) if parts else "Insufficient data for interpretation."
    
    def batch_query(self, variants: List[str]) -> List[Dict[str, Any]]:
        """Query multiple variants."""
        results = []
        for variant in variants:
            result = self.query_variant(variant)
            results.append(result)
        return results


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Query and annotate genetic variants from ClinVar and dbSNP"
    )
    parser.add_argument(
        "--variant", "-v",
        help="Variant to query (rsID, HGVS, VCF-style, etc.)"
    )
    parser.add_argument(
        "--file", "-f",
        help="File containing list of variants (one per line)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (JSON format)"
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--api-key",
        help="NCBI API key for increased rate limits"
    )
    parser.add_argument(
        "--delay", type=float, default=0.34,
        help="Delay between API requests in seconds (default: 0.34)"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    annotator = VariantAnnotator(api_key=args.api_key, delay=args.delay)
    
    variants = []
    if args.variant:
        variants.append(args.variant)
    elif args.file:
        with open(args.file, 'r') as f:
            variants = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        print("Error: Provide --variant or --file")
        return 1
    
    results = annotator.batch_query(variants)
    
    # Format output
    if args.format == "json":
        output = json.dumps(results, indent=2, ensure_ascii=False)
    else:
        lines = []
        for result in results:
            lines.append(f"Variant: {result.get('variant_id', 'N/A')}")
            lines.append(f"  Gene: {result.get('gene', 'N/A')}")
            lines.append(f"  Clinical Significance: {result.get('clinical_significance', 'N/A')}")
            lines.append(f"  ACMG: {result.get('acmg', {}).get('classification', 'N/A')}")
            lines.append(f"  Interpretation: {result.get('interpretation_summary', 'N/A')}")
            lines.append("")
        output = "\n".join(lines)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    exit(main())
