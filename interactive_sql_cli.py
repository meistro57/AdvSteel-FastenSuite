# interactive_sql_cli.py
import os
import pyodbc
import difflib
import json

# Predefined search paths
SEARCH_PATHS = [
    r'C:\PROGRAMDATA\AUTODESK\ADVANCE STEEL 2025'
]

def find_mdf_files():
    mdf_files = []
    for base in SEARCH_PATHS:
        for root, _, files in os.walk(base):
            for file in files:
                if file.lower().endswith('.mdf'):
                    mdf_files.append(os.path.join(root, file))
    return sorted(mdf_files)

def connect_to_mdf(mdf_path):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=(LocalDB)\\ADVANCESTEEL2025;"
        f"Integrated Security=true;"
        f"AttachDbFilename={mdf_path};"
    )
    return pyodbc.connect(conn_str)

def get_table_names(cursor):
    cursor.execute(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    )
    return sorted([row[0] for row in cursor.fetchall()])

def preview_table(cursor, table_name, limit=5):
    cursor.execute(f"SELECT TOP {limit} * FROM [{table_name}]")
    rows = cursor.fetchall()
    if not rows:
        return [], []
    columns = [col[0] for col in cursor.description]
    return columns, rows

def get_distinct_values(cursor, table_name, column_name):
    cursor.execute(f"SELECT DISTINCT [{column_name}] FROM [{table_name}]")
    return [str(row[0]) for row in cursor.fetchall() if row[0] is not None]

def export_to_json(columns, rows, table_name):
    records = [dict(zip(columns, row)) for row in rows]
    filename = f"results_{table_name}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=4)
    print(f"\n💾 Saved {len(rows)} result(s) to '{filename}'")

def main():
    print("📦 Scanning for available .MDF databases...")
    mdf_files = find_mdf_files()
    if not mdf_files:
        print("❌ No .MDF files found in search paths.")
        return

    for idx, path in enumerate(mdf_files, 1):
        print(f"{idx:3d}. {os.path.basename(path)}")
    
    selected = input("\n🔢 Select a database by number: ").strip()
    if not selected.isdigit() or not (1 <= int(selected) <= len(mdf_files)):
        print("❌ Invalid selection.")
        return

    mdf_path = mdf_files[int(selected) - 1]
    print(f"🔌 Connecting to: {mdf_path}")
    
    try:
        conn = connect_to_mdf(mdf_path)
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    try:
        tables = get_table_names(cursor)
    except Exception as e:
        print(f"❌ Could not fetch tables: {e}")
        return

    print("\n📄 Available tables (alphabetical):")
    for idx, table in enumerate(tables, 1):
        print(f"{idx:3d}. {table}")

    table_choice = input("\n🔢 Choose a table by number: ").strip()
    if not table_choice.isdigit() or not (1 <= int(table_choice) <= len(tables)):
        print("❌ Invalid selection.")
        return

    table_name = tables[int(table_choice) - 1]
    print(f"\n🔍 Previewing top records from {table_name}...")
    columns, rows = preview_table(cursor, table_name)
    if not columns:
        print("No data available.")
        return

    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(item) for item in row))

    filter_col = input("\n🧮 Enter a column name to filter by (or press Enter to skip): ").strip()
    if not filter_col:
        return
    if filter_col not in columns:
        print(f"❌ Column '{filter_col}' not found.")
        return

    value = input("🔍 Enter value to match: ").strip()
    all_values = get_distinct_values(cursor, table_name, filter_col)
    matches = difflib.get_close_matches(value, all_values, n=3, cutoff=0.6)

    if matches and value not in all_values:
        print(f"\n🤖 Did you mean one of these?")
        for m in matches:
            print(f"   - {m}")
        confirm = input(f"➡️  Use '{matches[0]}' instead? [Y/n]: ").strip().lower()
        if confirm != 'n':
            value = matches[0]
        else:
            print("Aborted.")
            return

    cursor.execute(f"SELECT * FROM [{table_name}] WHERE [{filter_col}] = ?", (value,))
    filtered = cursor.fetchall()

    if not filtered:
        print("\n🚫 No results found.")
    else:
        print(f"\n📊 Results matching {filter_col} = {value}:\n")
        print(" | ".join(columns))
        for row in filtered:
            print(" | ".join(str(item) for item in row))
        export_to_json(columns, filtered, table_name)

if __name__ == "__main__":
    main()
