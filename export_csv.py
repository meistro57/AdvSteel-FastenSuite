import argparse
import csv
from utils.db import connect_sql_server


def export_table_to_csv(database: str, table: str, out_path: str) -> None:
    conn, cur = connect_sql_server(database)
    cur.execute(f"SELECT * FROM [{table}]")
    columns = [c[0] for c in cur.description]
    rows = cur.fetchall()
    conn.close()

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export table to CSV")
    parser.add_argument("database", help="Database name")
    parser.add_argument("table", help="Table name")
    parser.add_argument("output", help="Output CSV file")
    args = parser.parse_args()
    export_table_to_csv(args.database, args.table, args.output)

