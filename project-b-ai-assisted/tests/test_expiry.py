from datetime import datetime, timedelta, timezone

from tests.test_redirect import AN_UNKNOWN_SHORT_CODE
from tests.test_short_links import A_DESTINATION, shorten

AN_HOUR = timedelta(hours=1)


def moment(offset: timedelta) -> datetime:
    return datetime.now(timezone.utc) + offset


def shorten_until(client, expiry):
    return client.post(
        "/short-links",
        json={"destination": A_DESTINATION, "expires_at": expiry},
    )


def test_a_short_link_can_be_created_with_an_expiry(client):
    expiry = moment(AN_HOUR)

    response = shorten_until(client, expiry.isoformat())

    assert response.status_code == 201, response.text
    created = response.json()
    assert datetime.fromisoformat(created["expires_at"]) == expiry


def test_a_short_link_is_created_without_an_expiry_by_default(client):
    created = shorten(client)

    assert created["expires_at"] is None


def test_an_expiry_already_past_is_refused_naming_the_field(client):
    response = shorten_until(client, moment(-AN_HOUR).isoformat())

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


def test_a_short_link_resolves_right_up_to_its_expiry(client, scripted_clock):
    expiry = moment(AN_HOUR)
    created = shorten_until(client, expiry.isoformat()).json()

    scripted_clock(client, expiry - timedelta(seconds=1))
    response = client.get(f"/{created['short_code']}")

    assert response.status_code == 302
    assert response.headers["location"] == A_DESTINATION


def test_a_short_link_stops_resolving_at_its_expiry_moment(client, scripted_clock):
    expiry = moment(AN_HOUR)
    created = shorten_until(client, expiry.isoformat()).json()

    scripted_clock(client, expiry)

    assert client.get(f"/{created['short_code']}").status_code == 404


def test_a_short_link_past_its_expiry_no_longer_resolves(client, scripted_clock):
    expiry = moment(AN_HOUR)
    created = shorten_until(client, expiry.isoformat()).json()

    scripted_clock(client, expiry + AN_HOUR)
    response = client.get(f"/{created['short_code']}")

    assert response.status_code == 404
    assert "location" not in response.headers


def test_a_short_link_without_an_expiry_still_resolves_years_later(
    client, scripted_clock
):
    created = shorten(client)

    scripted_clock(client, moment(timedelta(days=3650)))
    response = client.get(f"/{created['short_code']}")

    assert response.status_code == 302
    assert response.headers["location"] == A_DESTINATION


def test_an_expired_short_code_answers_exactly_as_one_never_created(
    client, scripted_clock
):
    expiry = moment(AN_HOUR)
    created = shorten_until(client, expiry.isoformat()).json()
    scripted_clock(client, expiry + AN_HOUR)

    expired = client.get(f"/{created['short_code']}")
    never_created = client.get(f"/{AN_UNKNOWN_SHORT_CODE}")

    assert expired.status_code == never_created.status_code
    assert expired.text == never_created.text
    assert set(expired.headers) == set(never_created.headers)
    assert expired.headers["content-type"] == never_created.headers["content-type"]


def test_only_the_expired_short_link_stops_resolving(client, scripted_clock):
    expiry = moment(AN_HOUR)
    expiring = shorten_until(client, expiry.isoformat()).json()
    permanent = shorten(client)

    scripted_clock(client, expiry + AN_HOUR)

    assert client.get(f"/{expiring['short_code']}").status_code == 404
    assert client.get(f"/{permanent['short_code']}").status_code == 302


def test_a_refused_expiry_mints_no_short_link(client, scripted_short_codes):
    scripted_short_codes(client, ["Zz98765"])

    shorten_until(client, moment(-AN_HOUR).isoformat())

    assert client.get("/Zz98765").status_code == 404
