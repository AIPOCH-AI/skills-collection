---
name: citation-chasing-mapping
description: Trace citation networks to discover related research, identify foundational papers, and map field evolution. Analyzes citation relationships to find ancestors (cited works) and descendants (citing works) for comprehensive literature discovery.
allowed-tools: [Read, Write, Bash, Edit, WebFetch]
license: MIT
metadata:
  skill-author: AIPOCH
---

# Citation Chasing & Mapping

Explore and map citation networks to discover related research, identify foundational papers, and trace the evolution of scientific fields. Supports both backward citation chasing (finding cited works/ancestors) and forward citation chasing (finding citing works/descendants) for comprehensive literature reviews.

**Note:** This tool exports citation network data in JSON format for use with external visualization tools (e.g., Cytoscape, Gephi). It does not generate visualizations directly.

**Key Capabilities:**
- **Bidirectional Citation Tracing**: Find both papers cited by a work and papers that cite it
- **Multi-Hop Network Analysis**: Explore citation networks up to 3 degrees of separation
- **Foundational Paper Identification**: Discover highly-cited works that shaped the field
- **Field Evolution Mapping**: Track how research topics developed over time

---

## When to Use

**✅ Use this skill when:**
- Conducting **comprehensive literature reviews** and need to ensure completeness
- Starting research in a **new field** and need to identify key papers
- Writing a **review article** and need to map the development of a topic
- Identifying **foundational works** that everyone in the field should know
- Finding **recent developments** that cite a seminal paper
- Tracing the **evolution of an idea** from its origin to present day
- Discovering **related research** that might not appear in keyword searches
- Preparing **grant proposals** and need to establish the intellectual foundation

**❌ Do NOT use when:**
- Looking for **full-text papers** → Use `literature-full-text-fetcher` or `pubmed-central-downloader`
- Needing **bibliographic management** → Use Zotero, Mendeley, or EndNote
- Performing **systematic reviews** with strict inclusion criteria → Use Covidence or similar tools
- Requiring **citation counts and metrics** only → Use Google Scholar, Web of Science
- Analyzing **co-authorship networks** → Use specialized social network tools
- Doing **topic modeling or text mining** → Use NLP tools like LDA or BERT
- Needing **real-time citation alerts** → Use journal alert services or RSS feeds

**Related Skills:**
- **上游 (Upstream)**: `literature-full-text-fetcher`, `abstract-summarizer`
- **下游 (Downstream)**: `journal-club-presenter`, `cross-disciplinary-bridge-finder`

---

## Integration with Other Skills

**Upstream Skills:**
- `literature-full-text-fetcher`: Retrieve full text of papers identified through citation chasing
- `abstract-summarizer`: Summarize papers found in citation network
- `conference-abstract-adaptor`: Find related conference presentations

**Downstream Skills:**
- `journal-club-presenter`: Create presentations about key papers identified
- `cross-disciplinary-bridge-finder`: Find connections to other fields
- `grant-proposal-assistant`: Use identified papers for background sections

**Complete Workflow:**
```
Seed Paper → citation-chasing-mapping → literature-full-text-fetcher → abstract-summarizer → Comprehensive Review
```

---

## Core Capabilities

### 1. Backward Citation Chasing (Ancestors)

Find papers cited by a target paper to trace intellectual foundations and prior work.

```python
from scripts.main import CitationNetwork

# Initialize network
network = CitationNetwork()

# Add papers with their citations
network.add_paper(
    "CRISPR_2012",
    "A Programmable Dual-RNA-Guided DNA Endonuclease", 
    2012,
    citations=["ZFN_1996", "TALEN_2011", "tracrRNA_2008", "Cas9_2005"]
)

network.add_paper(
    "ZFN_1996",
    "Zinc Finger Nucleases",
    1996,
    citations=["zinc_finger_1985"]
)

# Find papers cited by CRISPR 2012 (depth 1)
seed_paper = "CRISPR_2012"
depth = 1

if seed_paper in network.papers:
    direct_citations = network.papers[seed_paper]["citations"]
    print(f"Papers cited by '{network.papers[seed_paper]['title']}' (depth 1):")
    for cited_id in direct_citations:
        if cited_id in network.papers:
            cited = network.papers[cited_id]
            print(f"  [{cited_id}] {cited['title']} ({cited['year']})")
```

**Backward Chasing Strategy:**

| Depth | What You Find | Use Case |
|-------|--------------|----------|
| **1 hop** | Direct citations | Immediate intellectual foundation |
| **2 hops** | Citations of citations | Broader field context |
| **3 hops** | Extended network | Historical development |

**Best Practices:**
- ✅ **Start with recent review papers** - they cite comprehensively
- ✅ **Note citation patterns** - papers cited multiple times are foundational
- ✅ **Check publication years** - ensure chronological logic
- ✅ **Look for review papers** in the citation list for broader context

**Common Issues and Solutions:**

**Issue: Too many citations to review**
- Symptom: High-impact papers have hundreds of citations
- Solution: Focus on papers cited multiple times; prioritize reviews

**Issue: Circular references**
- Symptom: Papers cite each other (A cites B, B cites A)
- Solution: Check publication dates to establish true lineage

### 2. Forward Citation Chasing (Descendants)

Find papers that cite a target paper to discover recent developments and applications.

```python
from scripts.main import CitationNetwork

network = CitationNetwork()

# Add papers
network.add_paper("CRISPR_2012", "CRISPR-Cas9 Original", 2012, [])
network.add_paper("CRISPR_App_2013", "CRISPR Applications", 2013, ["CRISPR_2012"])
network.add_paper("CRISPR_Therapy_2015", "Therapeutic CRISPR", 2015, ["CRISPR_2012", "CRISPR_App_2013"])
network.add_paper("CRISPR_BaseEdit_2016", "Base Editing", 2016, ["CRISPR_2012"])
network.add_paper("CRISPR_Clinical_2018", "Clinical Trials", 2018, ["CRISPR_Therapy_2015"])

# Find papers that cite CRISPR_2012 (forward chasing)
seed_paper = "CRISPR_2012"
citing_papers = network.find_citing_papers(seed_paper)

print(f"Papers citing '{network.papers[seed_paper]['title']}':")
for citing_id in citing_papers:
    citing = network.papers[citing_id]
    print(f"  [{citing_id}] {citing['title']} ({citing['year']})")

# Multi-hop forward search
related = network.find_related_papers(seed_paper, depth=2)
print(f"\nExtended network (2 hops): {len(related)} papers")
```

**Forward Chasing Strategy:**

| Approach | Best For | Expected Results |
|----------|----------|-----------------|
| **Direct citations** | Immediate follow-up work | 50-500 papers |
| **2-hop network** | Field development | 500-2000 papers |
| **Filtered by year** | Recent advances | Most recent subset |
| **Filtered by topic** | Specific applications | Focused subset |

**Best Practices:**
- ✅ **Check citation context** - not all citations are substantive
- ✅ **Sort by year** - identify recent developments
- ✅ **Look for application papers** - show practical impact
- ✅ **Track methodological improvements** - technical advances

**Common Issues and Solutions:**

**Issue: Too many citing papers**
- Symptom: Seminal papers have thousands of citations
- Solution: Filter by year, journal impact, or citation context

**Issue: Citation without relevance**
- Symptom: Paper cited only in introduction/background
- Solution: Read abstracts to assess substantive engagement

### 3. Foundational Paper Identification

Identify highly-cited papers that represent turning points or foundational work in a field.

```python
from scripts.main import CitationNetwork

# Build network from file or demo
network = CitationNetwork()

# Add sample papers
papers_data = [
    ("Genomics_2001", "Human Genome Paper", 2001, []),
    ("NGS_2005", "Next-Gen Sequencing", 2005, ["Genomics_2001"]),
    ("RNA_Seq_2008", "RNA-Seq Methods", 2008, ["NGS_2005"]),
    ("scRNA_2015", "Single-Cell RNA-Seq", 2015, ["RNA_Seq_2008", "NGS_2005"]),
    ("ATAC_2013", "ATAC-Seq", 2013, ["NGS_2005"]),
]

for pid, title, year, citations in papers_data:
    network.add_paper(pid, title, year, citations)

# Identify most cited papers
key_papers = network.identify_key_papers()

print("\n🏆 Foundational Papers (Most Cited):")
print("-" * 60)
for rank, (pid, count) in enumerate(key_papers[:5], 1):
    paper = network.papers.get(pid, {})
    title = paper.get('title', 'Unknown')
    year = paper.get('year', '?')
    print(f"{rank}. [{pid}] ({year})")
    print(f"   Citations: {count}")
    print(f"   Title: {title}")
    print()
```

**Foundational Paper Indicators:**

| Indicator | Significance | Example |
|-----------|--------------|---------|
| **High citation count** | Broad impact | >1000 citations |
| **Cited by diverse fields** | Cross-disciplinary | Multiple domain papers |
| **Early publication** | Foundational | Early in field timeline |
| **Methodology paper** | Enables research | New technique/protocol |
| **Review in top journal** | Synthesis | Nature/Science/Cell reviews |

**Best Practices:**
- ✅ **Consider citation velocity** - recent papers with rapid uptake
- ✅ **Check citation context** - meaningful vs. perfunctory citations
- ✅ **Look for methodological papers** - often highly cited
- ✅ **Identify review papers** - comprehensive field overviews

**Common Issues and Solutions:**

**Issue: Methodology vs. Discovery papers**
- Symptom: Methods papers often have more citations than discovery papers
- Solution: Separate analysis by paper type; both are valuable

**Issue: Self-citations inflate counts**
- Symptom: Authors cite their own work extensively
- Solution: Check for self-citation patterns; focus on external citations

### 4. Multi-Hop Network Analysis

Explore citation networks up to 3 degrees of separation for comprehensive field mapping.

```python
from scripts.main import CitationNetwork

network = CitationNetwork()

# Build a more complex network
papers = {
    "A_2000": {"title": "Original Discovery", "year": 2000, "citations": []},
    "B_2002": {"title": "First Application", "year": 2002, "citations": ["A_2000"]},
    "C_2003": {"title": "Method Improvement", "year": 2003, "citations": ["A_2000"]},
    "D_2005": {"title": "Clinical Study", "year": 2005, "citations": ["B_2002"]},
    "E_2006": {"title": "Large Scale Study", "year": 2006, "citations": ["C_2003"]},
    "F_2008": {"title": "Meta-Analysis", "year": 2008, "citations": ["D_2005", "E_2006"]},
}

for pid, data in papers.items():
    network.add_paper(pid, data["title"], data["year"], data["citations"])

# Analyze network from seed paper
seed = "A_2000"

for depth in [1, 2, 3]:
    related = network.find_related_papers(seed, depth=depth)
    print(f"\nDepth {depth}: {len(related)} related papers")
    
    # Group by generation
    if depth == 1:
        print("  Generation 1 (direct citations):")
    elif depth == 2:
        print("  Generation 2 (citations of citations):")
    else:
        print("  Generation 3 (extended network):")
    
    for pid in sorted(related)[:5]:  # Show first 5
        if pid in network.papers:
            paper = network.papers[pid]
            print(f"    [{pid}] {paper['title']} ({paper['year']})")
    
    if len(related) > 5:
        print(f"    ... and {len(related) - 5} more")
```

**Network Depth Analysis:**

| Depth | Coverage | Use Case | Risk |
|-------|----------|----------|------|
| **1 hop** | Direct neighbors | Focused review | May miss context |
| **2 hops** | Extended network | Comprehensive | Manageable size |
| **3 hops** | Broad field | Historical mapping | Too large/diluted |

**Best Practices:**
- ✅ **Start with depth=2** for most reviews
- ✅ **Check diminishing returns** - additional hops add noise
- ✅ **Prune by relevance** - remove off-topic papers
- ✅ **Map chronologically** - understand temporal development

**Common Issues and Solutions:**

**Issue: Network explosion**
- Symptom: 3 hops generates thousands of papers
- Solution: Use depth=2 with filtering; or sample from 3-hop results

**Issue: Off-topic drift**
- Symptom: Distant papers lose connection to original topic
- Solution: Apply topic filters; manually curate distant papers

### 5. Network Data Export

Export citation network data for external analysis and visualization tools.

```python
from scripts.main import CitationNetwork
import json

network = CitationNetwork()

# Add sample network
network.add_paper("Paper_A", "Original Work", 2010, ["Paper_B", "Paper_C"])
network.add_paper("Paper_B", "Prior Method", 2008, ["Paper_D"])
network.add_paper("Paper_C", "Related Theory", 2009, ["Paper_D"])
network.add_paper("Paper_D", "Foundational Work", 2005, [])
network.add_paper("Paper_E", "Follow-up Study", 2012, ["Paper_A"])

output_file = "citation_network.json"
network.export_network(output_file)

# Preview structure
with open(output_file, 'r') as f:
    data = json.load(f)

print("Network Structure:")
print(f"  Nodes (papers): {len(data['nodes'])}")
print(f"  Edges (citations): {len(data['edges'])}")

print("\nNode example:")
print(json.dumps(data['nodes'][0], indent=2))

print("\nEdge example:")
print(json.dumps(data['edges'][0], indent=2))

# External visualization tools
print("\n" + "="*60)
print("RECOMMENDED EXTERNAL TOOLS FOR VISUALIZATION:")
print("="*60)
print("1. Cytoscape: Import JSON, use 'yFiles Circular Layout'")
print("2. Gephi: Import JSON, use 'Force Atlas 2' layout")
print("3. D3.js: Use force-directed graph example")
print("4. Python: networkx + matplotlib (separate installation required)")
```

**Network Format Specification:**

```json
{
  "nodes": [
    {
      "id": "paper_id",
      "title": "Paper Title",
      "year": 2020,
      "citation_count": 45
    }
  ],
  "edges": [
    {
      "source": "citing_paper",
      "target": "cited_paper"
    }
  ]
}
```

**Note:** This tool exports network data in standard JSON format for use with external visualization tools. It does not generate visualizations directly.

### 6. Field Evolution Mapping

Trace how a research field developed over time by analyzing citation patterns chronologically.

```python
from scripts.main import CitationNetwork
from collections import defaultdict

network = CitationNetwork()

# Add papers across multiple years
field_papers = [
    ("Genomics_2001", "Human Genome", 2001, []),
    ("Microarray_2002", "Expression Arrays", 2002, ["Genomics_2001"]),
    ("RNAi_2003", "RNA Interference", 2003, []),
    ("NGS_2005", "Next-Gen Seq", 2005, ["Genomics_2001"]),
    ("RNA_Seq_2008", "RNA-Seq", 2008, ["NGS_2005", "Microarray_2002"]),
    ("GWAS_2009", "GWAS Methods", 2009, ["Genomics_2001"]),
    ("scRNA_2015", "Single-Cell", 2015, ["RNA_Seq_2008", "NGS_2005"]),
    ("CRISPR_2012", "CRISPR", 2012, ["RNAi_2003"]),
    ("Spatial_2020", "Spatial Omics", 2020, ["scRNA_2015", "RNA_Seq_2008"]),
]

for pid, title, year, citations in field_papers:
    network.add_paper(pid, title, year, citations)

# Analyze evolution by year
papers_by_year = defaultdict(list)
for pid, data in network.papers.items():
    papers_by_year[data['year']].append(pid)

print("\n📊 Field Evolution Timeline:")
print("="*60)

for year in sorted(papers_by_year.keys()):
    papers = papers_by_year[year]
    print(f"\n{year}:")
    for pid in papers:
        paper = network.papers[pid]
        citations = paper['citations']
        if citations:
            cited_titles = [network.papers.get(c, {}).get('title', '?')[:20] for c in citations]
            citation_str = f" ← {', '.join(cited_titles)}"
        else:
            citation_str = " (foundational)"
        print(f"  • {paper['title'][:40]}{citation_str}")

# Identify field shifts
print("\n" + "="*60)
print("🔍 Field Development Insights:")
print("="*60)

# Find periods of high activity
for year in sorted(papers_by_year.keys()):
    count = len(papers_by_year[year])
    if count >= 2:
        print(f"{year}: Active year with {count} major papers")
```

**Evolution Analysis Metrics:**

| Metric | What It Shows | Interpretation |
|--------|---------------|----------------|
| **Publication rate** | Field activity | Growth or maturity |
| **Citation patterns** | Knowledge flow | Influential works |
| **Method transitions** | Technique changes | Technical progress |
| **Cross-citation** | Subfield integration | Field convergence |

**Best Practices:**
- ✅ **Track methodological papers** - often mark transitions
- ✅ **Identify review paper timing** - indicates field maturity
- ✅ **Note citation half-life** - rate of knowledge turnover
- ✅ **Map paradigm shifts** - major changes in approach

**Common Issues and Solutions:**

**Issue: Confounding by publication delays**
- Symptom: Recent papers appear less influential
- Solution: Normalize by years since publication; use citation velocity

---

## Complete Workflow Example

**From seed paper to comprehensive literature map:**

```bash
# Step 1: Create sample citation network
python scripts/main.py --paper-id "CRISPR_2012" --depth 2 --output network.json

# Step 2: View key foundational papers
python scripts/main.py --network-file network.json
```

**Python API Usage:**

```python
from scripts.main import CitationNetwork
import json

def conduct_comprehensive_review(
    seed_papers: list,
    max_depth: int = 2,
    output_dir: str = "./literature_review"
) -> dict:
    """
    Comprehensive citation-based literature review.
    
    Args:
        seed_papers: List of seed paper IDs to start from
        max_depth: Maximum citation hops
        output_dir: Directory for output files
        
    Returns:
        Dictionary with review statistics and findings
    """
    from pathlib import Path
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    network = CitationNetwork()
    
    # Build network (in real use, load from database)
    # This example uses demo data
    demo_papers = {
        "Seed_2020": {"title": "Recent Discovery", "year": 2020, "citations": ["Foundational_2015", "Method_2018"]},
        "Foundational_2015": {"title": "Original Theory", "year": 2015, "citations": ["Classical_2010"]},
        "Method_2018": {"title": "Key Method", "year": 2018, "citations": ["Foundational_2015"]},
        "Classical_2010": {"title": "Seminal Work", "year": 2010, "citations": []},
        "FollowUp_2021": {"title": "Application Study", "year": 2021, "citations": ["Seed_2020"]},
        "Review_2022": {"title": "Recent Review", "year": 2022, "citations": ["Seed_2020", "Method_2018"]},
    }
    
    for pid, data in demo_papers.items():
        network.add_paper(pid, data["title"], data["year"], data.get("citations", []))
    
    # Analyze each seed paper
    all_related = set()
    findings = {
        "seed_papers": [],
        "foundational_papers": [],
        "recent_developments": [],
        "network_stats": {}
    }
    
    print("\n" + "="*70)
    print("COMPREHENSIVE LITERATURE REVIEW")
    print("="*70)
    
    for seed in seed_papers:
        if seed not in network.papers:
            print(f"⚠️  Seed paper '{seed}' not found in database")
            continue
            
        print(f"\n🎯 Analyzing: {seed}")
        print(f"   Title: {network.papers[seed]['title']}")
        
        # Find related papers
        related = network.find_related_papers(seed, max_depth)
        all_related.update(related)
        
        # Categorize findings
        for pid in related:
            if pid not in network.papers:
                continue
            paper = network.papers[pid]
            
            if paper['year'] <= 2015:
                findings["foundational_papers"].append(pid)
            elif paper['year'] >= 2020:
                findings["recent_developments"].append(pid)
        
        print(f"   Found {len(related)} related papers")
    
    # Identify key papers across entire network
    key_papers = network.identify_key_papers()
    
    # Export network
    network_file = f"{output_dir}/citation_network.json"
    network.export_network(network_file)
    
    # Compile summary
    summary = {
        "total_papers_analyzed": len(network.papers),
        "seed_papers": len(seed_papers),
        "related_papers_found": len(all_related),
        "foundational_papers": len(findings["foundational_papers"]),
        "recent_papers": len(findings["recent_developments"]),
        "top_cited_papers": [(pid, count) for pid, count in key_papers[:5]],
        "output_files": {
            "network_json": network_file
        }
    }
    
    # Print summary
    print("\n" + "="*70)
    print("REVIEW SUMMARY")
    print("="*70)
    print(f"Total papers in database: {summary['total_papers_analyzed']}")
    print(f"Related papers identified: {summary['related_papers_found']}")
    print(f"Foundational papers (≤2015): {summary['foundational_papers']}")
    print(f"Recent developments (≥2020): {summary['recent_papers']}")
    
    print("\n🏆 Most Cited Papers:")
    for i, (pid, count) in enumerate(summary['top_cited_papers'], 1):
        title = network.papers.get(pid, {}).get('title', 'Unknown')
        print(f"  {i}. [{pid}] {title[:50]}... ({count} citations)")
    
    print(f"\n📁 Network exported to: {network_file}")
    print("="*70)
    
    return summary

# Execute review
results = conduct_comprehensive_review(
    seed_papers=["Seed_2020"],
    max_depth=2,
    output_dir="./my_review"
)
```

**Expected Output Files:**

```
literature_review/
├── foundational_papers.txt    # List of key historical papers
├── recent_papers.txt          # List of recent developments
└── review_summary.json        # Analysis statistics
```

---

## Common Patterns

### Pattern 1: Comprehensive Literature Review

**Scenario**: Starting a new research project and need complete background.

```json
{
  "review_type": "comprehensive",
  "seed_papers": [
    "Most recent high-impact paper",
    "Recent comprehensive review"
  ],
  "depth": 2,
  "filtering": {
    "date_range": "2015-2025",
    "min_citations": 10,
    "journals": ["Nature", "Science", "Cell", "specialty journals"]
  }
}
```

**Workflow:**
1. Identify 2-3 recent high-quality seed papers
2. Run backward citation chasing (depth=2)
3. Run forward citation chasing (depth=2)
4. Identify top 20 most-cited papers
5. Filter by relevance and quality
6. Organize by themes/subtopics
7. Create reading schedule

**Output Example:**
```
Comprehensive Literature Review:
  Seed papers: 3
  Papers identified: 247
  After filtering: 85
  
Breakdown:
  - Foundational (pre-2015): 12 papers
  - Core developments (2015-2020): 38 papers
  - Recent advances (2020+): 35 papers
  
Themes identified:
  1. Methodological advances (23 papers)
  2. Clinical applications (31 papers)
  3. Basic mechanisms (31 papers)
```

### Pattern 2: Foundational Paper Discovery

**Scenario**: New to a field and need to identify must-read classics.

```json
{
  "task": "foundational_discovery",
  "approach": "citation_analysis",
  "seed": "Recent review paper",
  "metrics": [
    "citation_count",
    "citation_velocity",
    "author_h_index"
  ]
}
```

**Workflow:**
1. Start with recent comprehensive review
2. Extract all citations (backward chasing)
3. Rank by citation count
4. Check which papers are cited by multiple reviews
5. Read abstracts of top 20
6. Select 10-15 most relevant
7. Read in chronological order

**Output Example:**
```
Foundational Papers Identified:
  
Tier 1 (Essential - cited by everyone):
  1. Original discovery paper (2005) - 2,847 citations
  2. Methodology breakthrough (2008) - 1,923 citations
  3. First clinical application (2010) - 1,456 citations
  
Tier 2 (Important - cited by most):
  4-10. Major advances (2012-2018) - 500-1000 citations
  
Reading order: Chronological (2005 → 2018)
```

### Pattern 3: Recent Development Tracking

**Scenario**: Staying current with latest advances in your field.

```json
{
  "tracking_type": "recent_developments",
  "seed_papers": [
    "Seminal papers from 5 years ago"
  ],
  "direction": "forward",
  "depth": 1,
  "filter": {
    "year": "2023-2025",
    "alert_frequency": "monthly"
  }
}
```

**Workflow:**
1. Identify 5-10 key papers from ~5 years ago
2. Run forward citation chasing (depth=1)
3. Filter to last 2 years only
4. Sort by journal impact
5. Read titles and abstracts
6. Flag highly relevant papers
7. Set up alerts for key authors

**Output Example:**
```
Recent Developments (2023-2025):
  Papers citing key works: 127
  After year filter: 34
  
High-priority papers:
  - 3 papers in Nature/Science/Cell
  - 8 papers in top specialty journals
  - 12 methodological advances
  - 11 clinical studies
  
Key trends:
  - AI/ML integration increasing
  - Single-cell methods dominating
  - Clinical translation accelerating
```

### Pattern 4: Interdisciplinary Bridge Finding

**Scenario**: Finding connections between your field and adjacent disciplines.

```json
{
  "task": "interdisciplinary_mapping",
  "primary_field": "Your expertise",
  "target_fields": ["Field A", "Field B"],
  "method": "citation_bridge_analysis",
  "depth": 2
}
```

**Workflow:**
1. Identify top papers in your field
2. Run 2-hop citation network
3. Identify papers from other fields in network
4. Check cross-field citations
5. Map knowledge transfer pathways
6. Identify potential collaborators
7. Discover methodological opportunities

**Output Example:**
```
Interdisciplinary Connections Found:
  
Field A connections:
  - 12 papers cite your field's methods
  - 3 methodological papers highly relevant
  - Potential collaboration: Dr. X (3 shared citations)
  
Field B connections:
  - 8 papers apply your findings
  - 1 highly-cited review bridges fields
  - Conference overlap: ASM 2024
  
Bridge papers (cited by both fields):
  1. Methodology paper (2019) - 234 citations
  2. Application review (2021) - 156 citations
```

---

## Quality Checklist

**Pre-Analysis:**
- [ ] **CRITICAL**: Verify seed papers are high quality and relevant
- [ ] Confirm seed paper IDs are correct (DOI, PubMed ID)
- [ ] Check publication date of seed papers (recent vs. classic)
- [ ] Verify access to citation database or API
- [ ] Define scope clearly (topic boundaries)
- [ ] Set citation depth appropriate for goals
- [ ] Identify any papers to exclude (retractions, etc.)

**During Analysis:**
- [ ] Track both directions (ancestors and descendants)
- [ ] **CRITICAL**: Deduplicate papers found through multiple paths
- [ ] Note citation context (meaningful vs. perfunctory)
- [ ] Check for self-citation patterns
- [ ] Verify chronological consistency
- [ ] Flag review papers for special attention
- [ ] Identify methodological papers separately

**Post-Analysis:**
- [ ] **CRITICAL**: Filter results by relevance to topic
- [ ] Rank papers by importance (citations, journal, recency)
- [ ] Check for gaps (missing important papers)
- [ ] Verify no key papers overlooked
- [ ] Organize by themes or chronological development
- [ ] Create prioritized reading list

**Validation:**
- [ ] **CRITICAL**: Cross-check with domain expert or existing reviews
- [ ] Verify foundational papers match field consensus
- [ ] Check recent papers are actually novel
- [ ] Ensure no important subtopics missed
- [ ] Validate citation counts against Google Scholar/Web of Science
- [ ] Review for potential bias (author, institution, country)
- [ ] Document methodology for reproducibility

---

## Common Pitfalls

**Search Strategy Issues:**
- ❌ **Single seed paper** → Limited coverage of field
  - ✅ Use multiple diverse seed papers
  
- ❌ **Only forward OR backward** → Miss half the story
  - ✅ Always search both directions
  
- ❌ **Too shallow (depth=1)** → Miss important connections
  - ✅ Use depth=2 for comprehensive reviews
  
- ❌ **Too deep (depth=3+)** → Diluted, off-topic results
  - ✅ Depth=3 only for historical analyses

**Data Quality Issues:**
- ❌ **Ignoring citation context** → Include irrelevant papers
  - ✅ Read abstracts to assess relevance
  
- ❌ **Counting all citations equally** → Self-citations inflate counts
  - ✅ Check for and exclude self-citations
  
- ❌ **Not filtering by date** → Outdated information
  - ✅ Apply appropriate date filters
  
- ❌ **Missing recent preprints** → Not yet cited
  - ✅ Supplement with bioRxiv/medRxiv searches

**Interpretation Issues:**
- ❌ **Assuming more citations = better** → Method papers over-cited
  - ✅ Consider paper type and citation context
  
- ❌ **Ignoring negative citations** → Cited for being wrong
  - ✅ Check citation sentiment when possible
  
- ❌ **Confirmation bias** → Only finding supporting papers
  - ✅ Actively seek contradictory evidence
  
- ❌ **Neglecting recent papers** → Low citation count
  - ✅ Use citation velocity, not just total count

---

## Troubleshooting

**Problem: No papers found**
- Symptoms: Empty results or "paper not found"
- Causes:
  - Incorrect paper ID format
  - Paper not in database
  - API connection issues
- Solutions:
  - Verify paper ID (DOI, PMID)
  - Try alternative identifiers
  - Check database coverage dates
  - Use multiple search strategies

**Problem: Too many papers to review**
- Symptoms: Thousands of papers identified
- Causes:
  - High-impact seed paper
  - Broad field definition
  - Too many seed papers
- Solutions:
  - Filter by date (last 5 years)
  - Filter by citation count threshold
  - Limit to specific journals
  - Use depth=1 instead of 2

**Problem: Off-topic papers included**
- Symptoms: Papers not relevant to your topic
- Causes:
  - Perfunctory citations
  - Broad interdisciplinary citations
  - Methodology papers cited everywhere
- Solutions:
  - Filter by keywords in titles
  - Check citation context
  - Remove papers with <N citations from seed
  - Manual curation of results

**Problem: Missing obvious papers**
- Symptoms: Important papers not in results
- Causes:
  - Wrong seed papers
  - Incomplete database
  - Recent papers not yet cited
- Solutions:
  - Add more diverse seed papers
  - Supplement with keyword searches
  - Check recent preprint servers
  - Consult with domain experts

**Problem: Circular citations**
- Symptoms: Papers citing each other (A→B→C→A)
- Causes:
  - Concurrent publication
  - Cross-citation in reviews
  - Methods validation
- Solutions:
  - Check publication dates
  - Consider direction of influence
  - Note concurrent development
  - Manually resolve ordering

**Problem: Self-citations dominate**
- Symptoms: Author's own papers most cited
- Causes:
  - Prolific author as seed
  - Author reviews own work
  - Series of related papers
- Solutions:
  - Exclude self-citations from counts
  - Focus on external citations
  - Flag self-citation patterns
  - Consider author diversity

---

## References

Available in `references/` directory:

- (No reference files currently available for this skill)

**External Resources:**
- Web of Science: https://www.webofscience.com
- Google Scholar: https://scholar.google.com
- Scopus: https://www.scopus.com
- PubMed: https://pubmed.ncbi.nlm.nih.gov
- Semantic Scholar: https://www.semanticscholar.org
- Citation Chasing Guide: https://guides.lib.uw.edu/research/citationchasing

---

## Scripts

Located in `scripts/` directory:

- `main.py` - Citation network analysis and mapping engine

--
**Node Attributes:**
- **Size**: Proportional to citation count
- **Color**: Publication year (blue=old, red=recent)
- **Label**: Paper ID or shortened title

**Edge Attributes:**
- **Direction**: From citing to cited paper
- **Thickness**: Can represent citation strength
- **Color**: Can indicate citation type

**Recommended Tools:**
- **Cytoscape**: Large networks, advanced analysis
- **Gephi**: Visual exploration, force layouts
- **VOSviewer**: Bibliometric maps, clustering

---

**Last Updated**: 2026-02-09  
**Skill ID**: 187  
**Version**: 2.0 (K-Dense Standard)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--doi` | str | Required | Paper DOI to query |
| `--title` | str | Required | Paper title to search |
| `--pmid` | str | Required | PubMed ID to query |
| `--network-file` | str | Required |  |
| `--demo` | str | Required | Run demo with example data |
| `--depth` | int | 2 |  |
| `--max-per-level` | int | 20 |  |
| `--delay` | float | 0.5 |  |
| `--output` | str | "citation_network.json" |  |
| `--format` | str | "json" |  |
