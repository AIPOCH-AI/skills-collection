# NIH Data Management and Sharing Plan (DMSP) Template

**Source:** [NIH Data Management and Sharing Policy](https://sharing.nih.gov/data-management-and-sharing-policy)  
**Effective Date:** January 25, 2023  
**Version:** Final Policy

---

## Overview

This document provides the official template and guidance for preparing Data Management and Sharing Plans (DMSP) as required by the NIH Policy for Data Management and Sharing.

## Required Elements

NIH requires all six elements below to be addressed in a DMSP:

---

### 1. Data Type

**What to include:**
- Types and estimated amount of scientific data to be generated and/or used in the research
- Indicate whether existing data will be used
- Briefly describe the scientific data that will be shared
- List metadata, other relevant data, and any associated documentation that will be shared

**Key considerations:**
- NIH defines scientific data as "the recorded factual material commonly accepted in the scientific community as of sufficient quality to validate and replicate research findings"
- Describe data in sufficient detail for reviewers to understand what will be shared
- Include rationale for any scientific data that will not be shared

**Example language:**
```
This project will generate the following scientific data types:
- Raw sequencing reads (FASTQ format)
- Processed gene expression matrices
- Clinical metadata (de-identified)
- Analysis code and workflows

Estimated data volume: ~2 TB over the project period.

Data that will not be shared:
- Individual participant identifiers and direct identifiers per HIPAA Safe Harbor method
- Audio recordings of interviews (transcripts will be shared instead)
```

---

### 2. Related Tools, Software and/or Code

**What to include:**
- Tools and software needed to access and manipulate shared data
- Specialized tools or custom code developed for the project
- How to access the tools (open-source vs. proprietary)

**Key considerations:**
- Consider using open-source, widely available tools when possible
- If proprietary software is required, document version and licensing requirements
- Share custom code through public repositories (e.g., GitHub, Zenodo)

**Example language:**
```
Data will be accessible using standard bioinformatics tools including:
- R (v4.0+) with Bioconductor packages
- Python (v3.8+) with pandas, numpy, scipy
- Standard genome browsers (IGV, UCSC)

Custom analysis pipelines will be deposited in GitHub with DOI via Zenodo integration.
```

---

### 3. Standards

**What to include:**
- Standards to be applied to scientific data and metadata
- Data formats, terminologies/vocabularies, and ontologies
- Quality assurance/quality control procedures

**Key considerations:**
- Use community-accepted standards when available
- Document any departures from standard formats
- Include reference to specific standard versions

**Example language:**
```
Metadata Standards:
- Minimum Information About a Microarray Experiment (MIAME)
- Dublin Core metadata elements
- DataCite metadata schema

Data Formats:
- Raw data: FASTQ, BAM/CRAM
- Processed data: HDF5, TSV
- Metadata: JSON, XML

Ontologies:
- Gene Ontology (GO)
- Human Phenotype Ontology (HPO)
- NCI Thesaurus
```

---

### 4. Data Preservation, Access, and Associated Timelines

**What to include:**
- Repository(ies) where data will be archived
- How data will be findable (identifiers, metadata)
- When data will be made available
- Duration of data retention

**Key considerations:**
- Choose NIH-approved repositories when available
- Obtain persistent identifiers (DOIs, accession numbers)
- Data should be shared no later than the end of the award period (or at time of publication, whichever comes first)

**Example language:**
```
Repository Selection:
- Raw sequencing data: NCBI Sequence Read Archive (SRA)
- Processed data and metadata: GEO (Gene Expression Omnibus)
- Supplementary files: Figshare or Zenodo

Persistent Identifiers:
- DOIs will be obtained for all shared datasets
- SRA and GEO accession numbers will be referenced in publications

Timeline:
- Data will be shared no later than the end of the award period
- Data underlying publications will be shared at the time of publication
- Long-term preservation: Minimum 10 years per repository policies
```

---

### 5. Access, Distribution, or Reuse Considerations

**What to include:**
- Factors affecting subsequent access, distribution, or reuse
- Informed consent and privacy protections
- Restrictions imposed by agreements or laws
- Intellectual property considerations

**Key considerations:**
- Address informed consent for data sharing
- Describe de-identification procedures
- Document any data use agreements
- State licensing terms for reuse

**Example language:**
```
Access Controls:
- Open access for de-identified summary data
- Controlled access for individual-level data via dbGaP
- Data Use Certification agreement required for controlled-access data

Privacy Protections:
- Data de-identified per HIPAA Safe Harbor method
- Limited dataset provisions applied where applicable
- IRB approval includes data sharing plans

Licensing:
- Data shared under CC0 1.0 Universal (public domain dedication)
- Software shared under MIT License
```

---

### 6. Oversight of Data Management and Sharing

**What to include:**
- Plan for compliance with DMSP
- Roles and responsibilities
- How often the plan will be reviewed/updated

**Key considerations:**
- Assign specific roles for data management
- Include budget considerations
- Plan for periodic review and updates

**Example language:**
```
Oversight Structure:
- Principal Investigator: Overall compliance and approval authority
- Data Manager: Day-to-day data management and repository submissions
- Project Coordinator: Documentation and training

Compliance Monitoring:
- Quarterly review of data management practices
- Annual update of the DMSP
- Version control for all plan updates

Budget:
- Data management costs included in grant budget
- Repository fees: ~$5,000 per year
- Data manager effort: 10% FTE
```

---

## FAIR Principles Alignment

NIH encourages alignment with FAIR principles:

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **F**indable | Data and metadata should be easy to find | Persistent identifiers, rich metadata, searchable repositories |
| **A**ccessible | Data should be accessible with clear protocols | Standard access procedures, authentication when needed |
| **I**nteroperable | Data should work with other data/tools | Standard formats, vocabularies, ontologies |
| **R**eusable | Data should be well-described for reuse | Clear licenses, detailed provenance, quality metrics |

---

## Repository Selection Guide

### NIH-Supported Domain-Specific Repositories

| Data Type | Recommended Repositories |
|-----------|-------------------------|
| Genomic/Sequencing | NCBI GEO, dbGaP, SRA, ENA, DDBJ |
| Imaging | BioImage Archive, Cell-IDR, TCIA |
| Proteomics | PRIDE, MassIVE, iProX |
| Metabolomics | MetaboLights, Metabolomics Workbench |
| Clinical Trials | ClinicalTrials.gov, Vivli, YODA |
| General | Dryad, Zenodo, Figshare, Mendeley Data |

### Repository Selection Criteria

1. **Domain relevance** - Specialized repositories provide better discoverability
2. **NIH approval** - Check NIH's list of approved repositories
3. **FAIR support** - Persistent IDs, rich metadata, standard formats
4. **Sustainability** - Long-term funding and organizational stability
5. **Access controls** - Ability to handle controlled-access if needed

---

## Common Acronyms

- **DMSP**: Data Management and Sharing Plan
- **FAIR**: Findable, Accessible, Interoperable, Reusable
- **DOI**: Digital Object Identifier
- **IRB**: Institutional Review Board
- **PI**: Principal Investigator
- **HIPAA**: Health Insurance Portability and Accountability Act
- **CC0**: Creative Commons Zero (public domain dedication)
- **CC-BY**: Creative Commons Attribution License

---

## Additional Resources

### NIH Resources
- [NIH Data Sharing Website](https://sharing.nih.gov/)
- [Selecting a Data Repository](https://sharing.nih.gov/data-management-and-sharing-policy/sharing-scientific-data/selecting-a-data-repository)
- [Writing a DMSP](https://sharing.nih.gov/data-management-and-sharing-policy/planning-and-budgeting-for-data-management-and-sharing/writing-a-data-management-and-sharing-plan)
- [Budgeting for DMS](https://sharing.nih.gov/data-management-and-sharing-policy/planning-and-budgeting-for-data-management-and-sharing/budgeting-for-data-management-and-sharing)

### External Resources
- [GO FAIR Initiative](https://www.go-fair.org/)
- [FORCE11 Data Citation Principles](https://force11.org/info/data-citation-principles-fair-data/)
- [Research Data Alliance](https://www.rd-alliance.org/)
- [re3data Registry](https://www.re3data.org/) (repository registry)

---

## Compliance Checklist

Before submitting your DMSP, verify:

- [ ] All 6 required elements are addressed
- [ ] Data types are clearly described with estimated amounts
- [ ] Repositories are specified and are NIH-approved
- [ ] Sharing timeline is specified
- [ ] Access restrictions (if any) are justified
- [ ] Metadata standards are identified
- [ ] Oversight responsibilities are assigned
- [ ] Budget considerations are addressed
- [ ] Plan aligns with FAIR principles
- [ ] Plan is realistic and feasible

---

*Last updated: 2023 (NIH Final Policy)*  
*For the most current guidance, visit https://sharing.nih.gov/*
