# 🔩 AdvSteel FastenSuite

**AdvSteel FastenSuite** is a lightweight Flask application for browsing and editing Advance Steel fastener data. It provides a clean web interface that works directly with your SQL data without the pain of Management Tools.

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
- Direct SQL workflow without requiring JSON exports
- Built with Flask and Bootstrap 5
- Simple HTTP endpoint for filtering and querying table rows
- Command line script for running direct SQL queries
- Optional SQL browser with simple query interface
- Development read-only mode to prevent accidental changes
- Edit tables directly in SQL
- SetBolts browser with inch/mm unit conversion
- Advanced filtering with comparison operators (e.g. `__gt`, `__lte`) and partial matching

---

## 🚀 Getting Started

### Prerequisites
- [Python](https://www.python.org/) 3.10 or newer with `pip` available in your `PATH`.
  Verify your installation with `python --version` and `pip --version`.
  The Windows installer includes `pip`. On Linux or macOS install Python via your package manager.

1. **Clone the repository**
   ```bash
    git clone https://github.com/meistro57/AdvSteel-FastenSuite.git
    cd AdvSteel-FastenSuite
   ```
2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   # Install development dependencies to run the test suite
   pip install -r requirements-dev.txt
   ```
3. **Choose your Advance Steel version**
   Edit `config.py` and set `ADVANCE_STEEL_VERSION` to one of `2026`, `2025`, `2024`, or `2023`.
   You can also enable or disable `READ_ONLY` mode in this file. When enabled the
   web interface will prevent saving changes.

4. **Run the app**
   ```bash
   python app.py
   ```
   Open <http://127.0.0.1:5000> in your browser.
   On Windows you can run `deploy.bat` to automatically pull the latest
   changes, activate the virtual environment, and start the app.

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

### Utility Scripts
Several helper scripts are included in the repository. These were used while
exploring the Advance Steel databases and are handy for maintenance tasks:

- `sql_query.py` – execute arbitrary SQL statements from the command line and
  view the results as a table or JSON.
- `sql_dump.py` – dump entire Advance Steel databases to JSON files for quick
  inspection.
- `interactive_sql_cli.py` – browse attached `.MDF` files, preview tables and
  export filtered rows interactively.
- `check_db_connection.py` – verify that the settings in `config.py` can reach
  your local SQL Server instance.

### Running Tests
After installing the development dependencies you can run the
entire test suite with `pytest`:

```bash
pytest
```

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
