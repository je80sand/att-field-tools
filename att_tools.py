# att_tools.py
# AT&T Field Tools – Jobs JSON + Time Tracking + Google Sheets (2-way sync) + Stats + PDF

import json
import os
from collections import Counter
from datetime import datetime

# PDF generation
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

# ---------------- Files / time format ---------------- #

JOBS_FILE = "jobs.json"
# This matches how your timestamps look in the sheet (e.g. 2025-11-17 16:0)
TIME_FORMAT = "%Y-%m-%d %H:%M"

# ---------------- Google Sheets config --------------- #

GOOGLE_SERVICE_ACCOUNT_FILE = "service_account.json"

# 🔴 VERY IMPORTANT:
# Replace <YOUR_SHEET_ID_HERE> with the ID from your CURRENT working file
GOOGLE_SHEET_ID = "1NzwSeFUGH8ty2_L46I8dwV9wx1HI_55CYt4f4lKyytM"
GOOGLE_SHEET_NAME = "Jobs"

# Try to import gspread + google-auth
try:
    import gspread
    from google.oauth2.service_account import Credentials

    GDRIVE_ENABLED = True
except ImportError:
    gspread = None
    Credentials = None
    GDRIVE_ENABLED = False


# ------------- Core job storage (JSON) --------------- #

def _load_jobs_from_file():
    """Load all jobs from the local JSON file."""
    if not os.path.exists(JOBS_FILE):
        return []

    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print("Error reading jobs.json:", e)
        return []


def _save_jobs_to_file(jobs):
    """Write the given list of jobs back to the JSON file."""
    try:
        with open(JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)
    except Exception as e:
        print("Error writing jobs.json:", e)


def create_job(job_id, address, issue, resolution, signal, tech_name=""):
    """
    Create a new job dict with timestamps and duration.
    For now, start_time = end_time = now, duration_minutes = 0.
    """
    now = datetime.now()
    start_time = now.strftime(TIME_FORMAT)
    end_time = now.strftime(TIME_FORMAT)
    duration_minutes = 0.0

    return {
        "id": str(job_id).strip(),
        "address": address.strip(),
        "issue": issue.strip(),
        "resolution": resolution.strip(),
        "signal": signal.strip(),
        "start_time": start_time,
        "end_time": end_time,
        "duration_minutes": duration_minutes,
        "duration": duration_minutes, # normalized name
        "tech_name": tech_name.strip(),
        "tech": tech_name.strip(), # normalized name
    }


def add_job(job):
    """
    Add a single job to the local JSON file and return the full list.
    """
    jobs = _load_jobs_from_file()
    jobs.append(job)
    _save_jobs_to_file(jobs)
    print(f"Saved job {job.get('id')} locally to {JOBS_FILE}")
    return jobs


# ------------- Google Sheets helpers ----------------- #

def _get_gspread_client():
    """Internal helper to build a gspread client using the service account file."""
    if not GDRIVE_ENABLED:
        print("gspread / google-auth not installed. Google Sheets disabled.")
        return None

    if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
        print(f"Service account file '{GOOGLE_SERVICE_ACCOUNT_FILE}' not found.")
        return None

    try:
        creds = Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print("Error creating Google Sheets client:", e)
        return None


# ------------- Google Sheets: write (sync up) -------- #

def append_job_to_sheet(job):
    """
    Append a single job as a row in the Google Sheet.
    Column order in the sheet:
    Tech | ID | Address | Issue | Resolution | Signal | Start Time | End Time | Duration(min)
    """
    client = _get_gspread_client()
    if client is None:
        return False

    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID)
        worksheet = sheet.worksheet(GOOGLE_SHEET_NAME)

        row = [
            job.get("tech_name", ""),
            job.get("id", ""),
            job.get("address", ""),
            job.get("issue", ""),
            job.get("resolution", ""),
            job.get("signal", ""),
            job.get("start_time", ""),
            job.get("end_time", ""),
            job.get("duration_minutes", 0.0),
        ]

        worksheet.append_row(row, value_input_option="RAW")
        print("Job synced to Google Sheets.")
        return True

    except Exception as e:
        print("Error connecting to Google Sheets:", e)
        return False


# ------------- Google Sheets: read (sync down) ------- #

def load_jobs_from_sheet():
    """
    Pull all jobs from the Google Sheet and return them as a list of
    normalized dicts with keys:

    tech, id, address, issue, resolution, signal,
    start_time, end_time, duration
    """
    client = _get_gspread_client()
    if client is None:
        return []

    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID)
        worksheet = sheet.worksheet(GOOGLE_SHEET_NAME)

        rows = worksheet.get_all_records()
        jobs = []

        for r in rows:
            # Using your header names exactly as in the sheet
            job = {
                "tech": r.get("Tech", "").strip(),
                "id": str(r.get("ID", "")).strip(),
                "address": r.get("Address", "").strip(),
                "issue": r.get("Issue", "").strip(),
                "resolution": r.get("Resolution", "").strip(),
                "signal": r.get("Signal", "").strip(),
                "start_time": r.get("Start Time", "").strip(),
                "end_time": r.get("End Time", "").strip(),
            }

            dur_raw = r.get("Duration(min)", 0) or 0
            try:
                job["duration"] = float(dur_raw)
            except ValueError:
                job["duration"] = 0.0

            jobs.append(job)

        print(f"Loaded {len(jobs)} jobs from Google Sheets.")
        return jobs

    except Exception as e:
        print("Error loading from Google Sheets:", e)
        return []


# ------------- Analytics / stats --------------------- #

def compute_stats(jobs):
    """
    Given a list of normalized job dicts (from load_jobs_from_sheet),
    compute basic stats and return them in a dict.
    """
    if not jobs:
        return {
            "total_jobs": 0,
            "total_minutes": 0.0,
            "avg_minutes": 0.0,
            "longest_job": None,
            "shortest_job": None,
            "jobs_per_tech": {},
            "jobs_per_address": {},
            "jobs_per_day": {},
            "bad_signal_count": 0,
            "bad_signal_percent": 0.0,
        }

    durations = []
    techs = []
    addresses = []
    dates = []
    issues = []
    signals = []

    for job in jobs:
        dur = float(job.get("duration", 0.0) or 0.0)
        durations.append((dur, job))

        techs.append(job.get("tech") or "Unknown")
        addresses.append(job.get("address") or "Unknown")
        issues.append(job.get("issue") or "Unknown")
        sig = (job.get("signal") or "").lower()
        signals.append(sig)

        # Use first 10 chars of start_time (YYYY-MM-DD)
        start = job.get("start_time") or ""
        date_key = start[:10] if len(start) >= 10 else "Unknown"
        dates.append(date_key)

    total_jobs = len(durations)
    total_minutes = sum(d for d, _ in durations)
    avg_minutes = total_minutes / total_jobs if total_jobs else 0.0

    longest_job = max(durations, key=lambda x: x[0])[1] if durations else None
    shortest_job = min(durations, key=lambda x: x[0])[1] if durations else None

    bad_signal_words = {"bad", "poor", "weak", "low"}
    bad_signal_count = sum(
        1 for s in signals if any(word in s for word in bad_signal_words)
    )
    bad_signal_percent = (
        (bad_signal_count / total_jobs) * 100.0 if total_jobs else 0.0
    )

    stats = {
        "total_jobs": total_jobs,
        "total_minutes": round(total_minutes, 2),
        "avg_minutes": round(avg_minutes, 2),
        "longest_job": longest_job,
        "shortest_job": shortest_job,
        "jobs_per_tech": dict(Counter(techs)),
        "jobs_per_address": dict(Counter(addresses)),
        "jobs_per_day": dict(Counter(dates)),
        "bad_signal_count": bad_signal_count,
        "bad_signal_percent": round(bad_signal_percent, 2),
        "most_common_issue": Counter(issues).most_common(1)[0][0]
        if issues
        else "N/A",
    }

    return stats


# ------------- PDF export ---------------------------- #

def export_job_to_pdf(job, output_path):
    """
    Export a single normalized job dict to a simple PDF report.
    Expects keys: tech, id, address, issue, resolution, signal, start_time, end_time, duration
    """
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER

    y = height - 72 # start a bit down from the top

    def line(text, inc=18):
        nonlocal y
        c.drawString(72, y, text)
        y -= inc

    c.setFont("Helvetica-Bold", 16)
    line("AT&T Field Tools – Job Report", 24)

    c.setFont("Helvetica", 11)
    line(f"Job ID: {job.get('id', '')}")
    line(f"Tech: {job.get('tech', '')}")
    line(f"Address: {job.get('address', '')}")
    line(f"Issue: {job.get('issue', '')}")
    line(f"Resolution: {job.get('resolution', '')}")
    line(f"Signal: {job.get('signal', '')}")
    line(f"Start Time: {job.get('start_time', '')}")
    line(f"End Time: {job.get('end_time', '')}")
    line(f"Duration (min): {job.get('duration', '')}")

    c.showPage()
    c.save()
    print(f"PDF report saved to {output_path}")