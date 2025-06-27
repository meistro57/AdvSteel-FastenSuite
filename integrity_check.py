from utils.db import connect_sql_server


def check_bolt_integrity(database: str = "ASTORBASE"):
    """Return list of SetBolts.BoltDefID values missing from BoltDefinition."""
    conn, cur = connect_sql_server(database)
    cur.execute("SELECT ID FROM BoltDefinition")
    bolt_ids = {row[0] for row in cur.fetchall()}
    cur.execute("SELECT BoltDefID FROM SetBolts")
    missing = [row[0] for row in cur.fetchall() if row[0] not in bolt_ids]
    conn.close()
    return missing


if __name__ == "__main__":
    missing = check_bolt_integrity()
    if missing:
        print("Missing BoltDefinition IDs:", missing)
    else:
        print("Integrity check passed")

