# AT&T Field Tools (Python)

![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green)

A real-world inspired field technician job tracking system built with Python.

This project simulates telecom field operations workflows including:

- Job creation
- Local JSON persistence
- Analytics & statistics
- REST API layer
- Automated test coverage

Designed to demonstrate practical backend engineering skills including data modeling, testing, and API design.

---

## 🚀 Features

### Core Job Tracking
- Create job records
- Store jobs in `jobs.json`
- Track technician name
- Track signal quality
- Compute job duration

### 📊 Analytics
- Total jobs
- Total minutes worked
- Average minutes per job
- Bad signal counts
- Jobs per technician
- Jobs per address

### 🌐 REST API (FastAPI)
- Health check endpoint
- Create job endpoint
- List jobs endpoint
- Compute stats endpoint
- Auto-generated Swagger documentation

### ✅ Automated Testing
- Pytest test suite
- Validates job creation
- Validates statistics computation
- Validates empty cases

---

## 📂 Project Structure

```
att_field_tools/
│
├── att_tools.py # Core business logic
├── att_tools_gui.py # Tkinter GUI version
├── api.py # FastAPI REST API
├── jobs.json # Local job storage
├── requirements.txt # Project dependencies
├── README.md
│
└── tests/
    ├── conftest.py
    └── test_att_tools.py
```

---

## 🛠 Installation

From the project root:

```bash
pip install -r requirements.txt
```

Press Enter

---

## ▶️ Run CLI / Core Logic

```bash
python att_tools.py
```

Press Enter

---

## 🌐 Run the API

Start the FastAPI server:

```bash
uvicorn api:app --reload
```

Press Enter

Then open your browser:

```
http://127.0.0.1:8000/docs
```

---

## 🧪 Testing

Run the full test suite:

```bash
pytest -q
```

Press Enter

If successful, you should see:

```
3 passed in 0.52s
```

---

## 📊 Example Job Creation Response

```json
{
  "saved": true,
  "job": {
    "id": "123",
    "address": "567 D St",
    "issue": "Low Light",
    "resolution": "Replaced bulb",
    "signal": "Good",
    "tech_name": "Jose"
  }
}
```

---

## 🧠 Technical Stack

- Python
- FastAPI
- Pydantic
- Pytest
- Uvicorn
- JSON persistence
- Tkinter GUI

---

## 🎯 Purpose

This project demonstrates:

- Clean backend architecture
- Separation of concerns
- Data modeling
- Automated testing
- API design
- Real-world workflow simulation

Inspired by telecom field technician operations.

---

## 👨‍💻 Author

Jose Sandoval  
Field Technician → Backend Engineer  
Focused on automation, QA engineering, and backend development.