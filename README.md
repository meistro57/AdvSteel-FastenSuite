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
3. **Run the app**
   ```bash
   python app.py
   ```
   Open <http://127.0.0.1:5000> in your browser.

### JSON File Structure
Place your exported `.json` files in the `data/` directory:

```
/data
├── ASTORBASE__BoltDefinition.json
├── ASTORBASE__BoltsDiameters.json
├── ASTORBASE__AnchorsDefinition.json
└── ...
```

## 📋 Roadmap
- ✔️ Tabbed UI for bolts and anchors
- ⏳ Inline editing with table validation
- ⏳ SQL direct mode (read/write)
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
