"""
SQLite Database module for persistence of analyses, moderation queue, and user feedback.
Stores data locally without requiring external services or cloud credentials.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection with Row factory enabled."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and indexes automatically."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Analyses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comment_text TEXT NOT NULL,
        is_toxic INTEGER NOT NULL,
        confidence REAL NOT NULL,
        primary_class TEXT NOT NULL,
        estimated_severity INTEGER NOT NULL,
        severity_label TEXT NOT NULL,
        category_scores TEXT NOT NULL,
        influential_words TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # Moderation queue table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS moderation_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id INTEGER,
        comment_text TEXT NOT NULL,
        flagged_reason TEXT NOT NULL,
        severity_level INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        reviewer_notes TEXT,
        reviewed_at TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
    );
    """)

    # User feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id INTEGER,
        is_accurate INTEGER NOT NULL,
        suggested_label TEXT,
        user_comments TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(analysis_id) REFERENCES analyses(id) ON DELETE SET NULL
    );
    """)

    # Indexes for fast filtering
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_toxic ON analyses(is_toxic);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_moderation_status ON moderation_queue(status);")

    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {settings.db_path}")


# Database CRUD helpers

def insert_analysis(
    comment_text: str,
    is_toxic: bool,
    confidence: float,
    primary_class: str,
    estimated_severity: int,
    severity_label: str,
    category_scores: Dict[str, float],
    influential_words: List[Dict[str, Any]],
    auto_flag_moderation: bool = True
) -> Dict[str, Any]:
    """Inserts a new analysis record and flags high-severity cases into the moderation queue."""
    now_str = datetime.utcnow().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO analyses (
        comment_text, is_toxic, confidence, primary_class,
        estimated_severity, severity_label, category_scores,
        influential_words, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        comment_text,
        1 if is_toxic else 0,
        float(confidence),
        primary_class,
        int(estimated_severity),
        severity_label,
        json.dumps(category_scores),
        json.dumps(influential_words),
        now_str
    ))
    analysis_id = cursor.lastrowid

    # Auto-flag for human moderation if severity >= 2 (Moderate or High)
    if auto_flag_moderation and estimated_severity >= 2:
        reason = f"Algorithmic trigger: {severity_label} severity ({confidence * 100:.1f}% confidence)"
        cursor.execute("""
        INSERT INTO moderation_queue (
            analysis_id, comment_text, flagged_reason, severity_level, status, created_at
        ) VALUES (?, ?, ?, ?, 'PENDING', ?)
        """, (
            analysis_id,
            comment_text,
            reason,
            estimated_severity,
            now_str
        ))

    conn.commit()
    conn.close()

    return get_analysis_by_id(analysis_id)


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single analysis by primary key."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "comment_text": row["comment_text"],
        "is_toxic": bool(row["is_toxic"]),
        "confidence": float(row["confidence"]),
        "primary_class": row["primary_class"],
        "estimated_severity": int(row["estimated_severity"]),
        "severity_label": row["severity_label"],
        "category_scores": json.loads(row["category_scores"]),
        "influential_words": json.loads(row["influential_words"]),
        "created_at": row["created_at"]
    }


def list_analyses(
    limit: int = 50,
    offset: int = 0,
    filter_toxic: Optional[bool] = None,
    filter_severity: Optional[int] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieves paginated analyses with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM analyses WHERE 1=1"
    params = []

    if filter_toxic is not None:
        query += " AND is_toxic = ?"
        params.append(1 if filter_toxic else 0)

    if filter_severity is not None:
        query += " AND estimated_severity = ?"
        params.append(filter_severity)

    if search:
        query += " AND comment_text LIKE ?"
        params.append(f"%{search}%")

    # Count total
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]

    # Fetch rows
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "comment_text": r["comment_text"],
            "is_toxic": bool(r["is_toxic"]),
            "confidence": float(r["confidence"]),
            "primary_class": r["primary_class"],
            "estimated_severity": int(r["estimated_severity"]),
            "severity_label": r["severity_label"],
            "category_scores": json.loads(r["category_scores"]),
            "created_at": r["created_at"]
        })

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": results
    }


def delete_analysis(analysis_id: int) -> bool:
    """Deletes an analysis record and associated moderation/feedback."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    deleted = cursor.rowcount > 0
    cursor.execute("DELETE FROM moderation_queue WHERE analysis_id = ?", (analysis_id,))
    cursor.execute("DELETE FROM user_feedback WHERE analysis_id = ?", (analysis_id,))
    conn.commit()
    conn.close()
    return deleted


def get_dashboard_statistics() -> Dict[str, Any]:
    """Computes genuine statistics strictly from local SQLite records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM analyses")
    total_records = cursor.fetchone()[0]

    if total_records == 0:
        conn.close()
        return {
            "total_analyses": 0,
            "toxic_count": 0,
            "non_toxic_count": 0,
            "toxic_percentage": 0.0,
            "severity_distribution": {0: 0, 1: 0, 2: 0, 3: 0},
            "category_breakdown": {
                "toxic": 0, "severe_toxic": 0, "obscene": 0,
                "threat": 0, "insult": 0, "identity_hate": 0
            },
            "moderation_pending": 0,
            "recent_analyses": []
        }

    cursor.execute("SELECT COUNT(*) FROM analyses WHERE is_toxic = 1")
    toxic_count = cursor.fetchone()[0]
    non_toxic_count = total_records - toxic_count

    # Severity distribution
    cursor.execute("SELECT estimated_severity, COUNT(*) FROM analyses GROUP BY estimated_severity")
    sev_rows = cursor.fetchall()
    sev_dist = {0: 0, 1: 0, 2: 0, 3: 0}
    for s_level, cnt in sev_rows:
        sev_dist[int(s_level)] = cnt

    # Moderation pending
    cursor.execute("SELECT COUNT(*) FROM moderation_queue WHERE status = 'PENDING'")
    mod_pending = cursor.fetchone()[0]

    # Category totals by parsing JSON
    cursor.execute("SELECT category_scores FROM analyses WHERE is_toxic = 1")
    cat_rows = cursor.fetchall()
    cat_totals = {
        "toxic": 0, "severe_toxic": 0, "obscene": 0,
        "threat": 0, "insult": 0, "identity_hate": 0
    }
    for (cs_json,) in cat_rows:
        try:
            scores = json.loads(cs_json)
            for cat, sc in scores.items():
                if cat in cat_totals and sc >= 0.5:
                    cat_totals[cat] += 1
        except Exception:
            pass

    # Recent 5
    cursor.execute("SELECT id, comment_text, is_toxic, estimated_severity, severity_label, confidence, created_at FROM analyses ORDER BY id DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    conn.close()

    recent = []
    for r in recent_rows:
        recent.append({
            "id": r["id"],
            "comment_text": r["comment_text"][:80] + ("..." if len(r["comment_text"]) > 80 else ""),
            "is_toxic": bool(r["is_toxic"]),
            "estimated_severity": r["estimated_severity"],
            "severity_label": r["severity_label"],
            "confidence": r["confidence"],
            "created_at": r["created_at"]
        })

    return {
        "total_analyses": total_records,
        "toxic_count": toxic_count,
        "non_toxic_count": non_toxic_count,
        "toxic_percentage": round((toxic_count / total_records) * 100, 1),
        "severity_distribution": sev_dist,
        "category_breakdown": cat_totals,
        "moderation_pending": mod_pending,
        "recent_analyses": recent
    }


def list_moderation_queue(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves moderation queue cases."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM moderation_queue WHERE status = ? ORDER BY id DESC", (status,))
    else:
        cursor.execute("SELECT * FROM moderation_queue ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "analysis_id": r["analysis_id"],
            "comment_text": r["comment_text"],
            "flagged_reason": r["flagged_reason"],
            "severity_level": r["severity_level"],
            "status": r["status"],
            "reviewer_notes": r["reviewer_notes"],
            "reviewed_at": r["reviewed_at"],
            "created_at": r["created_at"]
        })
    return items


def update_moderation_item(item_id: int, status: str, notes: Optional[str] = None) -> bool:
    """Updates the moderation action taken by a human moderator."""
    now_str = datetime.utcnow().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE moderation_queue
    SET status = ?, reviewer_notes = ?, reviewed_at = ?
    WHERE id = ?
    """, (status, notes or "", now_str, item_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def record_feedback(analysis_id: int, is_accurate: bool, suggested_label: Optional[str], comments: Optional[str]) -> int:
    """Inserts user correction or validation feedback."""
    now_str = datetime.utcnow().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO user_feedback (analysis_id, is_accurate, suggested_label, user_comments, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (analysis_id, 1 if is_accurate else 0, suggested_label or "", comments or "", now_str))
    fid = cursor.lastrowid
    conn.commit()
    conn.close()
    return fid
