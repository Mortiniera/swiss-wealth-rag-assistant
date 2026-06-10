def test_ask_rejects_empty_question(client):
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ingest_missing_folder_returns_404(client):
    response = client.post("/ingest", json={"source_dir": "data/does_not_exist"})
    assert response.status_code == 404