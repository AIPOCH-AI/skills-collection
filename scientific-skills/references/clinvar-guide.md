# ClinVar Database Guide

## Overview
ClinVar is a freely accessible, public archive of reports of the relationships among human variations and phenotypes, with supporting evidence.

- **Website**: https://www.ncbi.nlm.nih.gov/clinvar/
- **Database**: NCBI
- **Access**: Web interface, FTP, API (E-utilities)

## API Access

### E-utilities Endpoints

```
ESearch: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar
ESummary: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar
EFetch: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=clinvar
```

### Rate Limits
- Without API key: 3 requests/second
- With API key: 10 requests/second

### Example Query
```bash
# Search for BRCA1 variants
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=BRCA1[Gene]&retmode=json"

# Get variant summary
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=1552&retmode=json"
```

## Clinical Significance Values

| Value | Description |
|-------|-------------|
| Pathogenic | Very strong evidence of pathogenicity |
| Likely pathogenic | Strong evidence (>90% certainty) |
| Uncertain significance | Insufficient evidence |
| Likely benign | Strong evidence of no pathogenicity |
| Benign | Very strong evidence of no pathogenicity |
| Conflicting interpretations | Different submitters disagree |
| drug response | Affects drug response |
| risk factor | Associated with increased risk |
| protective | Protects against disease |
| association | Associated but not necessarily causal |
| affects | Affects phenotype but not necessarily disease |
| other | Other significance |
| not provided | No significance provided |

## Review Status (Star Rating)

| Star Rating | Review Status |
|-------------|---------------|
| ★★★★ | Practice guideline |
| ★★★ | Reviewed by expert panel |
| ★★ | Criteria provided, multiple submitters, no conflicts |
| ★ | Criteria provided, single submitter OR conflicting interpretations |
| No stars | No criteria provided |

## Data Fields

### Core Fields
- **RS (dbSNP ID)**: Reference SNP cluster ID
- **Variation ID**: ClinVar unique identifier
- **Gene(s)**: Associated gene symbol(s)
- **Chromosome**: Chromosome location
- **Position**: Genomic position
- **Reference/Alternate**: Alleles
- **HGVS**: HGVS expressions

### Clinical Fields
- **Clinical Significance**: Pathogenicity classification
- **Review Status**: Evidence quality indicator
- **Last Evaluated**: Date of last assessment
- **Submissions**: Number of submitters
- **Conditions**: Associated diseases/phenotypes

### Evidence Fields
- **Allele Frequency**: Population frequency data
- **Origin**: Germline/Somatic/De novo/etc.
- **Citations**: Literature references
- **Functional Consequence**: Predicted effect

## File Formats

### VCF Format
ClinVar releases VCF files for download:
- GRCh37: `clinvar.vcf.gz`
- GRCh38: `clinvar.vcf.gz`

### VCF INFO Fields
```
ALLELEID: Allele ID
CLNSIG: Clinical significance
CLNREVSTAT: Review status
CLNDN: Disease name
CLNHGVS: HGVS expression
GENEINFO: Gene information
CLNSIGCONF: Conflicting significance
```

## FTP Download
```bash
# Download latest ClinVar VCF
wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
wget ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.tbi
```

## Important Notes

1. **Conflicting Interpretations**: Always check for conflicting classifications from different submitters
2. **Star Rating**: Higher stars = more reliable classification
3. **Date**: Check last evaluated date for currency
4. **Multiple Conditions**: A variant may be associated with multiple conditions
5. **Submission Count**: More submissions generally indicate more confidence

## Submitter Categories

| Category | Examples |
|----------|----------|
| Diagnostic Labs | GeneDx, Invitae, Ambry |
| Research Labs | OMIM, GeneReviews |
| Expert Panels | ClinGen, ENIGMA |
| Practice Guidelines | AMP/ASCO/CAP |

## Resources

- **ClinVar Help**: https://www.ncbi.nlm.nih.gov/clinvar/intro/
- **Submission Guide**: https://www.ncbi.nlm.nih.gov/clinvar/docs/submit/
- **FAQ**: https://www.ncbi.nlm.nih.gov/clinvar/docs/faq/
