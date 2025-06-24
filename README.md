# 🔩 AdvSteel FastenSuite

**AdvSteel FastenSuite** is a lightweight Flask application for browsing and editing Advance Steel fastener data. It provides a clean web interface for working with your exported `.json` files (or SQL data) without the pain of Management Tools.

---

## 🛠️ Features

- View Advance Steel bolt and anchor tables in the browser
- Supports major fastener tables:
  - `BoltDefinition`
  - `BoltsDiameters`
  - `BoltsCoating`
  - `BoltsDistances`
  - `AnchorsDefinition`
  - `AnchorsClass`, `AnchorsStandard`, and more
- JSON-based workflow with optional SQL integration
- Built with Flask and Bootstrap 5
- Simple HTTP endpoint for filtering and querying table rows
- Command line script for running direct SQL queries
- Optional SQL browser with simple query interface
- Development read-only mode to prevent accidental changes
- SQL direct mode for editing tables without JSON exports

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/advsteel-fastensuite.git
   cd advsteel-fastensuite
   ```
2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. **Choose your Advance Steel version**
   Edit `config.py` and set `ADVANCE_STEEL_VERSION` to one of `2026`, `2025`, `2024`, or `2023`.
   You can also enable or disable `READ_ONLY` mode in this file. When enabled the
   web interface will prevent saving changes.
   Set `SQL_DIRECT_MODE = True` to read and write directly from your SQL Server databases.

4. **Run the app**
   ```bash
   python app.py
   ```
   Open <http://127.0.0.1:5000> in your browser.
   On Windows you can run `deploy.bat` to automatically pull the latest
   changes, activate the virtual environment, and start the app.

### JSON File Structure
Place your exported `.json` files in the `data/` directory:

```
/data
├── ASTORBASE__BoltDefinition.json
├── ASTORBASE__BoltsDiameters.json
├── ASTORBASE__AnchorsDefinition.json
└── ...
```

### Querying Tables
Use the `/search/<filename>` endpoint to filter or search rows:

```bash
curl "http://127.0.0.1:5000/search/ASTORBASE__BoltsDiameters.json?q=20"
curl "http://127.0.0.1:5000/search/ASTORBASE__BoltDefinition.json?Diameter=20&Name=Hex"
```

### Running Direct SQL Queries
You can query your Advance Steel databases directly using `sql_query.py`:

```bash
python sql_query.py -d ASTORBASE "SELECT TOP 5 * FROM BoltDefinition"
```
Use the `-o json` option to output results as JSON.

### Testing the SQL Server Connection
Run `check_db_connection.py` to quickly verify that your
`config.py` settings can successfully connect to SQL Server:

```bash
python check_db_connection.py
```
The script will attempt to connect using the configured driver and
server. It prints a success message if the connection works or an
error message otherwise.

### SQL Browser
Navigate to `/sql` in the running app to view available tables and run simple
queries through the web interface.

## 📋 Roadmap
- ✔️ Tabbed UI for bolts and anchors
- ⏳ Inline editing with table validation
- ✔️ SQL direct mode (read/write)
- ⏳ Add row / delete row support
- ⏳ User roles & access protection
- ⏳ Portable deployment (LAN, Docker, etc.)

## 🧠 Why?
Advance Steel makes modifying bolts and anchors a pain. This app changes that.

## 👷‍♂️ Built By
Mark Hubrich  
Steel wizard. Creator of magic. Purveyor of bolts.  
"I got tired of Management Tools. So I built my own."

## 🧲 License
MIT — Use it, fork it, make it better. Just don’t weld it closed.
