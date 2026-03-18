#!/usr/bin/env python3
"""Main orchestrator: fetch, post, and update."""

import argparse
import sys

from fetch_sam import fetch_all_legislative_opportunities
from database import upsert_many, get_unposted_opportunities, mark_as_posted, get_stats
from bluesky_poster import post_to_bluesky
from spreadsheet import export_csv
from export_json import export_json
from database import get_all_opportunities


def run(post_bluesky: bool = True, export: bool = True, active_only: bool = False):
    """Main monitoring loop iteration."""
    print("=" * 60)
    print("Congressional RFP Alert System")
    print("=" * 60)

    # 1. Fetch opportunities from SAM.gov
    print("\n[1/4] Fetching opportunities from SAM.gov...")
    opps = fetch_all_legislative_opportunities(active_only=active_only)

    # 2. Store in database
    print("\n[2/4] Updating database...")
    new_count, updated_count = upsert_many(opps)
    print(f"  New: {new_count}, Updated: {updated_count}")

    # 3. Post new opportunities to Bluesky
    if post_bluesky:
        print("\n[3/4] Posting to Bluesky...")
        unposted = get_unposted_opportunities()
        if unposted:
            print(f"  {len(unposted)} opportunities to post")
            for opp in unposted:
                uri = post_to_bluesky(opp)
                if uri:
                    mark_as_posted(opp["notice_id"], uri)
                else:
                    # Still mark as "posted" to avoid retry spam when creds not configured
                    mark_as_posted(opp["notice_id"], "skipped")
        else:
            print("  No new opportunities to post")
    else:
        print("\n[3/4] Skipping Bluesky posting")

    # 4. Export data
    if export:
        print("\n[4/4] Exporting data...")
        all_opps = get_all_opportunities()
        export_csv(all_opps)
        export_json()
    else:
        print("\n[4/4] Skipping export")

    # Summary
    stats = get_stats()
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total tracked: {stats['total']}")
    print(f"  Currently active: {stats['active']}")
    print(f"  Posted to Bluesky: {stats['posted_to_bluesky']}")
    print("  By department:")
    for dept in stats["by_department"]:
        print(f"    {dept['department']}: {dept['cnt']} total, {dept['active_cnt'] or 0} active")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Congressional RFP Alert System")
    parser.add_argument("--no-bluesky", action="store_true", help="Skip Bluesky posting")
    parser.add_argument("--no-export", action="store_true", help="Skip CSV/JSON export")
    parser.add_argument("--active-only", action="store_true", help="Only fetch active opportunities")
    parser.add_argument("--fetch-all", action="store_true", help="Fetch all opportunities (active + inactive)")
    args = parser.parse_args()

    active_only = args.active_only or not args.fetch_all

    run(
        post_bluesky=not args.no_bluesky,
        export=not args.no_export,
        active_only=active_only,
    )


if __name__ == "__main__":
    main()
