A_DESTINATION = "https://example.com/listed-in-the-dashboard-never-in-the-schema"

ENVELOPE_REF = "#/components/schemas/ErrorResponse"


def test_the_schema_is_readable_without_a_key(anonymous_client):
    response = anonymous_client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "URL Shortener API"


def test_the_documentation_page_is_readable_without_a_key(anonymous_client):
    response = anonymous_client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_the_schema_carries_no_short_link_anyone_created(client, anonymous_client):
    created = client.post("/short-links", json={"destination": A_DESTINATION})

    schema = anonymous_client.get("/openapi.json").text

    assert created.status_code == 201
    assert A_DESTINATION not in schema
    assert created.json()["short_code"] not in schema


def test_the_schema_describes_the_error_envelope(anonymous_client):
    schema = anonymous_client.get("/openapi.json").json()

    envelope = schema["components"]["schemas"]["ErrorResponse"]
    assert set(envelope["properties"]) == {"code", "message", "fields"}
    assert envelope["required"] == ["code", "message"]

    creation = schema["paths"]["/short-links"]["post"]["responses"]
    for status_code in ("401", "422", "500", "503"):
        content = creation[status_code]["content"]["application/json"]
        assert content["schema"]["$ref"] == ENVELOPE_REF


def test_the_schema_names_no_failure_shape_the_service_never_returns(anonymous_client):
    schema = anonymous_client.get("/openapi.json").json()

    assert "HTTPValidationError" not in schema["components"]["schemas"]
    assert "ValidationError" not in schema["components"]["schemas"]
    assert "422" not in schema["paths"]["/{short_code}"]["get"]["responses"]


def test_the_schema_gives_the_listing_no_status_it_cannot_answer(anonymous_client):
    schema = anonymous_client.get("/openapi.json").json()

    listing = schema["paths"]["/short-links"]["get"]["responses"]
    assert set(listing) == {"200", "401", "500"}
    creation = schema["paths"]["/short-links"]["post"]["responses"]
    assert set(creation) == {"201", "401", "422", "500", "503"}
