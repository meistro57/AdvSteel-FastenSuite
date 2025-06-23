# sql_query.py
"""Run arbitrary SQL queries against the configured server."""

import argparse
import json
import pyodbc
from typing import List, Dict, Optional, Any
from config import DB_CONFIG


def connect_sql_server():
    """Connect to the SQL Server using settings from config.py."""
    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
    )
    print(f"🔌 Connecting to {DB_CONFIG['server']}...")
    conn = pyodbc.connect(conn_str, autocommit=True)
    print("✅ Connected successfully.")
    return conn


def run_query(cursor, query: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
    """Execute a SQL query and return results as a list of dicts."""
    if database:
        cursor.execute(f"USE [{database}]")
    cursor.execute(query)
    if cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return rows


def format_table(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No results."
    columns = list(rows[0].keys())
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row[c])))
    header = " | ".join(c.ljust(widths[c]) for c in columns)
    sep = "-+-".join("-" * widths[c] for c in columns)
    lines = [header, sep]
    for row in rows:
        lines.append(" | ".join(str(row[c]).ljust(widths[c]) for c in columns))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a direct SQL query.")
    parser.add_argument("query", help="SQL statement to execute")
    parser.add_argument("-d", "--database", help="Database to USE before executing")
    parser.add_argument(
        "-o",
        "--output",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )
    args = parser.parse_args()

    conn = connect_sql_server()
    cur = conn.cursor()
    results = run_query(cur, args.query, args.database)
    conn.close()

    if args.output == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(format_table(results))


if __name__ == "__main__":
    main()
