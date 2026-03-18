"""Manage the CSV spreadsheet of opportunities."""

import csv
import os
from typing import List

from config import CSV_PATH


CSV_FIELDS = [
    "title",
    "department",
    "subtier",
    "office",
    "type_name",
    "solicitation_number",
    "publish_date",
    "response_date",
    "is_active",
    "set_aside",
    "description",
    "sam_url",
    "awardee_name",
    "award_amount",
]


def export_csv(opportunities: List[dict]):
    """Export opportunities to CSV file."""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for opp in opportunities:
            row = {k: opp.get(k, "") for k in CSV_FIELDS}
            # Convert is_active from int to string
            row["is_active"] = "Active" if opp.get("is_active") else "Inactive"
            # Clean up dates
            for date_field in ["publish_date", "response_date"]:
                if row[date_field]:
                    row[date_field] = row[date_field][:10]
            writer.writerow(row)

    print(f"Exported {len(opportunities)} opportunities to {CSV_PATH}")


if __name__ == "__main__":
    from database import get_all_opportunities
    opps = get_all_opportunities()
    if opps:
        export_csv(opps)
    else:
        print("No opportunities in database. Run monitor.py first.")
