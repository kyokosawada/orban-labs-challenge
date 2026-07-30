import pytest

from backend.config import API_KEY_HEADER

DOCUMENTATION_ADDRESSES = ["/openapi.json", "/docs", "/redoc"]


def published(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize("address", DOCUMENTATION_ADDRESSES)
def test_the_documentation_is_readable_without_a_key(anonymous_client, address):
    assert anonymous_client.get(address).status_code == 200


def test_the_documentation_carries_no_note_and_no_key(client, anonymous_client, api_key):
    written = client.post("/notes", json={"title": "A private note"})
    assert written.status_code == 201, written.text

    for address in DOCUMENTATION_ADDRESSES:
        served = anonymous_client.get(address).text
        assert "A private note" not in served, address
        assert api_key not in served, address


def test_the_api_describes_where_its_key_is_required_and_where_it_is_not(client):
    description = published(client)["info"]["description"]

    assert API_KEY_HEADER in description
    for address in DOCUMENTATION_ADDRESSES:
        assert address in description
