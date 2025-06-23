# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from utils.json_handler import load_json, save_json
from utils.search_utils import filter_data, query_data

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@app.route('/')
def index():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    return render_template('index.html', files=files)

@app.route('/view/<filename>')
def view_table(filename):
    path = os.path.join(DATA_DIR, filename)
    table_data = load_json(path)
    return render_template('edit_table.html', filename=filename, table=table_data["data"])


@app.route('/search/<filename>')
def search_table(filename):
    """Return filtered or searched data for the given table."""
    path = os.path.join(DATA_DIR, filename)
    table_data = load_json(path)["data"]

    # Extract search term and filter parameters from the query string
    search_term = request.args.get('q')
    filters = {k: v for k, v in request.args.items() if k != 'q'}

    if search_term:
        table_data = query_data(table_data, search_term)
    if filters:
        table_data = filter_data(table_data, **filters)

    return jsonify(table_data)

@app.route('/save/<filename>', methods=['POST'])
def save_table(filename):
    updated_data = request.form.get('json_data')
    path = os.path.join(DATA_DIR, filename)
    save_json(path, updated_data)
    return redirect(url_for('view_table', filename=filename))

if __name__ == '__main__':
    app.run(debug=True)
