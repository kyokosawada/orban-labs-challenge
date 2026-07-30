from tests.test_short_links import shorten


def refuse(client, destination):
    response = client.post("/short-links", json={"destination": destination})

    assert response.status_code == 422, response.text
    failure = response.json()
    assert failure["code"] == "validation_error"
    return failure


def reason(client, destination):
    failure = refuse(client, destination)
    fields = failure["fields"]

    assert [field["field"] for field in fields] == ["destination"]
    return fields[0]["message"]


def test_an_http_destination_is_accepted(client):
    created = shorten(client, destination="http://example.com/page")

    assert created["destination"] == "http://example.com/page"


def test_an_https_destination_is_accepted(client):
    created = shorten(client, destination="https://example.com/page")

    assert created["destination"] == "https://example.com/page"


def test_a_javascript_destination_is_refused(client):
    assert "http" in reason(client, "javascript:alert(document.cookie)")


def test_a_data_destination_is_refused(client):
    assert "http" in reason(client, "data:text/html;base64,PHNjcmlwdD4=")


def test_a_non_web_scheme_is_refused(client):
    assert "http" in reason(client, "ftp://example.com/archive.zip")


def test_a_destination_without_a_scheme_is_refused(client):
    assert "http" in reason(client, "example.com/page")


def test_a_destination_with_no_host_is_refused(client):
    assert reason(client, "https:///page")


def test_a_malformed_destination_names_the_field_in_the_shared_error_shape(client):
    failure = refuse(client, "https://")

    assert failure["message"]
    assert failure["fields"][0]["field"] == "destination"
    assert failure["fields"][0]["message"]
