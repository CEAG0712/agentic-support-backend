# tests/test_tickets_flow.py
from datetime import datetime

def test_create_ticket_returns_id_and_sets_status_queued(client):
    payload = {"subject": "Reset link expired", "description": "Cannot log in"}
    res = client.post("/tickets", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert set(data.keys()) == {"ticket_id", "job_id", "status"}
    assert data["status"] == "queued"
    assert isinstance(data["ticket_id"], str)
    assert isinstance(data["job_id"], str)

def test_get_ticket_round_trip(client):
    # 1) Create
    create = client.post("/tickets", json={"subject":"Payment failed","description":"card declined"})
    tid = create.json()["ticket_id"]

    # 2) Read
    read = client.get(f"/tickets/{tid}")
    assert read.status_code == 200
    doc = read.json()

    # Shape: TicketOut + 'id'
    expected_keys = {"subject","description","created_at","status","classification","updated_at","job_id","id"}
    assert expected_keys.issubset(set(doc.keys()))
    assert doc["id"] == tid
    assert doc["status"] in {"new","queued"}  # our fake doesn’t run a worker
    assert doc["classification"] in (None, "general", "billing", "auth", "account")

def test_reclassify_endpoint_enqueues_and_updates_status(client):
    # create a ticket
    tid = client.post("/tickets", json={"subject":"profile","description":"change email"}).json()["ticket_id"]
    # re-enqueue classification
    res = client.post(f"/tickets/{tid}/classify")
    assert res.status_code == 200
    data = res.json()
    assert data["ticket_id"] == tid
    assert data["status"] == "queued"
    assert isinstance(data["job_id"], str)
