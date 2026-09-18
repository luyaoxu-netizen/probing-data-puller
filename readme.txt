Here is the complete summary of your current 3-file system along with a comprehensive **`README.md`** documentation file.

---

### Core Files Summary

1. **`emailwafertable1.gs` (Google Apps Script)**
* **Role:** Cloud Email & Table Parsing Engine.
* **What it does:** Scans Gmail daily for completed wafer probing emails from `@chipbond.com.tw`, parses strict HTML tables containing FTP file paths, deduplicates table content using MD5 hashing, generates CSV files, and saves them to Google Drive (`datatable` folder). Exposes a `doGet(e)` Web App endpoint for remote execution.


2. **`ftp_puller.py` (Python Script)**
* **Role:** Local Data Ingestion & File Downloader.
* **What it does:** Scans local Google Drive CSV files created by the script, connects to Chipbond's FTP server over TLS/SSL, parses remote directories, downloads raw wafer probing measurement files (`.csv`, `.xlsx`, `.zip`), organizes them locally into `maskID`-based subdirectories (`G:\My Drive\FTP data\<maskID>\`), and logs completed pulls.


3. **`wafer_control_panel.py` (Python GUI)**
* **Role:** Desktop Master Control Interface.
* **What it does:** Provides a graphical Tkinter dashboard with live automated status tracking and manual override controls:
* **Button 1:** Triggers the Apps Script Web App remotely via background HTTP requests.
* **Button 2:** Spawns a non-blocking background thread (`threading.Thread`) with unbuffered streaming (`python -u`) to run `ftp_puller.py` and print real-time download logs into the UI without freezing your PC.





---

### Comprehensive `README.md`

Below is the ready-to-use **`README.md`** file explaining the architecture, setup, daily automation setup, and file structure.

```markdown
# Wafer Probing Automated Data Collection System

An automated end-to-end data pipeline designed to monitor, extract, and ingest wafer probing test reports sent via email, clean metadata into Google Drive CSV records, and automatically retrieve full raw test files over FTP into structured local storage.

---

## 🏗 System Architecture & Workflow


```

[ Email: @chipbond.com.tw ]
│
▼ (Daily Apps Script Scanner)
[ Google Drive / datatable/*.csv ]
│
▼ (FTP Downloader Script)
[ Chipbond FTP Server ]
│
▼ (Automated Pull & Organization)
[ Local Drive: G:\My Drive\FTP data<maskID>\ ]

```

---

## 📁 File Manifest

| File Name | Platform | Description |
| :--- | :--- | :--- |
| `emailwafertable1.gs` | Google Apps Script (JS) | Scans Gmail, parses target probing email tables, generates hash-verified metadata CSVs, saves to Google Drive, and hosts Web App trigger. |
| `ftp_puller.py` | Python 3.x | Reads local Google Drive CSV metadata, opens secure FTP sessions, downloads probing measurement files, and categorizes by `maskID`. |
| `wafer_control_panel.py` | Python Tkinter (GUI) | Interactive control dashboard. Features real-time log streaming (`-u` unbuffered), multi-threaded execution, and Web App triggering. |

---

## ⏰ Daily Automated Execution Setup

The system is configured to run automatically once per day in two synchronized phases:

### Phase 1: Google Apps Script Time-Driven Trigger (Cloud Execution)
* **Schedule:** Daily between 11:00 AM – 12:00 PM (Noon).
* **Setup Instructions:**
  1. Open the project in [Google Apps Script Editor](https://script.google.com/).
  2. Click the **Triggers (Alarm Clock icon)** on the left menu.
  3. Click **+ Add Trigger** (bottom right).
  4. Configure settings:
     * **Choose function to run:** `extractChipbondWaferTables`
     * **Select event source:** `Time-driven`
     * **Select type of time based trigger:** `Day timer`
     * **Select time of day:** `11am to 12pm`
  5. Click **Save**.

### Phase 2: Local Windows Task Scheduler (FTP Ingestion)
* **Schedule:** Daily at 12:00 PM (Noon).
* **Setup Instructions:**
  1. Press `Win + R`, type `taskschd.msc`, and press **Enter**.
  2. Click **Create Basic Task...** on the right side.
  3. **Name:** `Wafer FTP Daily Ingestion`
  4. **Trigger:** `Daily` at `12:00:00 PM`.
  5. **Action:** `Start a program`
     * **Program/script:** `python.exe` (or full path to your `python.exe`)
     * **Add arguments:** `"G:\My Drive\claude code work\wafer_ftp_puller\ftp_puller.py"`
     * **Start in:** `G:\My Drive\claude code work\wafer_ftp_puller\`
  6. Click **Finish**.

---

## 🎮 Manual Execution (Control Panel UI)

For on-demand extractions outside scheduled hours:

1. Launch the control panel:
   ```bash
   python wafer_control_panel.py

```

2. **Click "1. Run Email Table Extractor"** — Triggers cloud parsing and generates CSVs in Google Drive.
3. **Click "2. Run Local FTP Downloader Now"** — Downloads raw files for all detected CSVs into `G:\My Drive\FTP data\<maskID>\` with live UI log updates.

---

## 🛠 Dependencies & Requirements

* **Python:** `3.8+`
* **Python Libraries:** `tkinter`, `urllib`, `ssl`, `threading`, `subprocess`, `os`, `csv`, `ftplib`
* **Google Workspace Account:** Access to Gmail and Google Drive.

```

Save this text as `README.md` inside your project directory (`G:\My Drive\claude code work\wafer_ftp_puller\`).