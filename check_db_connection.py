#!/usr/bin/env python3
"""Simple script to verify SQL Server connectivity."""

import sys

import pyodbc

from config import DB_CONFIG, DEFAULT_DATABASE


def main() -> None:
    """Attempt to connect to the configured SQL Server."""
    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
    )
    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()
        if DEFAULT_DATABASE:
            cursor.execute(f"USE [{DEFAULT_DATABASE}]")
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Connection successful: {result[0]}")
    except Exception as exc:
        print(f"Connection failed: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
