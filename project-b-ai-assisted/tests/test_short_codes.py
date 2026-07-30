from tests.test_short_links import A_DESTINATION, shorten

A_COLLIDING_CODE = "Ab12345"


def test_a_colliding_short_code_is_regenerated(client, scripted_short_codes):
    scripted_short_codes(client, [A_COLLIDING_CODE, A_COLLIDING_CODE, "Zz98765"])

    first = shorten(client)
    second = shorten(client)

    assert first["short_code"] == A_COLLIDING_CODE
    assert second["short_code"] == "Zz98765"


def test_a_regenerated_short_link_still_resolves_to_its_own_destination(
    client, scripted_short_codes
):
    scripted_short_codes(client, [A_COLLIDING_CODE, A_COLLIDING_CODE, "Zz98765"])

    shorten(client, destination=A_DESTINATION)
    second = shorten(client, destination="https://example.org/somewhere-else")

    assert second["destination"] == "https://example.org/somewhere-else"


def test_short_codes_that_never_stop_colliding_are_reported_not_retried_forever(
    client, scripted_short_codes
):
    scripted_short_codes(client, [A_COLLIDING_CODE] * 50)
    shorten(client)

    response = client.post("/short-links", json={"destination": A_DESTINATION})

    assert response.status_code == 503
    assert response.json()["code"] == "short_code_unavailable"
