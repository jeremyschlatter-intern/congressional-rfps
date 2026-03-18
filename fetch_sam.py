"""Fetch contract opportunities from SAM.gov for legislative branch agencies."""

import json
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass, asdict
from typing import List, Optional

from config import LEGISLATIVE_BRANCH_AGENCIES, SAM_API_BASE, SAM_PAGE_SIZE


@dataclass
class Opportunity:
    notice_id: str
    title: str
    solicitation_number: str
    type_code: str
    type_name: str
    is_active: bool
    department: str
    subtier: str
    office: str
    publish_date: str
    modified_date: str
    response_date: Optional[str]
    description: str
    sam_url: str
    awardee_name: Optional[str] = None
    award_amount: Optional[str] = None
    set_aside: Optional[str] = None
    naics_code: Optional[str] = None
    place_city: Optional[str] = None
    place_state: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def _parse_opportunity(result: dict) -> Opportunity:
    """Parse a SAM.gov search result into an Opportunity."""
    orgs = result.get("organizationHierarchy", [])
    department = next((o["name"] for o in orgs if o["level"] == 1), "")
    subtier = next((o["name"] for o in orgs if o["level"] == 2), "")
    office = next((o["name"] for o in orgs if o["level"] == 3), "")
    office_addr = next((o.get("address", {}) for o in orgs if o["level"] == 3), {})

    descriptions = result.get("descriptions", [])
    desc_text = ""
    if descriptions:
        raw = descriptions[0].get("content", "")
        # Strip HTML tags and decode entities
        import re
        import html
        desc_text = re.sub(r"<[^>]+>", " ", raw).strip()
        desc_text = html.unescape(desc_text)
        desc_text = re.sub(r"\s+", " ", desc_text)
        if len(desc_text) > 500:
            desc_text = desc_text[:497] + "..."

    notice_id = result.get("_id", "")
    opp_type = result.get("type", {})
    award = result.get("award", {})
    awardee = award.get("awardee", {}) if award else {}

    response_date = result.get("responseDate")
    if response_date:
        response_date = response_date[:19]  # Trim timezone

    return Opportunity(
        notice_id=notice_id,
        title=result.get("title", "").strip(),
        solicitation_number=result.get("solicitationNumber", ""),
        type_code=opp_type.get("code", ""),
        type_name=opp_type.get("value", ""),
        is_active=result.get("isActive", False),
        department=department,
        subtier=subtier,
        office=office,
        publish_date=result.get("publishDate", "")[:19],
        modified_date=result.get("modifiedDate", "")[:19],
        response_date=response_date,
        description=desc_text,
        sam_url=f"https://sam.gov/opp/{notice_id}/view",
        awardee_name=awardee.get("name") if awardee else None,
        award_amount=str(award.get("amount")) if award and award.get("amount") else None,
        set_aside=result.get("setAside"),
        naics_code=result.get("naicsCode"),
        place_city=office_addr.get("city") if office_addr else None,
        place_state=office_addr.get("state") if office_addr else None,
    )


def fetch_opportunities(org_id: str, active_only: bool = False, max_pages: int = 10) -> List[Opportunity]:
    """Fetch all opportunities for a given organization ID."""
    opportunities = []
    page = 0

    while page < max_pages:
        params = {
            "index": "opp",
            "page": str(page),
            "sort": "-modifiedDate",
            "size": str(SAM_PAGE_SIZE),
            "mode": "search",
            "responseType": "json",
            "q": "",
            "qMode": "ALL",
            "organization_id": org_id,
        }
        if active_only:
            params["is_active"] = "true"

        url = SAM_API_BASE + "?" + urllib.parse.urlencode(params)

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CongressionalRFPAlert/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error fetching page {page} for org {org_id}: {e}")
            break

        results = data.get("_embedded", {}).get("results", [])
        if not results:
            break

        for result in results:
            try:
                opp = _parse_opportunity(result)
                opportunities.append(opp)
            except Exception as e:
                print(f"Error parsing opportunity: {e}")

        total = data.get("page", {}).get("totalElements", 0)
        fetched = (page + 1) * SAM_PAGE_SIZE
        if fetched >= total:
            break

        page += 1
        time.sleep(0.5)  # Be polite

    return opportunities


def fetch_all_legislative_opportunities(active_only: bool = False) -> List[Opportunity]:
    """Fetch opportunities from all legislative branch agencies."""
    all_opps = []
    for org_id, name in LEGISLATIVE_BRANCH_AGENCIES.items():
        print(f"Fetching from {name} (org_id={org_id})...")
        opps = fetch_opportunities(org_id, active_only=active_only)
        print(f"  Found {len(opps)} opportunities")
        all_opps.extend(opps)
        time.sleep(1)  # Be polite between agencies

    # Deduplicate by notice_id
    seen = set()
    unique = []
    for opp in all_opps:
        if opp.notice_id not in seen:
            seen.add(opp.notice_id)
            unique.append(opp)

    print(f"\nTotal unique opportunities: {len(unique)}")
    return unique


if __name__ == "__main__":
    opps = fetch_all_legislative_opportunities(active_only=True)
    for opp in opps[:5]:
        print(f"\n{'='*60}")
        print(f"Title: {opp.title}")
        print(f"Agency: {opp.department} > {opp.subtier} > {opp.office}")
        print(f"Type: {opp.type_name}")
        print(f"Published: {opp.publish_date}")
        print(f"Response Due: {opp.response_date}")
        print(f"URL: {opp.sam_url}")
        if opp.description:
            print(f"Description: {opp.description[:200]}")
