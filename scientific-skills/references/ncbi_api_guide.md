# NCBI BLAST API Guide

## API Endpoints

Base URL: `https://blast.ncbi.nlm.nih.gov/Blast.cgi`

## Request Commands

### Put Command (Submit Search)
Submit a new BLAST search request.

**Parameters:**
- `CMD=Put` - Required
- `PROGRAM` - BLAST program (blastn, blastp, blastx, tblastn, tblastx)
- `DATABASE` - Target database name
- `QUERY` - Query sequence
- `EXPECT` - E-value threshold (default: 10)
- `HITLIST_SIZE` - Max hits to return (default: 50)
- `FORMAT_TYPE` - Response format (HTML, Text, XML, JSON2)

**Example:**
```
CMD=Put&PROGRAM=blastn&DATABASE=nt&QUERY=ATGCGTACG
```

### Get Command (Retrieve Results)
Retrieve results using Request ID (RID).

**Parameters:**
- `CMD=Get` - Required
- `RID` - Request ID from Put command
- `FORMAT_TYPE` - Output format

**Example:**
```
CMD=Get&RID=ABCDEF123&FORMAT_TYPE=XML
```

### Delete Command (Cancel Search)
Cancel a running search.

**Parameters:**
- `CMD=Delete` - Required
- `RID` - Request ID to cancel

## Response Status

When checking search status, look for these indicators in the response:

- `Status=WAITING` - Search is in progress
- `Status=READY` - Search completed successfully
- `Status=FAILED` - Search failed
- `Status=UNKNOWN` - Invalid RID

## Rate Limiting

NCBI recommends:
- Maximum 1 request every 3 seconds
- Do not poll more frequently than every 10 seconds
- Use appropriate delays based on RTOE (Request Time of Execution)

## Error Handling

Common HTTP errors:
- `429 Too Many Requests` - Rate limit exceeded, wait before retry
- `500 Internal Server Error` - Server error, retry with backoff
- `502 Bad Gateway` - Temporary issue, retry after delay

## Output Formats

### XML (Recommended)
- Complete alignment data
- Structured parsing possible
- Supports all BLAST features

### JSON2
- Modern JSON format
- Easier parsing than XML
- Available for most programs

### Text
- Human-readable format
- Limited programmatic use
- Quick inspection

## Python Example

```python
import urllib.request
import urllib.parse
import time

# Submit search
params = {
    'CMD': 'Put',
    'PROGRAM': 'blastn',
    'DATABASE': 'nt',
    'QUERY': 'ATGCGTACGTAGCTAGCTAG',
    'FORMAT_TYPE': 'XML'
}
data = urllib.parse.urlencode(params).encode('utf-8')
req = urllib.request.Request('https://blast.ncbi.nlm.nih.gov/Blast.cgi', 
                              data=data, method='POST')
response = urllib.request.urlopen(req)
result = response.read().decode('utf-8')

# Extract RID
rid = result[result.find('RID = ') + 6:].split('\n')[0].strip()

# Poll for results
while True:
    time.sleep(10)
    check_params = {'CMD': 'Get', 'RID': rid}
    check_data = urllib.parse.urlencode(check_params).encode('utf-8')
    check_req = urllib.request.Request(url, data=check_data, method='POST')
    check_resp = urllib.request.urlopen(check_req)
    check_result = check_resp.read().decode('utf-8')
    if 'Status=READY' in check_result:
        break

# Retrieve results
get_params = {'CMD': 'Get', 'RID': rid, 'FORMAT_TYPE': 'XML'}
```

## NCBI Policies

- Include tool name and email in requests when possible
- Do not overwhelm the server with requests
- Cache results when appropriate
- Respect the Entrez Usage Guidelines: https://www.ncbi.nlm.nih.gov/home/about/policies/
