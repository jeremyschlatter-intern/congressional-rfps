"""Post new contract opportunities to Bluesky."""

import re
from datetime import datetime, timezone
from typing import Optional

from config import BSKY_HANDLE, BSKY_PASSWORD


# Agency short names for compact posts
AGENCY_SHORT = {
    "THE LEGISLATIVE BRANCH": "Capitol Police",
    "THE SENATE": "U.S. Senate",
    "THE HOUSE OF REPRESENTATIVES": "U.S. House",
    "SENATE, THE": "U.S. Senate",
    "HOUSE OF REPRESENTATIVES, THE": "U.S. House",
    "ARCHITECT OF THE CAPITOL": "Architect of the Capitol",
    "LIBRARY OF CONGRESS": "Library of Congress",
    "UNITED STATES GOVERNMENT PUBLISHING OFFICE": "Gov Publishing Office",
    "GOVERNMENT ACCOUNTABILITY OFFICE": "GAO",
    "CONGRESSIONAL BUDGET OFFICE": "CBO",
    "CONGRESSIONAL OFFICE FOR INTERNATIONAL LEADERSHIP": "COIL",
}

# Notice type emoji
TYPE_ICON = {
    "Solicitation": "📋",
    "Combined Synopsis/Solicitation": "📋",
    "Sources Sought": "🔍",
    "Award Notice": "🏆",
    "Special Notice": "📢",
    "Presolicitation": "📣",
    "Modification/Amendment/Cancel": "✏️",
    "Intent to Bundle Requirements": "📦",
}


def format_post(opp: dict) -> str:
    """Format an opportunity as a Bluesky post (max 300 chars)."""
    agency = AGENCY_SHORT.get(opp["department"], opp["department"])
    icon = TYPE_ICON.get(opp["type_name"], "📄")
    title = opp["title"]

    # Format response deadline if available
    deadline = ""
    if opp.get("response_date"):
        try:
            dt = datetime.fromisoformat(opp["response_date"])
            deadline = f"\n⏰ Due: {dt.strftime('%b %d, %Y')}"
        except (ValueError, TypeError):
            pass

    tags = "#GovCon #Congress #LegBranch"

    # Build post
    post = f"{icon} New {opp['type_name']} from {agency}\n\n{title}{deadline}\n\n{opp['sam_url']}\n\n{tags}"

    # Trim if too long (Bluesky limit is 300 graphemes)
    if len(post) > 295:
        # Shorten the title
        available = 295 - len(post) + len(title)
        if available > 20:
            title = title[:available - 3] + "..."
            post = f"{icon} New {opp['type_name']} from {agency}\n\n{title}{deadline}\n\n{opp['sam_url']}\n\n{tags}"
        else:
            # Drop tags if still too long
            post = f"{icon} New {opp['type_name']} from {agency}\n\n{title}{deadline}\n\n{opp['sam_url']}"
            if len(post) > 295:
                post = post[:292] + "..."

    return post


def _extract_url_facets(text: str) -> list:
    """Extract URL byte positions for Bluesky rich text facets."""
    facets = []
    url_pattern = re.compile(r'https?://\S+')
    text_bytes = text.encode('utf-8')

    for match in url_pattern.finditer(text):
        url = match.group()
        start = len(text[:match.start()].encode('utf-8'))
        end = start + len(url.encode('utf-8'))
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
        })
    return facets


def post_to_bluesky(opp: dict) -> Optional[str]:
    """Post an opportunity to Bluesky. Returns post URI or None on failure."""
    if not BSKY_HANDLE or not BSKY_PASSWORD:
        print(f"  Bluesky credentials not configured. Would post: {opp['title'][:60]}...")
        return None

    try:
        from atproto import Client

        client = Client()
        client.login(BSKY_HANDLE, BSKY_PASSWORD)

        text = format_post(opp)
        facets = _extract_url_facets(text)

        post = client.send_post(text=text, facets=facets if facets else None)
        print(f"  Posted to Bluesky: {opp['title'][:60]}...")
        return post.uri
    except ImportError:
        print("  atproto library not installed. Run: pip install atproto")
        return None
    except Exception as e:
        print(f"  Error posting to Bluesky: {e}")
        return None


if __name__ == "__main__":
    # Test post formatting
    test_opp = {
        "department": "LIBRARY OF CONGRESS",
        "type_name": "Solicitation",
        "title": "IT Operational Support Services IDIQ",
        "response_date": "2026-04-15T12:00:00",
        "sam_url": "https://sam.gov/opp/abc123/view",
    }
    print(format_post(test_opp))
    print(f"\nLength: {len(format_post(test_opp))}")
