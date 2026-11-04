# CleanGhat — Godavari Pushkaralu 2027 Prototype
**Problem Statement PS-07: Waste Collection and Environmental Cleanliness**

A lightweight, production-modeled prototype for municipal cleanliness monitoring, QR-based citizen reporting, supervisor custom location verification, nearest-available team dispatch, worker task execution with photographic proof, and operations analytics.

---

## Portals Overview

1. **📱 Citizen Mobile Portal (`/?page=report` or QR Scan)**:
   - Mobile-first, single-column design with zero sidebar distraction.
   - Trilingual support: English, తెలుగు (Telugu), and हिन्दी (Hindi).
   - QR prefilled location selection with full editability and an *"Other / Not Listed (Custom Location)"* option.
   - Unlisted custom locations are assigned `VERIFICATION_REQUIRED` and sent to the supervisor queue (never auto-dispatched).
   - Privacy-safe ticket tracking (requires only ticket ID; citizen contact numbers are never exposed publicly).
   - Strictly focused on PS-07 waste issues (dustbins, litter, accumulations, riverbanks, dirty public areas).

2. **🧹 Sanitation Worker Portal (`/?page=worker`)**:
   - Team account selection (`Team Alpha` through `Team Echo`) and individual worker profile selection (`K. Ramesh`, `P. Venkatesh`, etc.).
   - Enforced single active task rule per team.
   - 3-step workflow: **Accept Task** ➔ **Start Cleaning** ➔ **Complete Task**.
   - **Mandatory Before & After Photographs** required before task completion can be submitted.
   - Completed tasks archive with side-by-side evidence comparison and worker attribution.

3. **📊 Command & Admin Portal (`/?page=admin`)**:
   - **Supervisor Verification Queue**: Review custom location complaints, map to operational zones, and either auto-dispatch or manually assign available teams.
   - **All Complaints Log**: Full searchable audit log of every report showing where (location & zone), when (timestamps), and who (assigned team and worker).
   - **Cleanliness Hotspots**: Automated detection of recurring waste accumulation clusters.
   - **Fleet & Worker Performance**: Simulated team GPS status and worker resolution leaderboard.
   - **Location QR Code Centre**: Directly integrated within the Admin Portal to generate, preview, and download QR code PNGs for all 10 registered master ghats and roads.

4. **⚙️ Prototype Settings & Simulation Disclaimers (`/?page=settings`)**:
   - Outlines innovation challenge scope and simulation assumptions.
   - Safe reset functionality to clear test complaints without deleting master locations, teams, or worker accounts.

---

## How to Run Locally

### 1. Open Terminal & Activate Environment
In Windows PowerShell (from project root):

```powershell
cd cleanghat
..\.venv\Scripts\Activate.ps1
```

*(Or if using the global python environment, run `pip install -r requirements.txt`)*

### 2. Launch the Streamlit Application
```powershell
streamlit run app.py
```

### 3. Open in Browser
- **Citizen Portal**: [http://localhost:8501/?page=report](http://localhost:8501/?page=report)
- **Simulated QR Scan (Kotilingala Ghat)**: [http://localhost:8501/?page=report&location=GHAT-B-001](http://localhost:8501/?page=report&location=GHAT-B-001)
- **Worker Portal**: [http://localhost:8501/?page=worker](http://localhost:8501/?page=worker)
- **Admin Command Portal (with QR Codes)**: [http://localhost:8501/?page=admin](http://localhost:8501/?page=admin)

---

## Prototype Assumptions & Data Transparency
- 10 sample locations and 5 cleaning teams are seeded with simulated GPS coordinates.
- Team coordinates and availability are simulated demonstration telemetry for the Godavari Pushkaralu 2027 Challenge. They are not connected to official municipal government databases.
- Photos are stored locally in `uploads/` and database records in SQLite `cleanghat.db`.
- Database backup is preserved at `cleanghat.db.bak`.
