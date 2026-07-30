import re

SHORT_CODE_PATTERN = re.compile(r"^[0-9A-Za-z]+$")

A_DESTINATION = "https://example.com/a/genuinely/long/path?utm_source=newsletter"


def shorten(client, destination=A_DESTINATION):
    response = client.post("/short-links", json={"destination": destination})
    assert response.status_code == 201, response.text
    return response.json()


def test_a_destination_is_traded_for_a_short_link(client):
    created = shorten(client)

    assert created["destination"] == A_DESTINATION
    assert SHORT_CODE_PATTERN.match(created["short_code"])
    assert created["created_at"].startswith("20")


def test_a_short_code_is_short_enough_to_be_worth_having(client):
    created = shorten(client)

    assert len(created["short_code"]) <= 10


def test_short_codes_are_random_rather_than_counted(client):
    codes = [shorten(client)["short_code"] for _ in range(20)]

    assert len(set(codes)) == len(codes)
    assert len({len(code) for code in codes}) == 1
    assert codes != sorted(codes)


def test_the_same_destination_twice_mints_two_short_codes(client):
    first = shorten(client)
    second = shorten(client)

    assert first["short_code"] != second["short_code"]
    assert first["destination"] == second["destination"]


def test_a_destination_must_be_present_and_says_which_field_was_wrong(client):
    response = client.post("/short-links", json={})

    assert response.status_code == 422
    failure = response.json()
    assert failure["code"] == "validation_error"
    assert [field["field"] for field in failure["fields"]] == ["destination"]


def test_an_empty_destination_is_refused(client):
    response = client.post("/short-links", json={"destination": "   "})

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


def test_an_unexpected_field_is_refused_rather_than_quietly_dropped(client):
    response = client.post(
        "/short-links", json={"destination": A_DESTINATION, "clicks": 99}
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
