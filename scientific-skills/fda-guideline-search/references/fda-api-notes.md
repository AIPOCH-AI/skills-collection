# FDA API Documentation Notes

## Official FDA APIs

### 1. openFDA API
- **Base URL**: https://api.fda.gov
- **Documentation**: https://open.fda.gov/apis/
- **Scope**: Drug adverse events, labeling, recalls, enforcement reports
- **Guidelines**: Limited - does not contain full guidance documents

### 2. FDA Data Catalog
- **URL**: https://catalog.data.gov/organization/fda-gov
- **Format**: CKAN API
- **Scope**: Dataset metadata, not full-text documents

## Guidance Document Access

### Current Limitations
FDA does **not** currently provide a public REST API specifically for guidance documents. The recommended approach:

1. **Web Scraping** (implemented in this skill)
   - Parse HTML from https://www.fda.gov/drugs/guidance-compliance-regulatory-information/guidances-drugs
   - Respect rate limits (10 req/min)
   - Cache results locally

2. **FDA Email Updates**
   - Subscribe to guidance document updates
   - https://www.fda.gov/drugs/guidance-compliance-regulatory-information/guidances-drugs

3. **FDA RSS Feeds**
   - Available for new guidance announcements
   - XML format for automated processing

## ICH Guidelines Access

### ICH API
- **URL**: https://database.ich.org
- **Format**: Web interface with downloadable PDFs
- **API**: No public REST API available
- **Access**: Manual download or web scraping

## Authentication

### openFDA API
- No API key required for basic usage
- Rate limit: 1000 requests per day per IP
- Higher limits available with API key registration

### FDA Cloud
- Some datasets require authentication
- Not applicable to guidance documents

## Data Structure

### Guideline Document Fields
```json
{
  "document_number": "FDA-YYYY-D-NNNN",
  "title": "Guidance Title",
  "issue_date": "YYYY-MM-DD",
  "type": "Draft|Final|ICH",
  "therapeutic_area": "Area Name",
  "pdf_url": "https://...",
  "html_url": "https://...",
  "docket_number": "FDA-YYYY-D-NNNN",
  "contact": "division@fda.hhs.gov"
}
```

## Best Practices

1. **Caching**: Store downloaded PDFs locally
2. **Rate Limiting**: Never exceed 10 requests/minute
3. **Error Handling**: Handle 429 (rate limit) and 503 (unavailable) responses
4. **User-Agent**: Identify your application clearly
5. **Respect robots.txt**: Check before implementing scrapers

## Future Enhancements

Monitor FDA API announcements for:
- Official guidance document API
- Webhook support for new documents
- GraphQL endpoint for complex queries
- Bulk data downloads

## References

- FDA API Documentation: https://open.fda.gov/apis/
- FDA Developer Resources: https://www.fda.gov/forindustry/datastandards/
- ICH Guidelines Database: https://database.ich.org
