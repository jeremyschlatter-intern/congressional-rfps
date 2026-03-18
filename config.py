"""Configuration for the Congressional RFP Alert System."""

import os

# Legislative branch agencies and their SAM.gov organization IDs
LEGISLATIVE_BRANCH_AGENCIES = {
    "300000001": "THE LEGISLATIVE BRANCH",
    "300000004": "ARCHITECT OF THE CAPITOL",
    "100094131": "LIBRARY OF CONGRESS",
    "300000005": "US GOVERNMENT PUBLISHING OFFICE",
}

# SAM.gov API configuration
SAM_API_BASE = "https://sam.gov/api/prod/sgs/v1/search/"
SAM_DETAIL_URL = "https://sam.gov/opp/{notice_id}/view"
SAM_PAGE_SIZE = 100

# Bluesky configuration
BSKY_HANDLE = os.environ.get("BSKY_HANDLE", "")
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD", "")

# File paths
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "opportunities.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "opportunities.csv")
JSON_PATH = os.path.join(os.path.dirname(__file__), "docs", "data", "opportunities.json")
