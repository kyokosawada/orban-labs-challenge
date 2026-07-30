from tests.test_short_links import A_DESTINATION, shorten


def list_short_links(client):
    response = client.get("/short-links")
    assert response.status_code == 200, response.text
    return response.json()


def test_nothing_created_yet_is_an_empty_list_rather_than_a_failure(client):
    assert list_short_links(client) == []


def test_a_short_link_is_reported_with_what_the_dashboard_shows(client):
    created = shorten(client)

    listed = list_short_links(client)

    assert len(listed) == 1
    assert listed[0]["short_code"] == created["short_code"]
    assert listed[0]["destination"] == A_DESTINATION
    assert listed[0]["created_at"] == created["created_at"]
    assert listed[0]["clicks"] == 0


def test_every_short_link_created_is_reported(client):
    codes = {shorten(client)["short_code"] for _ in range(3)}

    assert {link["short_code"] for link in list_short_links(client)} == codes


def test_the_newest_short_link_is_reported_first(client):
    first = shorten(client)
    second = shorten(client)

    listed = list_short_links(client)

    assert [link["short_code"] for link in listed] == [
        second["short_code"],
        first["short_code"],
    ]


def test_a_new_short_link_has_taken_no_clicks(client):
    assert shorten(client)["clicks"] == 0


def test_short_links_survive_a_restart_with_their_counts(client, build_client):
    created = shorten(client)

    with build_client() as restarted:
        listed = list_short_links(restarted)

    assert [link["short_code"] for link in listed] == [created["short_code"]]
    assert listed[0]["clicks"] == 0
