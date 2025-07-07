# app.py
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    Response,
)
import csv
import io
import json

from utils.search_utils import filter_data, query_data
from utils.validation import validate_rows
from config import DEFAULT_DATABASE, READ_ONLY
from utils.db import connect_sql_server
from utils.units import mm_to_inch, inch_to_mm
from backup_db import backup_database

app = Flask(__name__)


def parse_sql_path(filename: str):
    """Return (database, table) parsed from a data filename."""
    db_part, table_part = filename.split("__", 1)
    table = table_part.rsplit('.', 1)[0]
    return db_part, table


def load_table_data(filename: str):
    """Load table rows directly from SQL."""
    db, table = parse_sql_path(filename)
    conn, cur = connect_sql_server(db)
    cur.execute(f"SELECT * FROM [{table}]")
    columns = [c[0] for c in cur.description]
    rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    conn.close()
    return rows


def save_table_data(filename: str, json_string: str) -> None:
    """Save table rows directly to the SQL table."""
    rows = json.loads(json_string)
    validate_rows(rows)
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


def insert_row(filename: str, row: dict) -> None:
    """Insert a single row into the SQL table."""
    validate_rows([row])
    db, table = parse_sql_path(filename)
    conn, cur = connect_sql_server(db)
    cols = list(row.keys())
    placeholders = ",".join("?" for _ in cols)
    col_names = ",".join(f"[{c}]" for c in cols)
    values = [row[c] for c in cols]
    cur.execute(
        f"INSERT INTO [{table}] ({col_names}) VALUES ({placeholders})",
        values,
    )
    conn.close()


def delete_row(filename: str, row_id: int) -> None:
    """Delete a row from the SQL table by ID."""
    db, table = parse_sql_path(filename)
    conn, cur = connect_sql_server(db)
    cur.execute(f"DELETE FROM [{table}] WHERE ID=?", (row_id,))
    conn.close()


@app.route('/')
def index():
    files = []
    try:
        conn, cur = connect_sql_server()
        cur.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE='BASE TABLE'"
        )
        files = [
            f"{DEFAULT_DATABASE}__{row[0]}.json" for row in cur.fetchall()
        ]
        conn.close()
    except Exception:
        files = []
    return render_template('index.html', files=files, read_only=READ_ONLY)


@app.route('/view/<filename>')
def view_table(filename):
    rows = load_table_data(filename)
    return render_template(
        'edit_table.html',
        filename=filename,
        table=rows,
        read_only=READ_ONLY,
        save_url=url_for('save_table', filename=filename) if not READ_ONLY else ''
    )


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


@app.route('/csv/<filename>')
def export_csv_route(filename):
    """Download the table as a CSV file."""
    rows = load_table_data(filename)
    if not rows:
        return Response('', mimetype='text/csv')
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename[:-5]}.csv'},
    )


@app.route('/setbolts')
def browse_setbolts():
    """Browse and filter the ASTORBASE SetBolts table."""
    raw_rows = load_table_data('ASTORBASE__SetBolts.json')

    # Build filters from query parameters
    search_term = request.args.get('q')
    filters = {}
    for field in ['Standard', 'Material', 'Name', 'Type']:
        val = request.args.get(field)
        if val:
            filters[field] = val
    for field in ['Diameter', 'Length', 'HeadHeight']:
        val = request.args.get(field)
        if val:
            try:
                filters[field] = inch_to_mm(float(val))
            except ValueError:
                pass

    rows = raw_rows
    if search_term:
        rows = query_data(rows, search_term)
    if filters:
        rows = filter_data(rows, **filters)

    # Convert numeric fields to inches for display
    display_rows = []
    for row in rows:
        r = row.copy()
        for col in ['Diameter', 'Length', 'HeadHeight']:
            if r.get(col) is not None:
                r[col] = mm_to_inch(r[col])
        display_rows.append(r)

    return render_template('setbolts.html', rows=display_rows, read_only=READ_ONLY)


@app.route('/setbolts/edit')
def edit_setbolts():
    rows = load_table_data('ASTORBASE__SetBolts.json')
    for row in rows:
        for col in ['Diameter', 'Length', 'HeadHeight']:
            if row.get(col) is not None:
                row[col] = mm_to_inch(row[col])
    return render_template(
        'edit_table.html',
        filename='ASTORBASE__SetBolts.json',
        table=rows,
        read_only=READ_ONLY,
        save_url=url_for('save_setbolts') if not READ_ONLY else ''
    )


if not READ_ONLY:
    @app.route('/setbolts/save', methods=['POST'])
    def save_setbolts():
        updated = json.loads(request.form.get('json_data', '[]'))
        for row in updated:
            for col in ['Diameter', 'Length', 'HeadHeight']:
                if row.get(col) is not None:
                    row[col] = inch_to_mm(float(row[col]))
        save_table_data('ASTORBASE__SetBolts.json', json.dumps(updated))
        return redirect(url_for('edit_setbolts'))


if not READ_ONLY:
    @app.route('/save/<filename>', methods=['POST'])
    def save_table(filename):
        updated_data = request.form.get('json_data')
        save_table_data(filename, updated_data)
        return redirect(url_for('view_table', filename=filename))

    @app.route('/add_row/<filename>', methods=['POST'])
    def add_row_route(filename):
        """Add a single row to the given table."""
        row_json = request.form.get('row')
        if not row_json:
            return jsonify({'error': 'row missing'}), 400
        row = json.loads(row_json)
        insert_row(filename, row)
        return jsonify({'status': 'ok'})

    @app.route('/delete_row/<filename>/<int:row_id>', methods=['POST'])
    def delete_row_route(filename, row_id):
        """Delete a row by ID from the given table."""
        delete_row(filename, row_id)
        return jsonify({'status': 'ok'})

    @app.route('/backup')
    def backup():
        """Trigger a database backup and return the backup path."""
        path = backup_database()
        return jsonify({"backup": str(path)})


@app.route('/sql')
def list_sql_tables():
    """List available tables in the default database."""
    tables = []
    error = None
    try:
        conn, cur = connect_sql_server()
        cur.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE='BASE TABLE'"
        )
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
    query = (
        request.form.get('query')
        if request.method == 'POST'
        else f"SELECT TOP 100 * FROM [{table_name}]"
    )
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
    return render_template(
        'sql_query.html',
        table_name=table_name,
        query=query,
        results=results,
        error=error,

    )


if __name__ == '__main__':
    app.run(debug=True)
