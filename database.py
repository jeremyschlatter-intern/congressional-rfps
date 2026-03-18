"""SQLite database for tracking opportunities and deduplication."""

import os
import sqlite3
from typing import List, Optional, Tuple

from config import DB_PATH
from fetch_sam import Opportunity


def _ensure_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            notice_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            solicitation_number TEXT,
            type_code TEXT,
            type_name TEXT,
            is_active INTEGER,
            department TEXT,
            subtier TEXT,
            office TEXT,
            publish_date TEXT,
            modified_date TEXT,
            response_date TEXT,
            description TEXT,
            sam_url TEXT,
            awardee_name TEXT,
            award_amount TEXT,
            set_aside TEXT,
            naics_code TEXT,
            place_city TEXT,
            place_state TEXT,
            first_seen TEXT DEFAULT (datetime('now')),
            posted_to_bluesky INTEGER DEFAULT 0,
            bluesky_post_uri TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_active ON opportunities(is_active)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_department ON opportunities(department)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_posted_bluesky ON opportunities(posted_to_bluesky)
    """)
    conn.commit()
    conn.close()


def upsert_opportunity(opp: Opportunity, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Insert or update an opportunity. Returns True if it's new."""
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.execute("SELECT notice_id FROM opportunities WHERE notice_id = ?", (opp.notice_id,))
    exists = cursor.fetchone() is not None

    if exists:
        conn.execute("""
            UPDATE opportunities SET
                title=?, solicitation_number=?, type_code=?, type_name=?,
                is_active=?, department=?, subtier=?, office=?,
                modified_date=?, response_date=?, description=?, sam_url=?,
                awardee_name=?, award_amount=?, set_aside=?, naics_code=?,
                place_city=?, place_state=?
            WHERE notice_id=?
        """, (
            opp.title, opp.solicitation_number, opp.type_code, opp.type_name,
            1 if opp.is_active else 0, opp.department, opp.subtier, opp.office,
            opp.modified_date, opp.response_date, opp.description, opp.sam_url,
            opp.awardee_name, opp.award_amount, opp.set_aside, opp.naics_code,
            opp.place_city, opp.place_state,
            opp.notice_id
        ))
    else:
        conn.execute("""
            INSERT INTO opportunities (
                notice_id, title, solicitation_number, type_code, type_name,
                is_active, department, subtier, office,
                publish_date, modified_date, response_date, description, sam_url,
                awardee_name, award_amount, set_aside, naics_code,
                place_city, place_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opp.notice_id, opp.title, opp.solicitation_number, opp.type_code, opp.type_name,
            1 if opp.is_active else 0, opp.department, opp.subtier, opp.office,
            opp.publish_date, opp.modified_date, opp.response_date, opp.description, opp.sam_url,
            opp.awardee_name, opp.award_amount, opp.set_aside, opp.naics_code,
            opp.place_city, opp.place_state
        ))

    conn.commit()
    if close_conn:
        conn.close()

    return not exists


def upsert_many(opps: List[Opportunity]) -> Tuple[int, int]:
    """Insert/update many opportunities. Returns (new_count, updated_count)."""
    conn = get_connection()
    new_count = 0
    updated_count = 0
    for opp in opps:
        is_new = upsert_opportunity(opp, conn)
        if is_new:
            new_count += 1
        else:
            updated_count += 1
    conn.close()
    return new_count, updated_count


def get_unposted_opportunities() -> List[dict]:
    """Get opportunities that haven't been posted to Bluesky yet."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM opportunities
        WHERE posted_to_bluesky = 0 AND is_active = 1
        ORDER BY publish_date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_as_posted(notice_id: str, post_uri: str = ""):
    """Mark an opportunity as posted to Bluesky."""
    conn = get_connection()
    conn.execute("""
        UPDATE opportunities
        SET posted_to_bluesky = 1, bluesky_post_uri = ?
        WHERE notice_id = ?
    """, (post_uri, notice_id))
    conn.commit()
    conn.close()


def get_all_opportunities(active_only: bool = False) -> List[dict]:
    """Get all opportunities from the database."""
    conn = get_connection()
    query = "SELECT * FROM opportunities"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY publish_date DESC"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    """Get summary statistics."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM opportunities WHERE is_active = 1").fetchone()[0]
    posted = conn.execute("SELECT COUNT(*) FROM opportunities WHERE posted_to_bluesky = 1").fetchone()[0]
    by_dept = conn.execute("""
        SELECT department, COUNT(*) as cnt, SUM(is_active) as active_cnt
        FROM opportunities GROUP BY department ORDER BY cnt DESC
    """).fetchall()
    conn.close()
    return {
        "total": total,
        "active": active,
        "posted_to_bluesky": posted,
        "by_department": [dict(r) for r in by_dept],
    }


# Initialize on import
init_db()
