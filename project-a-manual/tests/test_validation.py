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


ACCEPTED_PAYLOADS = [
    pytest.param({"title": "x"}, id="title-of-one-character"),
    pytest.param({"title": "x" * 200}, id="title-at-the-limit"),
    pytest.param({"title": "  " + "x" * 200 + "  "}, id="title-at-the-limit-once-trimmed"),
    pytest.param({"title": "Fine", "body": ""}, id="body-empty"),
    pytest.param({"title": "Fine", "body": None}, id="body-null"),
    pytest.param({"title": "Fine", "body": "x" * 10_000}, id="body-at-the-limit"),
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


def test_the_published_schema_documents_the_error_envelope(client):
    schema = client.get("/openapi.json").json()

    envelope = schema["components"]["schemas"]["ErrorResponse"]
    assert set(envelope["properties"]) == {"code", "message", "fields"}

    responses = schema["paths"]["/notes"]["post"]["responses"]
    for status_code in ("401", "422", "500"):
        reference = responses[status_code]["content"]["application/json"]["schema"]
        assert reference["$ref"].endswith("/ErrorResponse")
