# ClinicalTrials.gov API v2 Documentation

## Overview

The ClinicalTrials.gov API v2 provides programmatic access to the ClinicalTrials.gov database containing registry and results information for clinical trials.

- **Base URL**: `https://clinicaltrials.gov/api/v2`
- **Documentation**: https://clinicaltrials.gov/data-api/api
- **Rate Limit**: 10 requests per second

## Authentication

No API key required. The API is publicly accessible.

## Key Endpoints

### Search Studies
```
GET /studies
```

Query Parameters:
- `pageSize`: Number of results (1-1000)
- `query.term`: Free text search
- `filter`: Structured filters

Filter Options:
- `sponsor:SponsorName` - Filter by sponsor
- `condition:ConditionName` - Filter by condition
- `overallStatus:STATUS` - Filter by status
- `phase:PHASE` - Filter by phase

### Get Study Details
```
GET /studies/{nctId}
```

Returns full protocol and results sections for a specific trial.

## Response Structure

### Study Object
```json
{
  "protocolSection": {
    "identificationModule": {
      "nctId": "NCT05108922",
      "briefTitle": "Study Title",
      "officialTitle": "Official Study Title"
    },
    "statusModule": {
      "overallStatus": "RECRUITING",
      "startDateStruct": {"date": "2022-01-15"},
      "completionDateStruct": {"date": "2024-12-31"},
      "statusVerifiedDate": "2024-01-15"
    },
    "sponsorCollaboratorsModule": {
      "leadSponsor": {"name": "Pfizer"}
    },
    "conditionsModule": {
      "conditions": ["Diabetes Mellitus", "Type 2"]
    },
    "designModule": {
      "phases": ["PHASE2", "PHASE3"],
      "enrollmentInfo": {"count": 500}
    }
  }
}
```

## Rate Limiting

- Maximum: 10 requests per second
- Recommended delay: 100-150ms between requests
- Exceeding limits returns HTTP 429

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Study not found |
| 429 | Rate limit exceeded |
| 500 | Server error |
