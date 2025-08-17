# tests/test_validation.py
def test_create_ticket_validation_envelope(client):
    # subject trims to empty, description too short => 422
    payload = {"subject": "  ", "description": "x"}
    res = client.post("/tickets", json=payload)
    assert res.status_code == 422
    body = res.json()
    assert "error" in body and body["error"]["type"] == "validation_error"
    # make sure details is a list of errors (fields, messages)
    assert isinstance(body["error"]["details"], list)
    # request_id should be present for correlation
    assert "request_id" in body["error"]
