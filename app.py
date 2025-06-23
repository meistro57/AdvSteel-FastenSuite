# app.py
from flask import Flask, render_template, request, redirect, url_for
import os
from utils.json_handler import load_json, save_json

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

@app.route('/save/<filename>', methods=['POST'])
def save_table(filename):
    updated_data = request.form.get('json_data')
    path = os.path.join(DATA_DIR, filename)
    save_json(path, updated_data)
    return redirect(url_for('view_table', filename=filename))

if __name__ == '__main__':
    app.run(debug=True)
