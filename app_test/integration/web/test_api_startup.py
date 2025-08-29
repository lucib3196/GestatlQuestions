def test_startup_connection(test_client):
    response = test_client.get("/startup")
    assert response.status_code == 200
    assert response.json() == {"message": "The API is LIVE!!"}