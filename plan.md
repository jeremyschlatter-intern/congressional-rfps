# Congressional RFP Alert System - Implementation Plan

## Goal
Monitor SAM.gov for new contract opportunities from legislative branch agencies (House, Senate, and support agencies). Alert via Bluesky posts and maintain a searchable spreadsheet.

## Legislative Branch Agencies on SAM.gov
| Agency | Org ID | Active Opps |
|--------|--------|-------------|
| THE LEGISLATIVE BRANCH (Capitol Police) | 300000001 | 0 |
| ARCHITECT OF THE CAPITOL | 300000004 | 4 |
| LIBRARY OF CONGRESS | 100094131 | 17 |
| US GOVERNMENT PUBLISHING OFFICE | 300000005 | 33 |

## Data Source
SAM.gov internal search API (no key required):
```
https://sam.gov/api/prod/sgs/v1/search/?index=opp&page=0&sort=-modifiedDate&size=100&mode=search&responseType=json&organization_id={ORG_ID}&is_active=true
```

## Components

### 1. SAM.gov Fetcher (`fetch_sam.py`)
- Queries each legislative branch org ID
- Returns structured opportunity data
- Handles pagination

### 2. SQLite Database (`database.py`)
- Tracks all seen opportunities
- Deduplication for Bluesky posts
- Records post timestamps

### 3. Bluesky Poster (`bluesky_poster.py`)
- Formats opportunity info into concise posts
- Posts with link to SAM.gov detail page
- Uses `atproto` Python SDK

### 4. Spreadsheet Manager (`spreadsheet.py`)
- Maintains CSV with all opportunities
- Auto-updates when new opps found
- Fields: title, agency, type, posted date, response deadline, solicitation #, link

### 5. Web Dashboard (`docs/index.html`)
- Static HTML/JS dashboard (deployable to GitHub Pages)
- Loads data from JSON file
- Filterable by agency, notice type
- Links directly to SAM.gov

### 6. Monitor/Orchestrator (`monitor.py`)
- Main entry point
- Fetches new opportunities
- Posts to Bluesky
- Updates spreadsheet + JSON
- Can run via cron

## Deployment
- GitHub Pages for web dashboard
- Cron job for periodic monitoring
- CSV accessible via GitHub raw URL
