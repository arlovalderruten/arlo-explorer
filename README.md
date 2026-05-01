# 🌟 Arlo's Data Explorer

**Owner:** @arlovalderruten

A collection of tools for collecting, analyzing, and synthesizing data from public APIs.

## About

This repo contains tools I built during exploration sessions. Each script fetches real data from public APIs and generates insights.

## Tools

| Script | Purpose |
|--------|---------|
| `fetch_real_data.py` | Collect from GitHub, Reddit, HN APIs |
| `internet_mood.py` | Sentiment analysis from public feeds |
| `universal_collector.py` | Weather, crypto, GitHub events |
| `world_state_dashboard.py` | Unified dashboard view |
| `daily_pulse.py` | Aggregated daily briefing |
| `narrative_generator.py` | AI-generated stories from data |
| `echo_chamber.py` | Analyzes feed diversity |

## Data Sources

- GitHub Public API (trending repos, events)
- Reddit Public API (r/news, r/worldnews, r/politics)
- Hacker News Firebase API (top stories)
- NASA APOD API (astronomy picture)
- wttr.in (weather)
- CoinGecko (crypto prices)

## Usage

```bash
# Run all tools
python3 scripts/master_explorer.py
```

## Generated Output

Check `/output/` for results:
- `internet_mood.json` - Sentiment analysis
- `world_state_dashboard.md` - Combined report
- `generated_narratives.json` - AI stories

---

*Built by Arlo on 2026-05-01*
