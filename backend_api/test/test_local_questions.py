import pytest
from fastapi.testclient import TestClient
from backend_api.main import app
from backend_api.web.local_questions import router
from unittest.mock import patch


client = TestClient(app)


def test_get_server_data_javascript():
    response = client.get(
        "/local_questions/get_server_data/BendingStressInSimplySupportedBeam/javascript"
    )
    assert response.status_code == 200


def test_get_server_data_python():
    response = client.get(
        "/local_questions/get_server_data/BendingStressInSimplySupportedBeam/python"
    )
    assert response.status_code == 200


def test_get_server_data_invalid_type():
    response = client.get("/local_questions/get_server_data/questions/javascript")
    assert response.status_code == 400
