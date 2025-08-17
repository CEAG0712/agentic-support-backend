# tests/test_jobs_status.py
from datetime import datetime, timezone

class _FakeFetchedJob:
    def __init__(self, job_id, status, result=None, exc_info=None):
        self.id = job_id
        self._status = status
        self.result = result
        self.exc_info = exc_info
        now = datetime.now(timezone.utc)
        self.enqueued_at = now
        self.started_at = now if status in {"started","finished","failed"} else None
        self.ended_at = now if status in {"finished","failed"} else None
    def get_status(self): return self._status

def test_job_status_finished(monkeypatch, client):
    # Simulate Job.fetch() returning a finished job with a result payload
    def _fake_fetch(job_id, connection):
        return _FakeFetchedJob(job_id, "finished", result={"ok": True, "classification": "billing"})
    from rq import job as rq_job
    monkeypatch.setattr(rq_job.Job, "fetch", staticmethod(_fake_fetch))

    res = client.get("/jobs/abc123")
    assert res.status_code == 200
    body = res.json()
    assert body["job_id"] == "abc123"
    assert body["status"] == "finished"
    assert body["result"] == {"ok": True, "classification": "billing"}
    assert body["exc_info"] is None
    assert body["enqueued_at"] is not None

def test_job_status_not_found(monkeypatch, client):
    from rq.job import NoSuchJobError
    def _raise_not_found(job_id, connection):
        raise NoSuchJobError
    from rq import job as rq_job
    monkeypatch.setattr(rq_job.Job, "fetch", staticmethod(_raise_not_found))

    res = client.get("/jobs/missing")
    assert res.status_code == 404
    assert res.json() == {"detail": "Job not found"}
