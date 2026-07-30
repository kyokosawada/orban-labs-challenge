import pytest

from backend.config import API_KEY_HEADER

REQUESTS = [
    ("GET", "/notes", None),
    ("POST", "/notes", {"title": "Should never be written"}),
    ("GET", "/tags", None),
]


@pytest.mark.parametrize("method, path, payload", REQUESTS)
def test_a_request_without_a_key_is_refused(anonymous_client, method, path, payload):
    response = anonymous_client.request(method, path, json=payload)

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


@pytest.mark.parametrize("method, path, payload", REQUESTS)
def test_a_request_with_the_wrong_key_is_refused(anonymous_client, method, path, payload):
    response = anonymous_client.request(
        method, path, json=payload, headers={API_KEY_HEADER: "not-the-key"}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_a_refused_write_never_reaches_storage(anonymous_client, client):
    anonymous_client.post("/notes", json={"title": "Should never be written"})

    assert client.get("/notes").json() == []
