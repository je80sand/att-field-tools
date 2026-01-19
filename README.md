# Field Technician Tools (Python)

Inspired by real-world telecom field technician workflows.

A Python-based automation toolkit designed to support real-world  field technician workflows.

This project simulates tools commonly used by field technicians and service professionals to track jobs, validate input, store job data, and streamline daily operational tasks. It reflects practical automation scenarios drawn directly from real field experience.

---

## 🎯 Why This Project Exists

This project was built to demonstrate how Python can be used to automate everyday field-service and technician workflows.

It mirrors real-world tasks such as:
- Capturing structured job information
- Validating required inputs before submission
- Logging completed jobs for tracking and reporting
- Reducing manual paperwork and repetitive data entry

The goal is to showcase **practical, entry-level Python automation skills** that translate directly to operational and support environments.

---

## 🧰 What This Tool Does

- Accepts technician job details (customer, address, issue, status)
- Validates required fields before saving
- Stores job records in a structured JSON file
- Provides both **CLI-based** and **GUI-based** interaction
- Simulates real field-service data tracking workflows

---

## ▶️ How to Run

### 1️⃣ Install Dependencies
From the project root directory:

```bash
pip install -r requirements.txt

## 📌 Example Output

Below is an example of the tool running successfully and creating a job record:

```text
Job created successfully
Customer: John
Address: 567 D St
Issue: Low Light
Status: Saved to jobs.json
