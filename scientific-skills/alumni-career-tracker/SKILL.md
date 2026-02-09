---
name: alumni-career-tracker
description: Analyze laboratory alumni career trajectories and outcomes to provide data-driven 
  career guidance for current students and postdocs. Tracks industry vs academia distribution, 
  identifies career pathways, and generates personalized recommendations based on degree level 
  and research interests.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Alumni Career Tracker

## Overview

Career analytics tool that tracks and analyzes the professional destinations of laboratory alumni, providing evidence-based guidance for trainees navigating career transitions.

**Key Capabilities:**
- **Career Outcome Tracking**: Monitor alumni destinations across sectors
- **Trajectory Analysis**: Map career progression patterns over time
- **Skills Gap Identification**: Compare training vs. job requirements
- **Salary Benchmarking**: Track compensation trends by degree and sector
- **Network Mapping**: Visualize alumni connections and pathways
- **Personalized Guidance**: Generate tailored career recommendations

## When to Use

**✅ Use this skill when:**
- Mentoring new students on career options and trajectories
- Training grant applications requiring career outcome data (e.g., NIH T32, F32)
- Lab website showcasing successful alumni for recruitment
- Departmental reviews demonstrating training effectiveness
- Individual career counseling sessions with trainees
- Identifying industry partners and collaboration opportunities
- Benchmarking your lab's career outcomes against peers

**❌ Do NOT use when:**
- Job placement services (out of scope) → Use career center resources
- Salary negotiation for current positions → Use `salary-negotiation-prep`
- Resume or CV writing → Use `medical-cv-resume-builder`
- Interview preparation → Use `interview-mock-partner`
- Real-time job searching → Use LinkedIn or job boards

**Integration:**
- **Upstream**: `mentorship-meeting-agenda` (career discussion prep), `linkedin-optimizer` (profile data)
- **Downstream**: `cover-letter-drafter` (application materials), `networking-email-drafter` (alumni outreach)

## Core Capabilities

### 1. Alumni Database Management

Collect and organize career outcome data:

```python
from scripts.tracker import AlumniTracker

tracker = AlumniTracker()

# Add single alumni record
alumni = {
    "name": "Dr. Sarah Chen",
    "graduation_year": 2023,
    "degree": "PhD",
    "current_status": "industry",
    "organization": "Genentech",
    "position": "Senior Scientist",
    "location": "San Francisco, CA",
    "field": "Immuno-oncology",
    "salary_range": "$140k-$160k",
    "linkedin": "linkedin.com/in/sarahchen"
}

tracker.add_alumni(alumni)

# Batch import from CSV
tracker.import_csv("alumni_2020_2024.csv")
```

**Data Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Full name |
| graduation_year | Yes | Year completed degree |
| degree | Yes | PhD/Master/Bachelor/Postdoc |
| current_status | Yes | industry/academia/startup/gov/other |
| organization | Yes | Company/University/Institution |
| position | Yes | Job title or rank |
| location | No | City/Country |
| field | No | Research/industry area |
| salary_range | No | Optional compensation |
| linkedin | No | Profile for tracking updates |

### 2. Career Outcome Analysis

Generate comprehensive statistics and visualizations:

```python
# Analyze by degree level
analysis = tracker.analyze(
    degree_filter=["PhD", "Master"],
    year_range=(2020, 2024),
    metrics=["sector_distribution", "geographic_spread", "salary_trends"]
)

# Generate report
report = analysis.generate_report(format="pdf")
report.save("lab_career_outcomes_2024.pdf")
```

**Analysis Dimensions:**
- **Sector Distribution**: Industry vs. Academia vs. Government vs. Other
- **By Degree Level**: PhD, Master, Bachelor outcomes
- **Geographic Trends**: Regional employment patterns
- **Temporal Trends**: Year-over-year changes
- **Salary Benchmarks**: By degree, sector, and years post-graduation
- **Top Employers**: Most common companies and institutions

### 3. Career Pathway Mapping

Visualize common career trajectories:

```python
# Map career pathways
pathways = tracker.map_pathways(
    start_degree="PhD",
    target_years=[0, 2, 5, 10],
    min_samples=5
)

# Visualize as Sankey diagram
pathways.visualize(output="career_flows.html")
```

**Visualization Types:**
- **Sankey Diagrams**: Flow from degree → first job → current position
- **Timeline Views**: Individual career progression over time
- **Network Graphs**: Alumni connections and referrals
- **Heatmaps**: Skills vs. job requirements

### 4. Personalized Career Recommendations

Generate tailored advice for current trainees:

```python
# Get recommendations for a student
recommendations = tracker.get_recommendations(
    current_degree="PhD",
    research_area="Cancer Biology",
    interests=["industry", "translational research"],
    years_to_graduation=2
)

print(recommendations.top_pathways)
print(recommendations.skill_gaps)
print(recommendations.network_contacts)
```

**Recommendation Categories:**
- **Top Pathways**: Most common routes for similar backgrounds
- **Skill Gaps**: Missing competencies for target roles
- **Network Contacts**: Alumni in relevant positions
- **Timeline**: Expected job search duration by sector
- **Preparation Steps**: Actionable next steps

## Common Patterns

### Pattern 1: New Student Onboarding

**Scenario**: First-year PhD student exploring career options.

```bash
# Generate career landscape overview
python scripts/main.py \
  --analyze \
  --degree PhD \
  --last-5-years \
  --output new_student_briefing.pdf

# Show specific pathways for their research area
python scripts/main.py \
  --pathways \
  --field "Cancer Immunotherapy" \
  --visualize \
  --output immunotherapy_careers.html
```

**Output Includes:**
- "65% of PhD alumni from our lab go to industry, 25% to academia"
- "Top companies hiring: Genentech (8 alumni), Pfizer (5), Stanford (4)"
- "Average time to first job: 3.2 months for industry, 8.1 months for academia"
- Recommended alumni to connect with

### Pattern 2: Training Grant Application

**Scenario**: Lab needs career outcome data for NIH T32 renewal.

```python
# Generate NIH-compliant report
report = tracker.generate_training_report(
    grant_type="T32",
    years=(2019, 2024),
    include_placements=True,
    include_salaries=False,  # Optional for privacy
    format="docx"
)

# Key metrics for NIH
print(f"Placement rate: {report.placement_rate}%")  # >95% target
print(f"Research-related jobs: {report.research_related}%")  # >80% target
print(f"Underrepresented minorities: {report.urm_percentage}%")
```

**NIH Requirements Met:**
- ✓ Placement rates within 6 months of graduation
- ✓ Research-related vs. non-research positions
- ✓ Diversity and underrepresented minority outcomes
- ✓ Career progression over time

### Pattern 3: Industry Partnership Development

**Scenario**: Lab wants to identify companies for collaboration.

```bash
# Analyze industry destinations
python scripts/main.py \
  --analyze \
  --filter-status industry \
  --group-by company \
  --output industry_partners.pdf

# Identify senior alumni for advisory roles
python scripts/main.py \
  --filter "position:Director,VP,Senior Manager" \
  --export contacts_for_outreach.csv
```

**Insights Generated:**
- Companies with most alumni (potential champions)
- Senior alumni in decision-making roles
- Geographic clusters for regional events
- Skills overlap with company needs

### Pattern 4: Individual Career Counseling

**Scenario**: Third-year PhD student deciding between industry and academia.

```python
# Personalized analysis for the student
student_profile = {
    "degree": "PhD",
    "research_area": "CRISPR gene editing",
    "publications": 3,
    "interests": ["startup", "gene therapy"]
}

comparison = tracker.compare_pathways(
    profile=student_profile,
    options=["industry", "startup", "academia"],
    metrics=["salary", "job_security", "work_life_balance", "availability"]
)

comparison.generate_personalized_report("career_comparison.pdf")
```

**Comparison Includes:**
- Salary ranges by path (year 1, 5, 10)
- Job market availability (positions per year)
- Alumni satisfaction ratings
- Required additional skills/training
- Network introductions

## Complete Workflow Example

**From data collection to actionable insights:**

```bash
# Step 1: Import existing alumni data
python scripts/main.py \
  --import alumni_survey_2024.csv \
  --validate \
  --output clean_alumni.json

# Step 2: Update LinkedIn profiles
python scripts/main.py \
  --update-linkedin \
  --input clean_alumni.json \
  --output updated_alumni.json

# Step 3: Generate comprehensive report
python scripts/main.py \
  --full-analysis \
  --years 2019-2024 \
  --output-dir career_report_2024/

# Step 4: Create visualization dashboard
python scripts/main.py \
  --dashboard \
  --serve \
  --port 8080
```

**Python API:**

```python
from scripts.tracker import AlumniTracker
from scripts.analyzer import CareerAnalyzer
from scripts.recommender import CareerRecommender

# Initialize
tracker = AlumniTracker(data_path="alumni_db.json")
analyzer = CareerAnalyzer()
recommender = CareerRecommender()

# Load and clean data
tracker.import_csv("alumni_2024.csv")
tracker.clean_data()

# Generate analysis
analysis = analyzer.analyze(tracker.data)
print(f"Industry rate: {analysis.industry_ratio:.1%}")
print(f"Median PhD salary (Year 1): ${analysis.salary_stats['phd_y1']['median']:,}")

# Generate recommendations for a student
recs = recommender.recommend(
    current_student={
        "year": 3,
        "degree": "PhD",
        "field": "Neuroscience"
    },
    alumni_data=tracker.data
)

print("Top 3 career paths:")
for i, path in enumerate(recs.top_paths[:3], 1):
    print(f"{i}. {path.name} ({path.probability:.0%} match)")
```

## Quality Checklist

**Data Collection:**
- [ ] Alumni consent obtained for tracking
- [ ] Data anonymized for reports (aggregated statistics only)
- [ ] GDPR/privacy compliance verified
- [ ] Regular update schedule established (annual recommended)

**Analysis Accuracy:**
- [ ] Minimum 30 alumni for statistically meaningful patterns
- [ ] Data validated for completeness (>80% response rate)
- [ ] Outliers identified and verified
- [ ] Salary data optional (respect privacy)

**Reporting:**
- [ ] **CRITICAL**: Individual privacy protected (no identifiable info in reports)
- [ ] Trends contextualized (mention sample size limitations)
- [ ] Multiple timeframes analyzed (short-term vs. long-term outcomes)
- [ ] Comparative benchmarks included (department/field averages)

**Before Sharing:**
- [ ] Alumni review opportunity provided
- [ ] **CRITICAL**: No individual salary data shared
- [ ] Aggregate statistics only in public reports
- [ ] Opt-out preferences respected

## Common Pitfalls

**Data Quality Issues:**
- ❌ **Low response rate** → Biased sample (only successful alumni respond)
  - ✅ Aim for >70% response rate; follow up multiple times
  
- ❌ **Outdated information** → Tracking 5-year-old data
  - ✅ Annual updates; LinkedIn monitoring for changes

- ❌ **Small sample size** → Drawing conclusions from n<10
  - ✅ Report confidence intervals; avoid over-interpretation

**Privacy Issues:**
- ❌ **Sharing individual salaries** → Violates privacy expectations
  - ✅ Report salary ranges or medians only; aggregate by groups

- ❌ **Identifiable case studies without consent** → Privacy breach
  - ✅ Always get written permission before highlighting individuals

**Interpretation Issues:**
- ❌ **Comparing to top-tier labs only** → Unrealistic expectations
  - ✅ Compare to similar-tier institutions; contextualize differences

- ❌ **Attributing success to lab alone** → Ignores individual factors
  - ✅ Acknowledge external factors; avoid causal claims

**Communication Issues:**
- ❌ **Discouraging academia based on low placement rates** → Biased counseling
  - ✅ Present all options neutrally; match to individual goals

- ❌ **Over-promising industry salaries** → Unrealistic expectations
  - ✅ Include salary ranges; mention geographic variations

## References

Available in `references/` directory:

- `nih_training_requirements.md` - NIH career outcome reporting standards
- `data_privacy_guide.md` - GDPR and FERPA compliance for alumni tracking
- `survey_templates.md` - Questionnaires for alumni data collection
- `benchmark_data.md` - National career outcome statistics by field
- `visualization_best_practices.md` - Ethical data visualization guidelines
- `career_counseling_ethics.md` - Professional standards for advising

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for all operations
- `tracker.py` - Alumni database management
- `analyzer.py` - Statistical analysis and reporting
- `visualizer.py` - Charts, graphs, and network maps
- `recommender.py` - Personalized career guidance
- `importers.py` - CSV, LinkedIn, survey data import
- `exporters.py` - PDF, Word, HTML report generation
- `privacy_guard.py` - Data anonymization and compliance checking

## Limitations

- **Response Bias**: Success bias (unsuccessful alumni less likely to respond)
- **Survivorship Bias**: Only tracks graduates, not those who left programs
- **Privacy Constraints**: Cannot collect detailed data without consent
- **Sample Size**: Small labs may have insufficient data for statistical significance
- **Temporal Changes**: Job market shifts may make historical data less relevant
- **Attribution Difficulty**: Cannot isolate lab impact from individual factors
- **International Tracking**: Difficulty tracking alumni who leave country

---

**🎓 Remember: Career tracking is a service to trainees, not a performance metric. Use data to empower informed decisions, not to pressure specific outcomes. Respect privacy and present all viable career paths without bias.**
