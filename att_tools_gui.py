# att_tools_gui.py
# tkinter GUI for AT&T Field Tools – Job Logger & Dashboard

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import att_tools

# This will hold the last set of jobs we loaded from Google Sheets
current_jobs = []


# --------------- GUI callbacks ---------------- #

def save_and_sync():
    """Collect form data, create a job, save it locally and sync to Google Sheets."""
    job_id = entry_id.get().strip()
    address = entry_address.get().strip()
    issue = entry_issue.get().strip()
    resolution = entry_resolution.get().strip()
    signal = entry_signal.get().strip()
    tech_name = entry_tech.get().strip()

    if not job_id or not address or not issue:
        messagebox.showerror("Missing Data", "Job ID, Address, and Issue are required.")
        return

    # Create job dict
    job = att_tools.create_job(job_id, address, issue, resolution, signal, tech_name)

    # Save locally
    att_tools.add_job(job)

    # Sync to Google Sheets
    success = att_tools.append_job_to_sheet(job)
    if success:
        messagebox.showinfo("Success", "Job saved and synced to Google Sheets.")
    else:
        messagebox.showwarning(
            "Partial Success",
            "Job saved locally, but Google Sheets sync failed.\n"
            "Check terminal output for details.",
        )

    # Clear fields for next job (keep tech so you don't retype it every time)
    entry_id.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    entry_issue.delete(0, tk.END)
    entry_resolution.delete(0, tk.END)
    entry_signal.delete(0, tk.END)

    refresh_table()


def refresh_table():
    """Refresh the table view with jobs from Google Sheets."""
    global current_jobs

    # Clear existing rows
    for row in tree.get_children():
        tree.delete(row)

    # Load from Sheets
    current_jobs = att_tools.load_jobs_from_sheet()
    if not current_jobs:
        messagebox.showinfo("No Data", "No jobs found in Google Sheets.")
        return

    # Insert into Treeview
    for idx, job in enumerate(current_jobs):
        tree.insert(
            "",
            tk.END,
            iid=str(idx), # use index as row ID
            values=[
                job.get("id", ""),
                job.get("address", ""),
                job.get("issue", ""),
                job.get("signal", ""),
                job.get("duration", ""),
                job.get("tech", ""),
            ],
        )


def show_stats():
    """Compute and show basic stats about jobs."""
    global current_jobs

    if not current_jobs:
        current_jobs = att_tools.load_jobs_from_sheet()
        if not current_jobs:
            messagebox.showinfo("Stats", "No jobs found to analyze.")
            return

    stats = att_tools.compute_stats(current_jobs)

    longest = stats["longest_job"]
    shortest = stats["shortest_job"]

    longest_text = (
        f"{longest.get('id', '')} ({longest.get('duration', '')} min)"
        if longest
        else "N/A"
    )
    shortest_text = (
        f"{shortest.get('id', '')} ({shortest.get('duration', '')} min)"
        if shortest
        else "N/A"
    )

    msg_lines = [
        f"Total jobs: {stats['total_jobs']}",
        f"Total minutes: {stats['total_minutes']}",
        f"Average duration (min): {stats['avg_minutes']}",
        "",
        f"Longest job: {longest_text}",
        f"Shortest job: {shortest_text}",
        "",
        f"Bad signal jobs: {stats['bad_signal_count']} "
        f"({stats['bad_signal_percent']}%)",
        f"Most common issue: {stats['most_common_issue']}",
        "",
        "Jobs per tech:",
        f" {stats['jobs_per_tech']}",
        "",
        "Jobs per address:",
        f" {stats['jobs_per_address']}",
        "",
        "Jobs per day:",
        f" {stats['jobs_per_day']}",
    ]

    messagebox.showinfo("Job Stats", "\n".join(msg_lines))


def export_selected_job():
    """Export the selected job in the table to a PDF report."""
    global current_jobs

    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a job in the table.")
        return

    row_id = selected[0]
    try:
        idx = int(row_id)
    except ValueError:
        messagebox.showerror("Error", "Could not determine selected job index.")
        return

    if idx < 0 or idx >= len(current_jobs):
        messagebox.showerror("Error", "Selected job index out of range.")
        return

    job = current_jobs[idx]

    # Ask where to save
    default_name = f"job_{job.get('id', 'report')}_report.pdf"
    filepath = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=default_name,
        title="Save Job Report as PDF",
    )
    if not filepath:
        return

    att_tools.export_job_to_pdf(job, filepath)
    messagebox.showinfo("PDF Export", f"Job report saved to:\n{filepath}")


# --------------- Build the GUI ---------------- #

root = tk.Tk()
root.title("AT&T Field Tools – Job Logger & Dashboard")
root.geometry("900x500")

# Title
label_title = tk.Label(root, text="AT&T Field Job Entry", font=("Helvetica", 16, "bold"))
label_title.pack(pady=10)

# Top frame: form
frame_form = tk.Frame(root)
frame_form.pack(pady=5)

# Tech name (simple 'login' so reports have a tech)
label_tech = tk.Label(frame_form, text="Tech Name:")
label_tech.grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_tech = tk.Entry(frame_form, width=30)
entry_tech.grid(row=0, column=1, padx=5, pady=5)

# Row 1: ID
label_id = tk.Label(frame_form, text="Job ID:")
label_id.grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_id = tk.Entry(frame_form, width=30)
entry_id.grid(row=1, column=1, padx=5, pady=5)

# Row 2: Address
label_address = tk.Label(frame_form, text="Address:")
label_address.grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_address = tk.Entry(frame_form, width=30)
entry_address.grid(row=2, column=1, padx=5, pady=5)

# Row 3: Issue
label_issue = tk.Label(frame_form, text="Issue:")
label_issue.grid(row=3, column=0, sticky="e", padx=5, pady=5)
entry_issue = tk.Entry(frame_form, width=30)
entry_issue.grid(row=3, column=1, padx=5, pady=5)

# Row 4: Resolution
label_resolution = tk.Label(frame_form, text="Resolution:")
label_resolution.grid(row=4, column=0, sticky="e", padx=5, pady=5)
entry_resolution = tk.Entry(frame_form, width=30)
entry_resolution.grid(row=4, column=1, padx=5, pady=5)

# Row 5: Signal
label_signal = tk.Label(frame_form, text="Signal:")
label_signal.grid(row=5, column=0, sticky="e", padx=5, pady=5)
entry_signal = tk.Entry(frame_form, width=30)
entry_signal.grid(row=5, column=1, padx=5, pady=5)

# Middle frame: buttons
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn_save_sync = tk.Button(
    frame_buttons, text="Save Job + Sync to Google Sheets", command=save_and_sync
)
btn_save_sync.grid(row=0, column=0, padx=10, pady=5)

btn_refresh = tk.Button(
    frame_buttons, text="Refresh Job List", command=refresh_table
)
btn_refresh.grid(row=0, column=1, padx=10, pady=5)

btn_stats = tk.Button(
    frame_buttons, text="Show Stats", command=show_stats
)
btn_stats.grid(row=0, column=2, padx=10, pady=5)

btn_export = tk.Button(
    frame_buttons, text="Export Selected Job to PDF", command=export_selected_job
)
btn_export.grid(row=0, column=3, padx=10, pady=5)

# Bottom frame: table (Treeview)
frame_table = tk.Frame(root)
frame_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

columns = ("id", "address", "issue", "signal", "duration", "tech")
tree = ttk.Treeview(
    frame_table,
    columns=columns,
    show="headings",
    height=10,
)

tree.heading("id", text="Job ID")
tree.heading("address", text="Address")
tree.heading("issue", text="Issue")
tree.heading("signal", text="Signal")
tree.heading("duration", text="Duration (min)")
tree.heading("tech", text="Tech")

tree.column("id", width=80)
tree.column("address", width=200)
tree.column("issue", width=180)
tree.column("signal", width=80, anchor="center")
tree.column("duration", width=100, anchor="center")
tree.column("tech", width=120)

# Scrollbar
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Initial load
refresh_table()

root.mainloop()