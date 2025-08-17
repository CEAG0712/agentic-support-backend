# tests/test_health.py
def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"message": "Agentic Support Backend up and running"}

def test_health_db_ok(client):
    # ping_db is monkeypatched to True in the client fixture
    res = client.get("/health/db")
    assert res.status_code == 200
    assert res.json() == {"mongo_ok": True}

def test_health_queue_ok(client):
    # FakeQueue.connection.ping() returns True
    res = client.get("/health/queue")
    assert res.status_code == 200
    assert res.json() == {"redis_ok": True}
