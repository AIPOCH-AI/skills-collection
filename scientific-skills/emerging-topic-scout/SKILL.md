---
name: emerging-topic-scout
description: Monitor bioRxiv/medRxiv preprints and academic discussions to identify
  emerging research hotspots before they appear in mainstream journals
version: 1.0.0
category: General
tags: []
author: The King of Skills
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: The King of Skills
reviewer: ''
last_updated: '2026-02-06'
---

# Emerging Topic Scout

A real-time monitoring system for identifying "incubation period" research hotspots in biological and medical sciences before they are defined by mainstream journals.

## Overview

This skill continuously monitors:
- **bioRxiv**: Biology preprints via RSS/API
- **medRxiv**: Medicine preprints via RSS/API
- **Academic discussions**: Social media and forum mentions

It uses trend analysis algorithms to detect sudden spikes in topic frequency, cross-platform mentions, and emerging keyword clusters.

## Installation

```bash
cd /Users/z04030865/.openclaw/workspace/skills/emerging-topic-scout
pip install -r scripts/requirements.txt
```

## Usage

### Basic Scan

```bash
python scripts/main.py --sources biorxiv medrxiv --days 7 --output json
```

### Advanced Configuration

```bash
python scripts/main.py \
  --sources biorxiv medrxiv \
  --keywords "CRISPR,gene editing,long COVID" \
  --days 14 \
  --min-score 0.7 \
  --output markdown \
  --notify
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--sources` | list | `biorxiv,medrxiv` | Data sources to monitor |
| `--keywords` | string | (auto-detect) | Comma-separated keywords to track |
| `--days` | int | `7` | Lookback period in days |
| `--min-score` | float | `0.6` | Minimum trending score (0-1) |
| `--max-topics` | int | `20` | Maximum topics to return |
| `--output` | string | `markdown` | Output format: `json`, `markdown`, `csv` |
| `--notify` | flag | `false` | Send notification for high-priority topics |
| `--config` | path | `config.yaml` | Path to configuration file |

## Output Format

### JSON Output

```json
{
  "scan_date": "2026-02-06T05:57:00Z",
  "sources": ["biorxiv", "medrxiv"],
  "hot_topics": [
    {
      "topic": "gene editing therapy",
      "keywords": ["CRISPR", "base editing", "prime editing"],
      "trending_score": 0.89,
      "velocity": "rapid",
      "preprint_count": 34,
      "cross_platform_mentions": 127,
      "related_papers": [
        {
          "title": "New CRISPR variant shows promise",
          "authors": ["Smith J.", "Lee K."],
          "doi": "10.1101/2026.01.15.xxxxx",
          "source": "biorxiv",
          "published": "2026-01-15",
          "abstract_summary": "..."
        }
      ],
      "emerging_since": "2026-01-20"
    }
  ],
  "summary": {
    "total_papers_analyzed": 1247,
    "new_topics_detected": 8,
    "high_priority_alerts": 2
  }
}
```

### Markdown Output

```markdown
# Emerging Topics Report - 2026-02-06

## 🔥 High Priority Topics

### 1. Gene Editing Therapy (Score: 0.89)
- **Keywords**: CRISPR, base editing, prime editing
- **Growth Rate**: Rapid (+145% vs last week)
- **Preprints**: 34 papers
- **Cross-platform mentions**: 127

#### Key Papers
1. "New CRISPR variant shows promise" - Smith J. et al.
   - DOI: 10.1101/2026.01.15.xxxxx
   - Source: bioRxiv
```

## Configuration File

Create `config.yaml` for persistent settings:

```yaml
sources:
  biorxiv:
    enabled: true
    rss_url: "https://www.biorxiv.org/rss/recent.rss"
    api_endpoint: "https://api.biorxiv.org/details/"
  medrxiv:
    enabled: true
    rss_url: "https://www.medrxiv.org/rss/recent.rss"
    api_endpoint: "https://api.medrxiv.org/details/"

trending:
  min_papers_threshold: 5
  velocity_window_days: 3
  novelty_weight: 0.4
  momentum_weight: 0.6

keywords:
  auto_detect: true
  custom_trackers:
    - "artificial intelligence"
    - "machine learning"
    - "single cell"
    - "spatial transcriptomics"

output:
  default_format: markdown
  save_history: true
  history_path: "./data/history.json"

notifications:
  enabled: false
  high_score_threshold: 0.8
```

## Trending Score Algorithm

The trending score (0-1) is calculated using:

```
Score = (Novelty × 0.4) + (Momentum × 0.4) + (CrossRef × 0.2)

Where:
- Novelty: Inverse frequency of topic in historical data
- Momentum: Rate of increase in mentions over velocity window
- CrossRef: Mentions across multiple platforms
```

## API Endpoints

### bioRxiv API
- Base: `https://api.biorxiv.org/`
- Details: `/details/[server]/[DOI]/[format]`
- Publication: `/pub/[DOI]/[format]`

### medRxiv API
- Same structure as bioRxiv

## Data Storage

Historical data is stored in `data/history.json` for:
- Trend comparison
- Velocity calculation
- Duplicate detection

## Examples

### Example 1: Quick Daily Scan

```bash
python scripts/main.py --days 1 --output markdown
```

### Example 2: Weekly Deep Analysis

```bash
python scripts/main.py \
  --days 7 \
  --min-score 0.7 \
  --max-topics 50 \
  --output json \
  > weekly_report.json
```

### Example 3: Track Specific Research Area

```bash
python scripts/main.py \
  --keywords "Alzheimer,neurodegeneration,amyloid" \
  --days 30 \
  --min-score 0.5
```

## Troubleshooting

### Rate Limiting
If you encounter rate limits, increase the `--delay` parameter (default: 1s between requests).

### Missing Papers
Ensure RSS feeds are accessible. Some institutional firewalls may block preprint servers.

### Low Trending Scores
For niche topics, lower `--min-score` threshold or increase `--days` for more data.

## References

See `references/README.md` for:
- API documentation links
- Research papers on trend detection
- Related tools and resources

## License

MIT License - Part of OpenClaw Skills Collection

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture
## Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support
