# services/anchor_builder.py
"""Service for creating complete anchor definitions in the database."""

from __future__ import annotations

from typing import Any, Dict
import re

from utils.db import connect_sql_server


def _sanitize_run_name_component(value: str) -> str:
    """Return a safe run-name component with spaces and symbols normalized."""
    normalized = re.sub(r"\s+", "_", value.strip())
    return re.sub(r"[^A-Za-z0-9_]+", "_", normalized).strip("_")


def _build_run_name(standard: str, grade: str, diameter: float) -> str:
    """Build a unique RunName like Standard_Grade_Diameter."""
    standard_part = _sanitize_run_name_component(standard)
    grade_part = _sanitize_run_name_component(grade)
    diameter_part = _sanitize_run_name_component(f"{diameter}")
    return f"{standard_part}_{grade_part}_{diameter_part}"


def _get_rule_table(cursor) -> str:
    """Return the rules table name available in the schema."""
    cursor.execute(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_NAME IN ('Rules', 'Rule_Anchors')"
    )
    rows = [row[0] for row in cursor.fetchall()]
    if "Rules" in rows:
        return "Rules"
    if "Rule_Anchors" in rows:
        return "Rule_Anchors"
    raise ValueError("Neither Rules nor Rule_Anchors table exists in the schema.")


def _validate_payload(anchor_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize anchor payload data."""
    required_fields = [
        "display_name",
        "standard",
        "diameter",
        "grade",
        "part_name",
        "head_width",
        "thickness",
        "set_name",
        "available_lengths",
    ]
    missing = [field for field in required_fields if field not in anchor_data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    available_lengths = anchor_data["available_lengths"]
    if not isinstance(available_lengths, list) or not available_lengths:
        raise ValueError("available_lengths must be a non-empty list.")

    return {
        "display_name": str(anchor_data["display_name"]),
        "standard": str(anchor_data["standard"]),
        "diameter": float(anchor_data["diameter"]),
        "grade": str(anchor_data["grade"]),
        "part_name": str(anchor_data["part_name"]),
        "head_width": float(anchor_data["head_width"]),
        "thickness": float(anchor_data["thickness"]),
        "set_name": str(anchor_data["set_name"]),
        "available_lengths": [float(length) for length in available_lengths],
    }


def create_full_anchor(anchor_data: Dict[str, Any]) -> Dict[str, str]:
    """Create a full anchor definition across related tables."""
    conn, cursor = connect_sql_server()
    conn.autocommit = False
    try:
        payload = _validate_payload(anchor_data)
        run_name = _build_run_name(
            payload["standard"],
            payload["grade"],
            payload["diameter"],
        )

        cursor.execute("BEGIN TRANSACTION")

        cursor.execute(
            "INSERT INTO [Anchor_Name] ([RunName], [Name], [Standard], [PartName]) "
            "VALUES (?, ?, ?, ?)",
            (
                run_name,
                payload["display_name"],
                payload["standard"],
                payload["part_name"],
            ),
        )

        cursor.execute(
            "INSERT INTO [Anchor_Deff] ([Name], [Diameter], [Thickness], [HeadWidth]) "
            "VALUES (?, ?, ?, ?)",
            (
                run_name,
                payload["diameter"],
                payload["thickness"],
                payload["head_width"],
            ),
        )

        rule_table = _get_rule_table(cursor)
        for length in payload["available_lengths"]:
            cursor.execute(
                f"INSERT INTO [{rule_table}] ([Name], [Rule], [BoltLength]) "
                "VALUES (?, ?, ?)",
                (
                    run_name,
                    payload["set_name"],
                    length,
                ),
            )

        cursor.execute("COMMIT")
        return {"status": "success", "run_name": run_name}
    except Exception as exc:  # noqa: BLE001 - return structured error for API clients.
        try:
            cursor.execute("ROLLBACK")
        except Exception:
            pass
        return {"status": "error", "message": str(exc)}
    finally:
        conn.close()
