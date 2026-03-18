# After-Action Report: Legislative Branch Contract Opportunities Tracker

## Project Summary

**Goal:** Create an alert system for new Requests for Proposals (contracts) from the House, Senate, and legislative branch support agencies. Post alerts to Bluesky and maintain a spreadsheet.

**Deliverables:**
- Live web dashboard: https://jeremyschlatter-intern.github.io/congressional-rfps/
- RSS feed for passive monitoring
- CSV export for spreadsheet use
- Bluesky posting module (ready for credentials)
- Automated monitoring pipeline
- Source code: https://github.com/jeremyschlatter-intern/congressional-rfps

**Data:** 2,735 contract opportunities tracked across 9 legislative branch agencies, 62 currently active.

---

## Process and Obstacles

### 1. Finding the Right Data Source

**Challenge:** The project specified SAM.gov as the data source, but SAM.gov's documented public API requires an API key that takes 1-4 weeks to obtain through registration. The documented endpoints (`api.sam.gov/prod/opportunities/v2/search`) returned empty 404 responses for all my test requests, even with various key attempts.

**What I tried:**
- Testing the documented API with `DEMO_KEY` (doesn't work; SAM.gov doesn't use api.data.gov keys)
- Testing without any key (same 404 response)
- Researching alternative data access methods (RSS feeds, bulk downloads)

**Resolution:** I used Chrome browser automation to navigate SAM.gov's search interface and captured the network requests. I discovered that SAM.gov's website uses an internal search API at `sam.gov/api/prod/sgs/v1/search/` that requires no API key and returns full JSON data. This API supports filtering by organization ID, pagination, and all the fields needed for the project.

### 2. Identifying All Legislative Branch Agencies

**Challenge:** The project asked for "House, Senate, and its support agencies," but SAM.gov doesn't have a single "legislative branch" filter that captures everything. The agencies are registered as separate top-level departments with different organization IDs.

**What I tried:**
- Started with the obvious "THE LEGISLATIVE BRANCH" org (300000001), which only contained US Capitol Police procurement
- Searched for individual agencies by name
- Used the SAM.gov Federal Organizations dropdown to discover org IDs

**Resolution:** Systematically tested organization IDs and found 9 agencies:

| Agency | Org ID | Total Opps | Active |
|--------|--------|-----------|--------|
| THE LEGISLATIVE BRANCH (Capitol Police) | 300000001 | 67 | 0 |
| THE SENATE | 300000002 | 316 | 4 |
| THE HOUSE OF REPRESENTATIVES | 300000003 | 52 | 2 |
| ARCHITECT OF THE CAPITOL | 300000004 | 221 | 4 |
| US GOVERNMENT PUBLISHING OFFICE | 300000005 | 1000+ | 33 |
| GOVERNMENT ACCOUNTABILITY OFFICE | 300000006 | 67 | 0 |
| CONGRESSIONAL BUDGET OFFICE | 300000007 | 8 | 0 |
| CONGRESSIONAL OFFICE FOR INTL LEADERSHIP | 300000009 | 2 | 0 |
| LIBRARY OF CONGRESS | 100094131 | 1000+ | 19 |

The Senate and House were nearly missed in my first pass -- I initially only had 4 agencies. A DC reviewer agent identified this gap, and I corrected it.

### 3. Bluesky Account Creation

**Challenge:** The project requires posting to Bluesky, which needs an account. My safety constraints prohibit creating new accounts on behalf of users.

**Resolution:** I built the complete Bluesky posting module with proper AT Protocol integration (rich text facets for links, hashtags, rate limiting), but left the account creation as a setup step. The module is tested and ready -- it just needs `BSKY_HANDLE` and `BSKY_PASSWORD` environment variables to be set. This is documented in the README.

### 4. Quality Feedback via DC Reviewer Agent

**Challenge:** The project instructions asked me to iterate with a DC persona until the solution is well-polished.

**What I did:** I created an agent teammate playing Daniel Schuman, the person who originally proposed this project. The agent reviewed all code and the live dashboard, then provided detailed feedback covering agency coverage, usefulness, presentation, data quality, and Bluesky posting.

**Key feedback incorporated:**
- Added 5 missing agencies (Senate, House, GAO, CBO, COIL) -- this was flagged as the #1 issue
- Added RSS feed for passive monitoring (flagged as essential for DC audience)
- Added CSV download from the dashboard
- Added about/explainer section
- Added sort controls and shareable URL filter state
- Removed "N/A" for missing dates
- Added hashtags to Bluesky posts for discoverability
- Fixed Bluesky rate limiting and posting logic
- Changed title from "Congressional" to "Legislative Branch" for precision

---

## Architecture

```
SAM.gov API  -->  fetch_sam.py  -->  database.py (SQLite)
                                        |
                                        +--> bluesky_poster.py  --> Bluesky
                                        +--> export_json.py     --> docs/data/opportunities.json
                                        +--> export_rss.py      --> docs/feed.xml
                                        +--> spreadsheet.py     --> data/opportunities.csv

                  monitor.py (orchestrator, runs all above)

                  docs/index.html (static dashboard, loads JSON)
                    --> GitHub Pages deployment
```

## Team Members

1. **Main Agent (me):** Architecture, implementation, data source discovery, browser automation for SAM.gov research, GitHub Pages deployment.

2. **DC Reviewer Agent ("Daniel Schuman"):** Reviewed the dashboard and codebase from the perspective of a Congressional transparency expert. Provided the detailed feedback that drove the second round of improvements, particularly the agency coverage gap and RSS/CSV additions.

---

## What I Would Do With More Resources

1. **Bluesky account setup:** Create a dedicated bot account (e.g., `@legbranch-rfps.bsky.social`) and configure it to post automatically.

2. **Email digest:** The DC reviewer flagged this as highly valuable. A weekly email summarizing new opportunities would reach more of the target audience than Bluesky alone.

3. **Google Sheets integration:** Currently exporting to CSV. A live Google Sheet that updates automatically would be more accessible and shareable for DC users.

4. **Outreach:** If I could contact people, I would share this tool with Congressional transparency advocates, the Data Coalition, government contracting communities, and relevant Bluesky accounts to drive adoption.

5. **SAM.gov API key:** Getting an official API key would provide better rate limits and access to additional fields (NAICS codes, set-aside details, full award data) that the search API doesn't include.

---

## Technical Notes

- **No API key required:** The solution uses SAM.gov's internal search endpoint which doesn't require authentication, making it immediately usable without registration delays.
- **Respectful data access:** All API calls include delays between requests and use standard HTTP headers. No anti-bot measures are bypassed.
- **Static deployment:** The dashboard is a single HTML file that loads data from a JSON file, deployable anywhere (GitHub Pages, any web server). No backend server required for the dashboard.
- **Cron-ready:** Running `python monitor.py` fetches new data, posts to Bluesky, and updates all exports. Add to cron for automated monitoring.
