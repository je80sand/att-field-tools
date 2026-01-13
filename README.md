# AT&T Field Tools – Google Sheets Job Tracker

A desktop Python tool I built to help field technicians log and analyze jobs.
It uses a custom GUI and the Google Sheets API (service accounts) to sync job
data (ID, address, issue, resolution, signal, timestamps, duration, etc.)
directly into a live spreadsheet.

---

## 🚀 Features

- Job entry GUI for field jobs
- One-click sync to Google Sheets using a service account
- Structured job data: ID, address, issue, resolution, signal, start/end time,
  and duration in minutes
- Uses a dedicated `Jobs` worksheet in a Google Sheet for clean storage
- Designed around real AT&T technician workflow

---

## 🧱 Tech Stack

- **Language:** Python 3
- **GUI:** tkinter
- **Storage:** Google Sheets (via service account)
- **Libraries:**
  - `gspread`
  - `google-auth`
  - `oauth2client`
  - `python-dateutil`

---

## 🧠 How It Works (High Level)

1. The GUI collects job details from the tech.
2. When the user clicks **Sync**, the app:
   - validates the inputs
   - calculates job duration
   - authenticates using a Google service account JSON key
   - appends a new row into the `Jobs` worksheet of a Google Sheet.
3. The sheet acts as a simple reporting database for field jobs.

---

## 🛠️ Running the App Locally

> Note: `service_account.json` is **not** committed to this repo for security.
> You must create your own service account if you want to run it.

1. Install dependencies:

   ```bash
   pip install -r requirements.txt