import socket

from tests.test_short_links import shorten

A_PUBLIC_ADDRESS = "https://93.184.216.34/pricing"

PRIVATE_DESTINATIONS = [
    "http://10.0.0.5/admin",
    "http://172.16.4.9/admin",
    "http://192.168.1.1/admin",
]


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


def test_a_loopback_destination_is_refused(client):
    assert "loopback" in reason(client, "http://127.0.0.1:8000/admin")


def test_an_ipv6_loopback_destination_is_refused(client):
    assert "loopback" in reason(client, "http://[::1]:8000/admin")


def test_an_ipv4_mapped_loopback_destination_is_refused(client):
    assert "loopback" in reason(client, "http://[::ffff:127.0.0.1]/admin")


def test_the_loopback_name_is_refused_without_looking_it_up(client):
    assert "loopback" in reason(client, "http://localhost:8000/admin")


def test_a_link_local_destination_is_refused(client):
    assert "link-local" in reason(client, "http://169.254.169.254/latest/meta-data/")


def test_a_private_network_destination_is_refused(client):
    for destination in PRIVATE_DESTINATIONS:
        assert "private" in reason(client, destination), destination


def test_the_unspecified_address_is_refused(client):
    assert reason(client, "http://0.0.0.0:8000/admin")


def test_credentials_cannot_disguise_a_private_destination(client):
    assert "private" in reason(client, "https://example.com@10.0.0.5/admin")


def test_a_loopback_address_written_as_one_number_is_refused(client):
    assert reason(client, "https://2130706433/admin")


def test_a_loopback_address_written_in_octal_is_refused(client):
    assert reason(client, "https://0177.0.0.1/admin")


def test_a_public_address_literal_is_accepted(client):
    created = shorten(client, destination=A_PUBLIC_ADDRESS)

    assert created["destination"] == A_PUBLIC_ADDRESS


def test_the_refusal_says_which_rule_was_broken_rather_than_that_it_failed(client):
    scheme_refusal = reason(client, "javascript:alert(1)")
    address_refusal = reason(client, "http://127.0.0.1/admin")

    assert scheme_refusal != address_refusal


def test_a_refused_destination_mints_no_short_link(client, scripted_short_codes):
    scripted_short_codes(client, ["Zz54321"])

    refuse(client, "http://127.0.0.1/admin")

    assert client.get("/Zz54321").status_code == 404


def test_creating_a_short_link_asks_the_network_nothing(client, monkeypatch):
    def refuse_to_leave_the_process(*args, **kwargs):
        raise AssertionError("creating a Short Link made a network request")

    monkeypatch.setattr(socket, "getaddrinfo", refuse_to_leave_the_process)
    monkeypatch.setattr(socket.socket, "connect", refuse_to_leave_the_process)

    created = shorten(client, destination="https://example.invalid/nothing-is-here")

    assert created["destination"] == "https://example.invalid/nothing-is-here"
