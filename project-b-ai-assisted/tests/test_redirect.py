from tests.test_short_links import A_DESTINATION, shorten

AN_UNKNOWN_SHORT_CODE = "Nothing"


def test_following_a_short_code_sends_the_visitor_to_its_destination(client):
    created = shorten(client)

    response = client.get(f"/{created['short_code']}")

    assert response.status_code == 302
    assert response.headers["location"] == A_DESTINATION


def test_a_destination_is_handed_back_exactly_as_it_was_given(client):
    destination = "https://example.com/path?one=1&two=2#fragment"
    created = shorten(client, destination=destination)

    response = client.get(f"/{created['short_code']}")

    assert response.headers["location"] == destination


def test_following_a_short_link_needs_no_credential(anonymous_client, client):
    created = shorten(client)

    response = anonymous_client.get(f"/{created['short_code']}")

    assert response.status_code == 302
    assert response.headers["location"] == A_DESTINATION


def test_a_redirect_is_never_cached_so_every_follow_reaches_the_service(client):
    created = shorten(client)

    response = client.get(f"/{created['short_code']}")

    assert response.headers["cache-control"] == "no-store"


def test_an_unknown_short_code_is_refused(client):
    response = client.get(f"/{AN_UNKNOWN_SHORT_CODE}")

    assert response.status_code == 404
    assert "location" not in response.headers


def test_a_visitor_meets_an_ordinary_status_rather_than_an_error_document(client):
    response = client.get(f"/{AN_UNKNOWN_SHORT_CODE}")

    assert response.headers["content-type"].startswith("text/plain")


def test_two_short_links_to_one_destination_resolve_independently(client):
    first = shorten(client)
    second = shorten(client)

    assert client.get(f"/{first['short_code']}").headers["location"] == A_DESTINATION
    assert client.get(f"/{second['short_code']}").headers["location"] == A_DESTINATION


def test_a_short_link_survives_a_restart(client, build_client):
    created = shorten(client)

    with build_client() as restarted:
        response = restarted.get(f"/{created['short_code']}")

    assert response.status_code == 302
    assert response.headers["location"] == A_DESTINATION


def test_a_refused_creation_never_mints_a_short_link(
    anonymous_client, client, scripted_short_codes
):
    scripted_short_codes(anonymous_client, ["Zz98765"])

    anonymous_client.post("/short-links", json={"destination": A_DESTINATION})

    assert client.get("/Zz98765").status_code == 404
