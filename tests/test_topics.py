"""CR-0: tēma PARKS un tēmu saraksts GET /topics."""

import pytest

EXPECTED_TOPICS = [
    {"code": "ROADS", "name": "Ceļi un ielas"},
    {"code": "WASTE", "name": "Atkritumi"},
    {"code": "PLANNING", "name": "Teritorijas plānošana"},
    {"code": "PARKS", "name": "Parki un skvēri"},
    {"code": "OTHER", "name": "Cits"},
]


def test_list_topics_returns_all_in_order(client):
    # Kritērijs 1 un 4: pilns saraksts, secība, kodi un nosaukumi.
    response = client.get("/topics")
    assert response.status_code == 200
    assert response.json() == EXPECTED_TOPICS


def test_submission_with_parks_topic_returns_201(client, valid_payload):
    # Kritērijs 2
    valid_payload["topic"] = "PARKS"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}").json()
    assert saved["topic"] == "PARKS"


def test_unknown_topic_returns_validation_error(client, valid_payload):
    # Kritērijs 3
    valid_payload["topic"] = "ZOO"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "topic", "issue": "INVALID_FORMAT"} in error["details"]


@pytest.mark.parametrize("topic", ["ROADS", "WASTE", "PLANNING", "OTHER"])
def test_existing_topics_still_accepted(client, valid_payload, topic):
    # Kritērijs 4
    valid_payload["topic"] = topic
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
