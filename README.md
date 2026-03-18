# Legislative Branch Contract Opportunities

Monitor contract opportunities from Congressional agencies on SAM.gov.

**Live dashboard:** https://jeremyschlatter-intern.github.io/congressional-rfps/

## What It Does

- Fetches RFPs, solicitations, and contract notices from 9 legislative branch agencies on SAM.gov
- Displays them in a searchable, filterable web dashboard
- Exports RSS feed, CSV, and JSON for integration with other tools
- Posts new opportunities to Bluesky (when configured)

## Agencies Tracked

- U.S. Senate
- U.S. House of Representatives
- Architect of the Capitol
- Library of Congress
- Government Publishing Office
- Government Accountability Office (GAO)
- Congressional Budget Office (CBO)
- U.S. Capitol Police
- Congressional Office for International Leadership (COIL)

## Quick Start

```bash
# Fetch active opportunities and update all exports
python3 monitor.py

# Fetch all historical opportunities too
python3 monitor.py --fetch-all

# Skip Bluesky posting
python3 monitor.py --no-bluesky
```

## Bluesky Setup

```bash
pip install atproto
export BSKY_HANDLE="your-handle.bsky.social"
export BSKY_PASSWORD="your-app-password"
python3 monitor.py
```

## Automated Monitoring

Add to crontab for hourly checks:

```
0 * * * * cd /path/to/rfps-for-congress && python3 monitor.py --no-bluesky >> /tmp/rfp-monitor.log 2>&1
```

## Data Outputs

| Output | Path | Description |
|--------|------|-------------|
| Web dashboard | `docs/index.html` | Static HTML, deployed to GitHub Pages |
| RSS feed | `docs/feed.xml` | Subscribe in any RSS reader |
| JSON data | `docs/data/opportunities.json` | Machine-readable, used by dashboard |
| CSV spreadsheet | `data/opportunities.csv` | Import into Excel/Google Sheets |
| SQLite database | `data/opportunities.db` | Full history with dedup tracking |
