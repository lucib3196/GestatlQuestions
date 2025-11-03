import pytest
import json
from src.api.models.models import Question


@pytest.fixture
def qpayload_bad():
    return {"Data": "Some Content"}


@pytest.fixture
def question_payload():
    """Minimal question payload with required fields only."""
    return {
        "title": "SomeTitle",
        "ai_generated": True,
        "isAdaptive": True,
    }


@pytest.fixture
def question_payload_thermo():
    """Thermodynamics question payload with metadata."""
    return {
        "title": "Thermodynamics First Law",
        "ai_generated": False,
        "isAdaptive": False,
        "topics": ["Thermodynamics", "Energy Balance"],
        "languages": ["python", "javascript"],
        "qtype": ["conceptual"],
    }


@pytest.fixture
def question_payload_fluids():
    """Fluid dynamics question payload with metadata."""
    return {
        "title": "Bernoulli Equation",
        "ai_generated": True,
        "isAdaptive": True,
        "topics": ["Fluid Dynamics", "Flow Analysis"],
        "languages": ["javascript"],
        "qtype": ["multiple-choice"],
    }


@pytest.fixture
def create_question_web(test_client, question_payload):
    """POST a minimal valid question payload to /questions/."""
    return test_client.post("/questions/", json=question_payload)


@pytest.fixture
def create_question_bad_payload_response(test_client, qpayload_bad):
    """POST an invalid question payload to /questions/."""
    return test_client.post("/questions/", json=qpayload_bad)


@pytest.fixture
def multi_payload_questions(
    question_payload, question_payload_thermo, question_payload_fluids
):
    return [question_payload, question_payload_fluids, question_payload_thermo]
