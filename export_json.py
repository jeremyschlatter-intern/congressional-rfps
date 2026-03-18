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
