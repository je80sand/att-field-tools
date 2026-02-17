# api.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

import att_tools

app = FastAPI(
    title="AT&T Field Tools API",
    version="1.0.0",
    description="API wrapper for job tracking + analytics (compute_stats) from att_tools.py",
)

class JobIn(BaseModel):
    id: str = Field(..., description="Job ID")
    address: str = Field(..., description="Customer address")
    issue: str = Field(..., description="Problem/issue")
    resolution: str = Field(..., description="Resolution notes")
    signal: str = Field(..., description="Signal quality label (e.g. Good/Bad)")
    tech_name: str = Field(..., description="Technician name")

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/jobs")
def list_jobs() -> Dict[str, Any]:
    jobs = att_tools._load_jobs_from_file()
    return {"count": len(jobs), "jobs": jobs}

@app.post("/jobs")
def create_job(job: JobIn) -> Dict[str, Any]:
    # Use your existing logic so API and CLI stay consistent
    new_job = att_tools.create_job(
        job_id=job.id,
        address=job.address,
        issue=job.issue,
        resolution=job.resolution,
        signal=job.signal,
        tech_name=job.tech_name,
    )
    att_tools.add_job(new_job)
    return {"saved": True, "job": new_job}

@app.get("/stats")
def stats() -> Dict[str, Any]:
    jobs = att_tools._load_jobs_from_file()
    return att_tools.compute_stats(jobs)