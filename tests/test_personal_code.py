"""CR-1: personas koda pārbaude iesniegumā (tracker/CR-1.md)."""

import pytest


@pytest.mark.parametrize(
    ("personal_code", "stored"),
    [
        ("32000000001", "32000000001"),  # 1
        ("320000-00001", "32000000001"),  # 2
        (" 32000000001 ", "32000000001"),  # 3
        ("010190-00000", "01019000000"),  # 8
    ],
)
def test_valid_personal_code_is_stored_normalized(
    client, fake_omd, valid_payload, personal_code, stored
):
    valid_payload["personalCode"] = personal_code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}").json()
    assert saved["personalCode"] == stored
    assert fake_omd.calls == [stored]


@pytest.mark.parametrize(
    "personal_code",
    [
        "3200000000",  # 4: 10 cipari
        "320000000011",  # 5: 12 cipari
        "3200000000O",  # 6: burts O
        "3200-0000001",  # 9: defise nepareizā vietā
        "320000--00001",  # 11
        "32000000001-",  # 11
        "320000 00001",  # 12: atstarpe vidū
    ],
)
def test_invalid_personal_code_returns_400_invalid_format(
    client, fake_omd, valid_payload, personal_code
):
    valid_payload["personalCode"] = personal_code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"] == [{"field": "personalCode", "issue": "INVALID_FORMAT"}]
    assert personal_code not in response.text
    assert fake_omd.calls == []


@pytest.mark.parametrize("personal_code", [None, "", "   "])  # 7, 10
def test_missing_or_blank_personal_code_returns_400_required(
    client, fake_omd, valid_payload, personal_code
):
    if personal_code is None:
        del valid_payload["personalCode"]
    else:
        valid_payload["personalCode"] = personal_code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"] == [{"field": "personalCode", "issue": "REQUIRED"}]
    assert fake_omd.calls == []


def test_ui_checks_personal_code_before_sending(client):
    # 13: pati pārbaude notiek pārlūkā; šeit tikai, ka forma satur to pašu noteikumu.
    response = client.get("/ui/")
    assert "/^[0-9]{6}-?[0-9]{5}$/" in response.text
