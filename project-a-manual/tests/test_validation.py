import pytest

REJECTED_PAYLOADS = [
    pytest.param({"body": "No title at all"}, "title", id="title-missing"),
    pytest.param({"title": ""}, "title", id="title-empty"),
    pytest.param({"title": "     "}, "title", id="title-only-spaces"),
    pytest.param({"title": "x" * 201}, "title", id="title-too-long"),
    pytest.param(
        {"title": "  " + "x" * 201 + "  "}, "title", id="title-too-long-after-trimming"
    ),
    pytest.param(
        {"title": "Fine", "body": "x" * 10_001}, "body", id="body-too-long"
    ),
    pytest.param(
        {"title": "Fine", "tittle": "typo"}, "tittle", id="unrecognised-field"
    ),
    pytest.param(
        {"title": "Fine", "tags": [""]}, "tags", id="tag-empty"
    ),
    pytest.param(
        {"title": "Fine", "tags": ["   "]}, "tags", id="tag-only-spaces"
    ),
    pytest.param(
        {"title": "Fine", "tags": ["x" * 51]}, "tags", id="tag-too-long"
    ),
    pytest.param(
        {"title": "Fine", "tags": ["two words"]}, "tags", id="tag-with-a-space-inside"
    ),
    pytest.param(
        {"title": "Fine", "tags": ["work!"]}, "tags", id="tag-with-punctuation"
    ),
    pytest.param(
        {"title": "Fine", "tags": ["work", "in/tray"]}, "tags", id="tag-with-a-slash"
    ),
    pytest.param(
        {"title": "Fine", "tags": [f"tag-{index}" for index in range(21)]},
        "tags",
        id="more-than-twenty-tags",
    ),
    pytest.param(
        {"title": "Fine", "tags": "work"}, "tags", id="tags-not-a-list"
    ),
]


@pytest.mark.parametrize("payload, offending_field", REJECTED_PAYLOADS)
def test_an_invalid_submission_is_rejected_naming_the_field(
    client, payload, offending_field
):
    response = client.post("/notes", json=payload)

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert offending_field in [field["field"] for field in error["fields"]]


@pytest.mark.parametrize("payload, offending_field", REJECTED_PAYLOADS)
def test_a_rejected_submission_writes_nothing(client, payload, offending_field):
    client.post("/notes", json=payload)

    assert client.get("/notes").json() == []


def test_a_field_message_reads_as_a_sentence_to_the_person_who_sent_it(client):
    response = client.post("/notes", json={"title": "   "})

    message = response.json()["fields"][0]["message"]
    assert not message.startswith("Value error")
    assert message == "Title must not be empty once surrounding spaces are removed."


def test_a_rejected_tag_is_named_in_the_message_so_a_long_list_is_not_a_hunt(client):
    response = client.post(
        "/notes", json={"title": "Fine", "tags": ["work", "in tray", "finance"]}
    )

    message = response.json()["fields"][0]["message"]
    assert "in tray" in message


ACCEPTED_PAYLOADS = [
    pytest.param({"title": "x"}, id="title-of-one-character"),
    pytest.param({"title": "x" * 200}, id="title-at-the-limit"),
    pytest.param({"title": "  " + "x" * 200 + "  "}, id="title-at-the-limit-once-trimmed"),
    pytest.param({"title": "Fine", "body": ""}, id="body-empty"),
    pytest.param({"title": "Fine", "body": None}, id="body-null"),
    pytest.param({"title": "Fine", "body": "x" * 10_000}, id="body-at-the-limit"),
    pytest.param({"title": "Fine", "tags": []}, id="no-tags-at-all"),
    pytest.param({"title": "Fine", "tags": ["x" * 50]}, id="tag-at-the-limit"),
    pytest.param({"title": "Fine", "tags": ["a-b_c9"]}, id="tag-of-every-allowed-character"),
    pytest.param(
        {"title": "Fine", "tags": [f"tag-{index}" for index in range(20)]},
        id="twenty-tags",
    ),
    pytest.param(
        {"title": "Fine", "tags": [f"tag-{index}" for index in range(20)] + ["TAG-0"]},
        id="twenty-one-tags-collapsing-to-twenty",
    ),
]


@pytest.mark.parametrize("payload", ACCEPTED_PAYLOADS)
def test_a_submission_at_the_edge_of_the_rules_is_accepted(client, payload):
    assert client.post("/notes", json=payload).status_code == 201


def test_every_failure_shares_one_envelope(client, anonymous_client):
    failures = [
        anonymous_client.get("/notes"),
        client.post("/notes", json={"title": ""}),
        client.get("/notes/does-not-exist"),
        client.delete("/notes"),
    ]

    for response in failures:
        error = response.json()
        assert response.status_code >= 400
        assert set(error) <= {"code", "message", "fields"}
        assert isinstance(error["code"], str) and error["code"]
        assert isinstance(error["message"], str) and error["message"]
        assert "detail" not in error


def test_a_body_that_is_not_json_names_the_body_rather_than_an_offset(client):
    response = client.post(
        "/notes",
        content="{not json at all",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json()["fields"] == [
        {"field": "body", "message": "The request body is not valid JSON."}
    ]


def test_an_unhandled_failure_returns_the_same_envelope(client, api_key):
    from fastapi.testclient import TestClient

    from backend.config import API_KEY_HEADER
    from backend.db import get_connection

    def unavailable_storage():
        raise RuntimeError("storage is unavailable")

    client.app.dependency_overrides[get_connection] = unavailable_storage
    with TestClient(client.app, raise_server_exceptions=False) as tolerant:
        response = tolerant.get("/notes", headers={API_KEY_HEADER: api_key})

    assert response.status_code == 500
    assert response.json() == {
        "code": "internal_error",
        "message": "The server could not complete the request.",
    }


def test_the_published_schema_documents_the_error_envelope(client):
    schema = client.get("/openapi.json").json()

    envelope = schema["components"]["schemas"]["ErrorResponse"]
    assert set(envelope["properties"]) == {"code", "message", "fields"}

    responses = schema["paths"]["/notes"]["post"]["responses"]
    for status_code in ("401", "422", "500"):
        reference = responses[status_code]["content"]["application/json"]["schema"]
        assert reference["$ref"].endswith("/ErrorResponse")
