# 🔩 AdvSteel FastenSuite

**AdvSteel FastenSuite** is a modern web-based toolkit for browsing, editing, and managing fastener data—bolts, anchors, and beyond—for **Advance Steel 2025**. Built with Flask and Bootstrap, it lets you escape the chaos of Management Tools and dive straight into your `.json` exports or SQL data with clarity and control.

---

## 🛠️ Features

- View Advance Steel bolt and anchor tables in a clean browser UI
- Supports all major fastener tables:
  - `BoltDefinition`
  - `BoltsDiameters`
  - `BoltsCoating`
  - `BoltsDistances`
  - `AnchorsDefinition`
  - `AnchorsClass`, `AnchorsStandard`, and more
- Simple inline editing of table values (coming soon)
- JSON-based workflow (SQL integration optional)
- Built with Flask + Bootstrap 5 — lightweight and shareable

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/advsteel-fastensuite.git
cd advsteel-fastensuite
2. Set up the virtual environment
bash
Copy
Edit
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
3. Run the app
bash
Copy
Edit
python app.py
The app will launch at http://127.0.0.1:5000

📂 JSON File Structure
Place all your exported .json files in the /data folder.

Example:

bash
Copy
Edit
/data
├── ASTORBASE__BoltDefinition.json
├── ASTORBASE__BoltsDiameters.json
├── ASTORBASE__AnchorsDefinition.json
└── ...
📋 Roadmap
✅ Tabbed UI for bolts and anchors

⏳ Inline editing + table validation

⏳ SQL direct mode (read/write)

⏳ Add row / delete row support

⏳ User roles & access protection

⏳ Portable deployment (LAN, Docker, etc.)

🧠 Why?
Advance Steel makes modifying bolts and anchors a pain. This app changes that.

👷‍♂️ Built By
Mark Hubrich
Steel wizard. Creator of magic. Purveyor of bolts.
“I got tired of Management Tools. So I built my own.”

🧲 License
MIT — Use it, fork it, make it better. Just don’t weld it closed.
