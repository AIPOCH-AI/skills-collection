---
name: scientific-podcast-summary
description: Automatically summarize scientific podcasts like Huberman Lab and Nature Podcast
---

# Scientific Podcast Summary

**ID:** 189  
**Version:** 1.0.0  
**Description:** Automatically summarizes core content from Huberman Lab or Nature Podcast, generating text briefings.

---

## Usage

```bash
# Summarize latest episode
python skills/scientific-podcast-summary/scripts/main.py --podcast huberman

# Specify episode URL
python skills/scientific-podcast-summary/scripts/main.py --url "https://..."

# Save to file
python skills/scientific-podcast-summary/scripts/main.py --podcast nature --output ./summary.md
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--podcast` | Optional | huberman | Select podcast source: `huberman` or `nature` |
| `--url` | Optional | - | Directly provide podcast page URL |
| `--output` | Optional | - | Output file path |
| `--format` | Optional | markdown | Output format: `markdown`, `json` |

## Output Format

Generated briefing contains:
- 🎙️ Podcast title and release date
- 👤 Host and guest information
- 📝 Core topic overview
- 🔬 Key scientific findings/points (3-5 items)
- 💡 Practical advice/action guidelines
- 📚 Related resource links

## Dependencies

- Python 3.8+
- requests
- beautifulsoup4
- openai (or compatible API)

## Installation

```bash
pip install requests beautifulsoup4 openai
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | LLM API Key |
| `OPENAI_BASE_URL` | No | Custom API Base URL |
| `OPENAI_MODEL` | No | Model name, default `gpt-4o-mini` |

## Example Output

```markdown
# 🎙️ Huberman Lab: The Science of Sleep

**Release Date:** 2024-01-15  
**Guest:** Dr. Matthew Walker

## 📝 Core Topic

This episode delves into the neuroscience mechanisms of sleep...

## 🔬 Key Points

1. **Sleep Cycles** - Humans experience 4-6 90-minute sleep cycles each night...
2. **Importance of Deep Sleep** - During deep sleep, the brain clears metabolic waste...

## 💡 Practical Advice

- Maintain regular sleep schedule
- Avoid blue light exposure before bed
- Keep room temperature at 18-20°C
```

---

## Changelog

### v1.0.0 (2024-02-06)
- Initial release
- Support for Huberman Lab and Nature Podcast
- Support for Markdown/JSON output formats
