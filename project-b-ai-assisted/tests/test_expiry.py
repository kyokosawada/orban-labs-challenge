from datetime import datetime, timedelta, timezone

from tests.test_short_links import A_DESTINATION, shorten


def moment(offset: timedelta) -> datetime:
    return datetime.now(timezone.utc) + offset


def shorten_until(client, expiry, destination=A_DESTINATION):
    return client.post(
        "/short-links",
        json={"destination": destination, "expires_at": expiry},
    )


def test_a_short_link_can_be_created_with_an_expiry(client):
    expiry = moment(timedelta(hours=1))

    response = shorten_until(client, expiry.isoformat())

    assert response.status_code == 201, response.text
    created = response.json()
    assert datetime.fromisoformat(created["expires_at"]) == expiry


def test_a_short_link_is_created_without_an_expiry_by_default(client):
    created = shorten(client)

    assert created["expires_at"] is None


def test_an_expiry_already_past_is_refused_naming_the_field(client):
    response = shorten_until(client, moment(timedelta(hours=-1)).isoformat())

    assert response.status_code == 422
    failure = response.json()
    assert failure["code"] == "validation_error"
    assert [field["field"] for field in failure["fields"]] == ["expires_at"]


def test_an_expiry_without_a_timezone_is_refused_naming_the_field(client):
    response = shorten_until(client, "2999-01-01T00:00:00")

    assert response.status_code == 422
    failure = response.json()
    assert failure["code"] == "validation_error"
    assert [field["field"] for field in failure["fields"]] == ["expires_at"]


def test_an_expiry_that_is_not_a_moment_at_all_is_refused(client):
    response = shorten_until(client, "next tuesday")

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


def test_a_refused_expiry_mints_no_short_link(client, scripted_short_codes):
    scripted_short_codes(client, ["Zz98765"])

    shorten_until(client, moment(timedelta(hours=-1)).isoformat())

    assert client.get("/Zz98765").status_code == 404
