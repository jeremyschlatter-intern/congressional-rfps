"""Generate RSS feed of recent opportunities."""

import os
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

from config import JSON_PATH
from database import get_all_opportunities


RSS_PATH = os.path.join(os.path.dirname(__file__), "docs", "feed.xml")

AGENCY_SHORT = {
    "THE LEGISLATIVE BRANCH": "U.S. Capitol Police",
    "SENATE, THE": "U.S. Senate",
    "HOUSE OF REPRESENTATIVES, THE": "U.S. House",
    "ARCHITECT OF THE CAPITOL": "Architect of the Capitol",
    "LIBRARY OF CONGRESS": "Library of Congress",
    "UNITED STATES GOVERNMENT PUBLISHING OFFICE": "Gov. Publishing Office",
    "GOVERNMENT ACCOUNTABILITY OFFICE": "GAO",
    "CONGRESSIONAL BUDGET OFFICE": "CBO",
    "Congressional Office for International Leadership": "COIL",
}


def export_rss(site_url: str = "https://jeremyschlatter-intern.github.io/congressional-rfps"):
    """Generate RSS feed XML."""
    opps = get_all_opportunities(active_only=True)

    rss = Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "Legislative Branch Contract Opportunities"
    SubElement(channel, "link").text = site_url
    SubElement(channel, "description").text = (
        "New contract opportunities from the U.S. House, Senate, "
        "and legislative branch support agencies, sourced from SAM.gov."
    )
    SubElement(channel, "language").text = "en-us"
    SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S +0000"
    )

    atom_link = SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", f"{site_url}/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for opp in opps[:100]:  # Latest 100 active
        item = SubElement(channel, "item")
        agency = AGENCY_SHORT.get(opp["department"], opp["department"])
        SubElement(item, "title").text = f"[{agency}] {opp['title']}"
        SubElement(item, "link").text = opp["sam_url"]
        SubElement(item, "guid", isPermaLink="true").text = opp["sam_url"]

        desc_parts = [f"<b>Agency:</b> {agency}"]
        if opp.get("office"):
            desc_parts.append(f"<b>Office:</b> {opp['office']}")
        desc_parts.append(f"<b>Type:</b> {opp.get('type_name', 'N/A')}")
        if opp.get("solicitation_number"):
            desc_parts.append(f"<b>Solicitation #:</b> {opp['solicitation_number']}")
        if opp.get("response_date"):
            desc_parts.append(f"<b>Response Due:</b> {opp['response_date'][:10]}")
        if opp.get("description"):
            desc_parts.append(f"<br/>{opp['description'][:500]}")
        SubElement(item, "description").text = "<br/>".join(desc_parts)

        if opp.get("publish_date"):
            try:
                pub = datetime.fromisoformat(opp["publish_date"])
                SubElement(item, "pubDate").text = pub.strftime(
                    "%a, %d %b %Y %H:%M:%S +0000"
                )
            except (ValueError, TypeError):
                pass

        SubElement(item, "category").text = agency

    os.makedirs(os.path.dirname(RSS_PATH), exist_ok=True)
    tree = ElementTree(rss)
    tree.write(RSS_PATH, encoding="unicode", xml_declaration=True)
    print(f"Exported RSS feed with {min(len(opps), 100)} items to {RSS_PATH}")


if __name__ == "__main__":
    export_rss()
