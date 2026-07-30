import pytest
from fastapi.routing import APIRoute

from backend.config import API_KEY_HEADER

DOCUMENTATION_ADDRESSES = ["/openapi.json", "/docs", "/redoc"]


def published(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200, response.text
    return response.json()


def operations(schema):
    for path, methods in schema["paths"].items():
        for method, operation in methods.items():
            yield f"{method.upper()} {path}", operation


def test_every_endpoint_the_app_serves_appears_in_the_schema(client):
    served = {
        f"{method} {route.path}"
        for route in client.app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    }

    assert served == {name for name, _ in operations(published(client))}


def test_every_endpoint_documents_the_statuses_it_answers_with(client):
    documented = {
        name: set(operation["responses"])
        for name, operation in operations(published(client))
    }

    assert documented == {
        "POST /notes": {"201", "401", "422", "500"},
        "GET /notes": {"200", "401", "422", "500"},
        "GET /notes/{note_id}": {"200", "401", "404", "422", "500"},
        "PUT /notes/{note_id}": {"200", "401", "404", "422", "500"},
        "DELETE /notes/{note_id}": {"204", "401", "404", "422", "500"},
        "GET /tags": {"200", "401", "500"},
    }


def test_every_documented_failure_carries_the_shared_error_envelope(client):
    for name, operation in operations(published(client)):
        failures = {
            status_code: response
            for status_code, response in operation["responses"].items()
            if int(status_code) >= 400
        }
        for status_code, response in failures.items():
            reference = response["content"]["application/json"]["schema"]["$ref"]
            assert reference.endswith("/ErrorResponse"), f"{name} {status_code}"


def test_the_listing_documents_the_filters_that_narrow_it(client):
    parameters = published(client)["paths"]["/notes"]["get"]["parameters"]

    assert {entry["name"]: entry["in"] for entry in parameters} == {
        "q": "query",
        "tag": "query",
    }
    assert all(entry["description"] for entry in parameters)
    assert not any(entry["required"] for entry in parameters)


def test_every_endpoint_addressing_one_note_documents_its_identifier(client):
    addressed = published(client)["paths"]["/notes/{note_id}"]

    for method, operation in addressed.items():
        described = {entry["name"]: entry for entry in operation["parameters"]}
        assert described["note_id"]["in"] == "path", method
        assert described["note_id"]["required"] is True, method
        assert described["note_id"]["description"], method


def test_the_documented_note_is_the_one_the_api_answers_with(client):
    written = client.post(
        "/notes",
        json={"title": "Buy milk", "body": "Semi-skimmed", "tags": ["shopping"]},
    )
    assert written.status_code == 201, written.text

    documented = published(client)["components"]["schemas"]["Note"]
    assert set(written.json()) == set(documented["properties"])
    assert set(documented["required"]) == set(documented["properties"])


def test_the_documented_submission_is_the_one_the_api_accepts(client):
    documented = published(client)["components"]["schemas"]["NoteContent"]

    assert set(documented["properties"]) == {"title", "body", "tags"}
    assert documented["required"] == ["title"]
    assert documented["additionalProperties"] is False


def test_the_submission_the_schema_shows_is_one_the_api_accepts(client):
    shown = published(client)["components"]["schemas"]["NoteContent"]["example"]

    written = client.post("/notes", json=shown)

    assert written.status_code == 201, written.text
    assert {field: written.json()[field] for field in shown} == {
        **shown,
        "tags": sorted(shown["tags"]),
    }


def test_the_note_the_schema_shows_is_shaped_like_the_one_the_api_answers_with(client):
    schema = published(client)
    shown = schema["components"]["schemas"]["Note"]["example"]

    written = client.post("/notes", json={"title": "Buy milk"})

    assert written.status_code == 201, written.text
    assert set(shown) == set(written.json())
    assert set(shown) == set(schema["components"]["schemas"]["Note"]["properties"])


def test_deleting_documents_that_it_answers_with_nothing_to_read(client):
    addressed = published(client)["paths"]["/notes/{note_id}"]

    assert "content" not in addressed["delete"]["responses"]["204"]


def test_every_endpoint_that_reaches_a_note_names_the_key_it_requires(client):
    schema = published(client)

    assert schema["components"]["securitySchemes"]["APIKeyHeader"] == {
        "type": "apiKey",
        "in": "header",
        "name": API_KEY_HEADER,
    }
    for name, operation in operations(schema):
        assert operation["security"] == [{"APIKeyHeader": []}], name


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
