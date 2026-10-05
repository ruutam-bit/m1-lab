"""CR-1 pieņemšanas kritēriji (tracker/CR-1.md): viens tests katrai kritēriju rindai.

Sagaidāmās vērtības ņemtas no kritērijiem un precizējumiem; kļūdas forma
no līguma docs/openapi.yaml (components.responses.ValidationError).
"""


def _post_with_code(client, payload, personal_code):
    payload["personalCode"] = personal_code
    return client.post("/submissions", json=payload)


def _assert_stored(client, response, expected):
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}")
    assert saved.status_code == 200
    assert saved.json()["personalCode"] == expected


def _assert_validation_error(response, issue, entered=None):
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "personalCode", "issue": issue} in error["details"]
    # Precizējums: kļūdas atbildē ievadīto kodu neatkārto.
    if entered:
        assert entered not in response.text


def test_cr1_ac1_eleven_digits_stored(client, valid_payload):
    """AC1: `32000000001` -> 201, saglabāts `32000000001`."""
    response = _post_with_code(client, valid_payload, "32000000001")
    _assert_stored(client, response, "32000000001")


def test_cr1_ac2_hyphen_normalised(client, valid_payload):
    """AC2: `320000-00001` -> 201, saglabāts `32000000001`."""
    response = _post_with_code(client, valid_payload, "320000-00001")
    _assert_stored(client, response, "32000000001")


def test_cr1_ac3_surrounding_spaces_removed(client, valid_payload):
    """AC3: `" 32000000001 "` -> 201 (atstarpes noņemtas)."""
    response = _post_with_code(client, valid_payload, " 32000000001 ")
    _assert_stored(client, response, "32000000001")


def test_cr1_ac4_ten_digits_invalid_format(client, valid_payload):
    """AC4: `3200000000` (10 cipari) -> 400 `INVALID_FORMAT`."""
    response = _post_with_code(client, valid_payload, "3200000000")
    _assert_validation_error(response, "INVALID_FORMAT", "3200000000")


def test_cr1_ac5_twelve_digits_invalid_format(client, valid_payload):
    """AC5: `320000000012` (12 cipari) -> 400 `INVALID_FORMAT`."""
    response = _post_with_code(client, valid_payload, "320000000012")
    _assert_validation_error(response, "INVALID_FORMAT", "320000000012")


def test_cr1_ac6_letter_o_invalid_format(client, valid_payload):
    """AC6: `32000000O01` (burts O) -> 400 `INVALID_FORMAT`."""
    response = _post_with_code(client, valid_payload, "32000000O01")
    _assert_validation_error(response, "INVALID_FORMAT", "32000000O01")


def test_cr1_ac7_missing_field_required(client, valid_payload):
    """AC7: lauka nav -> 400 `REQUIRED`."""
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "REQUIRED")


def test_cr1_ac8_old_format_hyphen_normalised(client, valid_payload):
    """AC8: vecā formāta sintētisks kods `311299-21233` -> 201, saglabāts `31129921233`."""
    response = _post_with_code(client, valid_payload, "311299-21233")
    _assert_stored(client, response, "31129921233")


def test_cr1_ac9_misplaced_hyphen_invalid_format(client, valid_payload):
    """AC9: `3200-0000001` (defise nepareizā vietā) -> 400 `INVALID_FORMAT`."""
    response = _post_with_code(client, valid_payload, "3200-0000001")
    _assert_validation_error(response, "INVALID_FORMAT", "3200-0000001")
