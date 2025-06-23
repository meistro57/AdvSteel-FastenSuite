# sql_dump.py

import os
import json
from utils.db import connect_sql_server

OUTPUT_DIR = "sql_dump"

def get_databases(cursor):
    cursor.execute("SELECT name, database_id FROM sys.databases ORDER BY name")
    all_dbs = [row.name for row in cursor.fetchall()]

    # Filter for ASTOR .mdf files under STEEL\DATA
    filtered = []
    for db in all_dbs:
        path = db.lower()
        if (
            "steel\\data" in path or "steel/data" in path
        ) and "astor" in path and db.lower().endswith(".mdf"):
            filtered.append(db)
    return filtered

def sanitize_name(mdf_path):
    return os.path.splitext(os.path.basename(mdf_path))[0].upper()

def get_tables(cursor):
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    return [row[0] for row in cursor.fetchall()]

def dump_table(cursor, db_name, table_name):
    try:
        cursor.execute(f"SELECT * FROM [{table_name}]")
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        file_name = f"{db_name}__{table_name}.json"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "_source_database": db_name,
                "_table_name": table_name,
                "data": rows
            }, f, indent=2, ensure_ascii=False)

        print(f"✅ Dumped {file_name} ({len(rows)} rows)")
    except Exception as e:
        print(f"❌ Failed to dump {db_name}.{table_name}: {e}")

def main():
    conn = connect_sql_server()
    cursor = conn.cursor()

    databases = get_databases(cursor)
    print(f"\n📦 Found {len(databases)} core Advance Steel databases")

    for db in databases:
        db_label = sanitize_name(db)
        print(f"\n🔍 Processing: {db_label}")
        try:
            cursor.execute(f"USE [{db}]")
            tables = get_tables(cursor)
            print(f" - Found {len(tables)} tables")
            for table in tables:
                dump_table(cursor, db_label, table)
        except Exception as e:
            print(f"❌ Error in {db_label}: {e}")

    conn.close()
    print("\n🎉 Dump complete.")

if __name__ == "__main__":
    main()
