import att_tools


def test_create_job_structure():
    job = att_tools.create_job(
        job_id="123",
        address="567 D St",
        issue="Low Light",
        resolution="Replaced bulb",
        signal="Good",
        tech_name="Jose",
    )

    assert isinstance(job, dict)

    # Core fields
    assert job["id"] == "123"
    assert job["address"] == "567 D St"
    assert job["issue"] == "Low Light"
    assert job["resolution"] == "Replaced bulb"
    assert job["signal"] == "Good"

    # Your project normalizes tech name in multiple keys
    assert job["tech_name"] == "Jose"
    assert job["tech"] == "Jose"

    # Time fields
    assert "start_time" in job
    assert "end_time" in job

    # Duration fields (your code stores both)
    assert "duration_minutes" in job
    assert "duration" in job


def test_compute_stats_empty_list():
    stats = att_tools.compute_stats([])

    assert stats["total_jobs"] == 0
    assert stats["total_minutes"] == 0.0
    assert stats["avg_minutes"] == 0.0
    assert stats["bad_signal_count"] == 0


def test_compute_stats_counts_and_minutes():
    # IMPORTANT:
    # Your compute_stats likely sums "duration" (not "duration_minutes"),
    # so we provide BOTH keys to match your real job objects.
    jobs = [
        {"duration": 10.0, "duration_minutes": 10.0, "tech": "Jose", "address": "A", "signal": "Good"},
        {"duration": 20.0, "duration_minutes": 20.0, "tech": "Jose", "address": "A", "signal": "Bad"},
        {"duration": 30.0, "duration_minutes": 30.0, "tech": "Ana", "address": "B", "signal": "Bad"},
    ]

    stats = att_tools.compute_stats(jobs)

    assert stats["total_jobs"] == 3
    assert stats["total_minutes"] == 60.0
    assert stats["avg_minutes"] == 20.0
    assert stats["bad_signal_count"] == 2

    # Breakdowns
    assert stats["jobs_per_tech"]["Jose"] == 2
    assert stats["jobs_per_tech"]["Ana"] == 1
    assert stats["jobs_per_address"]["A"] == 2
    assert stats["jobs_per_address"]["B"] == 1