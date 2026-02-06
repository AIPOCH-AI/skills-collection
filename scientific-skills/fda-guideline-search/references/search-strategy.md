# FDA Guideline Search Strategy

## Data Sources

### Primary Sources
1. **FDA CDER Guidance Documents**
   - URL: https://www.fda.gov/drugs/guidance-compliance-regulatory-information/guidances-drugs
   - Contains drug development and review guidelines

2. **FDA CBER Guidance Documents**
   - URL: https://www.fda.gov/vaccines-blood-biologics/guidance-compliance-regulatory-information-biologics/guidances-biologics
   - Contains biologics and blood product guidelines

3. **ICH Guidelines**
   - URL: https://database.ich.org/home
   - International harmonized guidelines adopted by FDA

## Search Methodology

### 1. Therapeutic Area Mapping
- Normalize user input to standard therapeutic area names
- Use keyword expansion for comprehensive matching
- Support partial matches and aliases

### 2. Document Filtering
- By type: Draft, Final, ICH
- By date: Single year or date ranges
- By content: Full-text search within titles

### 3. Rate Limiting
- Maximum 10 requests per minute to FDA servers
- 6-second delay between requests
- Respect robots.txt and server response times

## Implementation Notes

### Current Approach
- Python script with urllib for HTTP requests
- Regex-based HTML parsing (for reliability)
- Local JSON caching
- Mock data structure for demonstration

### Production Enhancement Path
1. Use BeautifulSoup for robust HTML parsing
2. Implement FDA OpenFDA API integration
3. Add full-text indexing with SQLite/Elasticsearch
4. PDF text extraction for content search

## Known Limitations

1. FDA does not provide a comprehensive public API for all guidance documents
2. Some historical documents lack digital PDFs
3. Document numbering and URLs may change
4. ICH guidelines require separate database access

## Reference Links

- FDA Guidance Index: https://www.fda.gov/regulatory-information/search-fda-guidance-documents
- FDA Drug Guidance: https://www.fda.gov/drugs/guidance-compliance-regulatory-information/guidances-drugs
- ICH Guidelines: https://database.ich.org/home
