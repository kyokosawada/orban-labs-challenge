from backend.config import API_KEY_HEADER

A_DESTINATION = "https://example.com/should-never-be-minted"


def test_creating_a_short_link_without_a_key_is_refused(anonymous_client):
    response = anonymous_client.post(
        "/short-links", json={"destination": A_DESTINATION}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_creating_a_short_link_with_the_wrong_key_is_refused(anonymous_client):
    response = anonymous_client.post(
        "/short-links",
        json={"destination": A_DESTINATION},
        headers={API_KEY_HEADER: "not-the-key"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"
