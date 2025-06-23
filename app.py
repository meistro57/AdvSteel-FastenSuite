# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import safe_join
import json
import pyodbc
from utils.json_handler import load_json, save_json
from utils.search_utils import filter_data, query_data
from config import DB_CONFIG, DEFAULT_DATABASE, READ_ONLY, SQL_DIRECT_MODE

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def sanitize_filename(filename: str) -> str:
    """Return the filename if safe, otherwise raise ValueError."""
    sanitized = os.path.basename(filename)
    if sanitized != filename or os.path.sep in sanitized or (
        os.path.altsep and os.path.altsep in sanitized
    ):
        raise ValueError("Invalid filename")
    return sanitized


def connect_sql_server(database: str = DEFAULT_DATABASE):
    """Return a connection object to the configured SQL Server."""
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


def parse_sql_path(filename: str):
    """Return (database, table) parsed from a data filename."""
    db_part, table_part = filename.split("__", 1)
    table = table_part.rsplit('.', 1)[0]
    return db_part, table


def load_table_data(filename: str):
    """Load table rows from JSON or SQL depending on configuration."""
    filename = sanitize_filename(filename)
    if SQL_DIRECT_MODE:
        db, table = parse_sql_path(filename)
        conn, cur = connect_sql_server(db)
        cur.execute(f"SELECT * FROM [{table}]")
        columns = [c[0] for c in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]
        conn.close()
        return rows
    else:
        path = safe_join(DATA_DIR, filename)
        return load_json(path)["data"]


def save_table_data(filename: str, json_string: str) -> None:
    """Save table rows to JSON file or SQL table."""
    filename = sanitize_filename(filename)
    rows = json.loads(json_string)
    if SQL_DIRECT_MODE:
        db, table = parse_sql_path(filename)
        conn, cur = connect_sql_server(db)
        cur.execute(f"DELETE FROM [{table}]")
        for row in rows:
            cols = list(row.keys())
            placeholders = ",".join("?" for _ in cols)
            col_names = ",".join(f"[{c}]" for c in cols)
            values = [row[c] for c in cols]
            cur.execute(
                f"INSERT INTO [{table}] ({col_names}) VALUES ({placeholders})",
                values,
            )
        conn.close()
    else:
        path = safe_join(DATA_DIR, filename)
        existing = load_json(path)
        if isinstance(existing, dict) and "data" in existing:
            existing["data"] = rows
            save_json(path, json.dumps(existing))
        else:
            save_json(path, json_string)

@app.route('/')
def index():
    if SQL_DIRECT_MODE:
        files = []
        try:
            conn, cur = connect_sql_server()
            cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            files = [f"{DEFAULT_DATABASE}__{row[0]}.json" for row in cur.fetchall()]
            conn.close()
        except Exception:
            files = []
    else:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    return render_template('index.html', files=files, read_only=READ_ONLY)

@app.route('/view/<filename>')
def view_table(filename):
    rows = load_table_data(filename)
    return render_template('edit_table.html', filename=filename, table=rows, read_only=READ_ONLY)


@app.route('/search/<filename>')
def search_table(filename):
    """Return filtered or searched data for the given table."""
    table_data = load_table_data(filename)

    # Extract search term and filter parameters from the query string
    search_term = request.args.get('q')
    filters = {k: v for k, v in request.args.items() if k != 'q'}

    if search_term:
        table_data = query_data(table_data, search_term)
    if filters:
        table_data = filter_data(table_data, **filters)

    return jsonify(table_data)

if not READ_ONLY:
    @app.route('/save/<filename>', methods=['POST'])
    def save_table(filename):
        updated_data = request.form.get('json_data')
        save_table_data(filename, updated_data)
        return redirect(url_for('view_table', filename=filename))


@app.route('/sql')
def list_sql_tables():
    """List available tables in the default database."""
    tables = []
    error = None
    try:
        conn, cur = connect_sql_server()
        cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()
    except Exception as e:
        error = str(e)
    return render_template('sql_tables.html', tables=tables, error=error)


@app.route('/sql/<table_name>', methods=['GET', 'POST'])
def query_sql_table(table_name):
    """Simple interface to run a SELECT query against a table."""
    results = None
    error = None
    query = request.form.get('query') if request.method == 'POST' else f"SELECT TOP 100 * FROM [{table_name}]"
    if request.method == 'POST':
        try:
            conn, cur = connect_sql_server()
            cur.execute(query)
            if cur.description:
                columns = [c[0] for c in cur.description]
                rows = [dict(zip(columns, r)) for r in cur.fetchall()]
                results = rows
            else:
                results = []
            conn.close()
        except Exception as e:
            error = str(e)
    return render_template('sql_query.html', table_name=table_name, query=query, results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True)
