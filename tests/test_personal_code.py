"""CR-1: personas koda pārbaude iesniegumā (tracker/CR-1.md)."""

import logging

import pytest


@pytest.mark.parametrize(
    ("personal_code", "stored"),
    [
        ("32000000001", "32000000001"),  # 1
        ("320000-00001", "32000000001"),  # 2
        (" 32000000001 ", "32000000001"),  # 3
        ("311299-21233", "31129921233"),  # 8: vecā formāta sintētisks kods
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
        "320000000012",  # 5: 12 cipari
        "32000000O01",  # 6: burts O
        "3200-0000001",  # 9: defise nepareizā vietā
        # Papildu pārbaudes (precizējums: formāts DDMMYY-NNNNN vai 11 cipari)
        "320000--00001",
        "32000000001-",
        "320000 00001",  # atstarpe vidū
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


# 7; papildu pārbaude (precizējums): tukša virkne vai tikai atstarpes → REQUIRED
@pytest.mark.parametrize("personal_code", [None, "", "   "])
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


@pytest.mark.parametrize(
    ("personal_code", "status"),
    [("320000-00001", 201), ("32000000O01", 400)],
)
def test_personal_code_is_not_logged(
    client, valid_payload, caplog, personal_code, status
):
    # Precizējums: kodu neatkārto ne atbildē, ne žurnālā.
    valid_payload["personalCode"] = personal_code
    with caplog.at_level(logging.DEBUG):
        response = client.post("/submissions", json=valid_payload)
    assert response.status_code == status
    assert personal_code not in caplog.text
    assert personal_code.replace("-", "") not in caplog.text


def test_ui_checks_personal_code_before_sending(client):
    # Papildu UI pārbaude: pati pārbaude notiek pārlūkā; šeit tikai, ka forma
    # satur to pašu noteikumu. Galīgo lēmumu pieņem serveris.
    response = client.get("/ui/")
    assert "/^[0-9]{6}-?[0-9]{5}$/" in response.text
