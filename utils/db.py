# utils/db.py
"""Helper for connecting to the configured SQL Server."""

import pyodbc
from typing import Tuple

from config import DB_CONFIG, DEFAULT_DATABASE


def connect_sql_server(
    database: str = DEFAULT_DATABASE,
) -> Tuple[pyodbc.Connection, pyodbc.Cursor]:
    """Return a connection and cursor to the configured SQL Server."""
    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
    )
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    if database:
        cursor.execute(f"USE [{database}]")
    return conn, cursor
