# References for Emerging Topic Scout

This directory contains API documentation, research papers, and resources related to trend detection in academic literature.

## Table of Contents

1. [API Documentation](#api-documentation)
2. [Research Papers](#research-papers)
3. [Related Tools](#related-tools)
4. [Datasets](#datasets)

---

## API Documentation

### bioRxiv API

The bioRxiv API provides programmatic access to preprint metadata.

**Base URL:** `https://api.biorxiv.org/`

**Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `/details/[server]/[interval]/[cursor]/[format]` | Get papers in date range |
| `/details/[server]/[DOI]/[format]` | Get specific paper by DOI |
| `/pub/[DOI]/[format]` | Get publication details |
| `/pub/[interval]/[cursor]/[format]` | Get published papers |

**Parameters:**
- `server`: `biorxiv` or `medrxiv`
- `interval`: `YEAR-MONTH` or `YEAR-MONTH-DAY/YEAR-MONTH-DAY`
- `cursor`: Pagination cursor (usually starts at 0)
- `format`: `json` or `xml`

**Example:**
```bash
curl "https://api.biorxiv.org/details/biorxiv/2026-02-01/2026-02-06/json"
```

**Response Format:**
```json
{
  "messages": [{"status": "ok", "count": 100}],
  "collection": [
    {
      "doi": "10.1101/2026.02.05.xxxxx",
      "title": "Paper Title",
      "authors": "Author A; Author B",
      "author_corresponding": "Author A",
      "author_corresponding_institution": "University",
      "date": "2026-02-05",
      "version": "1",
      "type": "new results",
      "license": "cc_by",
      "category": "neuroscience",
      "jatsxml": "https://...",
      "abstract": "Paper abstract...",
      "published": "NA"  // or journal reference if published
    }
  ]
}
```

### medRxiv API

Identical structure to bioRxiv API, with server parameter set to `medrxiv`.

**Base URL:** `https://api.medrxiv.org/`

### RSS Feeds

For real-time monitoring, RSS feeds are often more responsive:

- **bioRxiv Recent:** `https://www.biorxiv.org/rss/recent.rss`
- **bioRxiv by Category:** `https://www.biorxiv.org/rss/[category].rss`
- **medRxiv Recent:** `https://www.medrxiv.org/rss/recent.rss`

**Categories for bioRxiv:**
- animal-behavior-and-cognition
- biochemistry
- bioengineering
- bioinformatics
- biophysics
- cancer-biology
- cell-biology
- clinical-trials
- developmental-biology
- ecology
- epidemiology
- evolutionary-biology
- genetics
- genomics
- immunology
- microbiology
- molecular-biology
- neuroscience
- paleontology
- pathology
- pharmacology-and-toxicology
- physiology
- plant-biology
- scientific-communication-and-education
- synthetic-biology
- systems-biology
- zoology

---

## Research Papers

### Trend Detection in Scientific Literature

1. **"Detecting Emergent Research Trends in Scientific Literature"** (2019)
   - Authors: Athanasios Tsanas, Angeliki Xifara
   - Focus: Statistical methods for early detection of research trends
   - DOI: 10.1371/journal.pone.0214824

2. **"Predicting the Future Relevance of Research"** (2020)
   - Authors: Newman et al.
   - Focus: Citation network analysis for impact prediction
   - DOI: 10.1073/pnas.1915766117

3. **"Early Detection of Emerging Research Areas"** (2018)
   - Authors: Small et al.
   - Focus: Citation bursts and emerging topics
   - DOI: 10.1002/asi.24054

### Preprint Analysis

4. **"The Preprint Ecosystem of bioRxiv"** (2022)
   - Authors: Abdill & Blekhman
   - Focus: Analysis of bioRxiv growth patterns
   - DOI: 10.1101/2022.04.01.486720

5. **"Tracking the Popularity and Outcomes of all bioRxiv Preprints"** (2021)
   - Authors: Fraser et al.
   - Focus: Preprint to publication patterns
   - DOI: 10.1101/515643

### Natural Language Processing for Scientific Text

6. **"SciBERT: A Pretrained Language Model for Scientific Text"** (2019)
   - Authors: Beltagy et al.
   - Focus: BERT model trained on scientific corpus
   - DOI: 10.18653/v1/D19-1371

7. **"BERTopic: Neural Topic Modeling with a Class-Based TF-IDF"** (2022)
   - Authors: Grootendorst
   - Focus: Transformer-based topic modeling
   - arXiv: 2203.05794

---

## Related Tools

### Academic Trend Tracking

| Tool | Description | URL |
|------|-------------|-----|
| **Altmetric** | Tracks online attention to research | https://www.altmetric.com |
| **Semantic Scholar** | AI-powered research tool | https://www.semanticscholar.org |
| **Dimensions** | Research analytics platform | https://www.dimensions.ai |
| **Paper Digest** | Automated research summaries | https://www.paper-digest.com |
| **Litmaps** | Visual literature mapping | https://www.litmaps.com |
| **Inciteful** | Citation network explorer | https://inciteful.xyz |
| **Open Knowledge Maps** | Visual topic discovery | https://openknowledgemaps.org |

### Twitter/X Academic Monitoring

| Tool | Description | URL |
|------|-------------|-----|
| **Followerwonk** | Twitter analytics | https://followerwonk.com |
| **Academic Twitter Lists** | Curated researcher lists | Search: "[field] Twitter list" |

### Preprint Servers

| Server | Focus | URL |
|--------|-------|-----|
| **bioRxiv** | Biology | https://www.biorxiv.org |
| **medRxiv** | Medicine | https://www.medrxiv.org |
| **arXiv** | Physics/CS/Math | https://arxiv.org |
| **ChemRxiv** | Chemistry | https://chemrxiv.org |
| **PsyArXiv** | Psychology | https://psyarxiv.com |
| **SocArXiv** | Social Sciences | https://osf.io/preprints/socarxiv |
| **Research Square** | General | https://www.researchsquare.com |

---

## Datasets

### Available for Research

1. **bioRxiv Metadata Dump**
   - Available through Crossref or direct API
   - Updated daily
   - License: CC-BY for most content

2. **Microsoft Academic Graph (MAG)**
   - Comprehensive scholarly data
   - Discontinued 2021 but archives available
   - Alternative: OpenAlex (https://openalex.org)

3. **OpenAlex**
   - Open catalog of scholarly communication
   - API available
   - URL: https://docs.openalex.org

4. **Semantic Scholar Open Research Corpus**
   - 200M+ papers
   - Available for download
   - URL: https://api.semanticscholar.org/corpus

---

## Algorithms & Methods

### Trend Detection Techniques

#### 1. Burst Detection
Detect sudden increases in term frequency:
```python
# Kleinberg's burst detection algorithm
# Parameters: s (burst state), gamma (transition cost)
```

#### 2. TF-IDF with Time Windows
Weight terms by recency:
```python
# Calculate TF-IDF for each time window
# Detect terms with increasing TF-IDF scores
```

#### 3. Citation Network Analysis
Detect emerging topics via citation patterns:
- Co-citation clustering
- Bibliographic coupling
- Citation burst detection

#### 4. Topic Modeling
- LDA (Latent Dirichlet Allocation)
- NMF (Non-negative Matrix Factorization)
- BERTopic (Transformer-based)

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Precision@k | Accuracy of top-k predictions |
| NDCG | Normalized Discounted Cumulative Gain |
| MAP | Mean Average Precision |
| F1-Score | Harmonic mean of precision and recall |

---

## Implementation Notes

### Rate Limiting

- **bioRxiv/medRxiv:** No explicit rate limits, but be respectful
- **Recommended:** 1 request per second
- **Batching:** Use date ranges to minimize requests

### Data Quality Considerations

1. **Duplicate Detection:** Papers may appear multiple times (versions, cross-posts)
2. **Author Disambiguation:** Same author may be written differently
3. **Category Assignment:** Not all papers have accurate categories
4. **Retractions:** Check for withdrawal notices

### Ethical Considerations

- Respect server resources (implement delays)
- Follow robots.txt guidelines
- Cache data appropriately
- Credit original sources
- Handle unpublished data responsibly

---

## Additional Resources

### Documentation
- bioRxiv API Guide: https://www.biorxiv.org/submit-a-manuscript
- Crossref REST API: https://github.com/CrossRef/rest-api-doc

### Communities
- r/bioinformatics (Reddit)
- Academic Twitter (#academicTwitter, #PhDChat)
- FOSDEM (Open Source scientific software)

### Tutorials
- "Mining Scientific Articles with Python" - Various blog posts
- "Text Mining for Biology" - EBI Training

---

## Updates

Last updated: 2026-02-06

To suggest additions, update the relevant section and increment the version.
