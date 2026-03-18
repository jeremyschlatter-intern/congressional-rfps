"""Export opportunities to JSON for the web dashboard."""

import json
import os
from datetime import datetime, timezone

from config import JSON_PATH
from database import get_all_opportunities, get_stats


def export_json():
    """Export all opportunities to JSON for the web dashboard."""
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)

    opps = get_all_opportunities()
    stats = get_stats()

    # Convert is_active from int to bool for cleaner JSON
    for opp in opps:
        opp["is_active"] = bool(opp.get("is_active"))
        # Truncate descriptions for JSON size (full text stays in DB)
        if opp.get("description") and len(opp["description"]) > 1000:
            opp["description"] = opp["description"][:997] + "..."

    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "opportunities": opps,
    }

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"Exported {len(opps)} opportunities to {JSON_PATH}")


if __name__ == "__main__":
    export_json()
