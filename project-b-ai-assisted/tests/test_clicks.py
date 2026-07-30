from concurrent.futures import ThreadPoolExecutor

from tests.test_short_links import A_DESTINATION, shorten
from tests.test_stats import list_short_links

AN_UNKNOWN_SHORT_CODE = "Nothing"
PARALLEL_FOLLOWS = 12


def clicks_on(client, short_code):
    listed = list_short_links(client)
    return next(link["clicks"] for link in listed if link["short_code"] == short_code)


def test_a_served_redirect_is_a_counted_click(client):
    created = shorten(client)

    response = client.get(f"/{created['short_code']}")

    assert response.status_code == 302
    assert response.headers["location"] == A_DESTINATION
    assert clicks_on(client, created["short_code"]) == 1


def test_the_same_person_following_twice_counts_twice(client):
    created = shorten(client)

    client.get(f"/{created['short_code']}")
    client.get(f"/{created['short_code']}")

    assert clicks_on(client, created["short_code"]) == 2


def test_a_visitor_without_the_key_still_counts(anonymous_client, client):
    created = shorten(client)

    anonymous_client.get(f"/{created['short_code']}")

    assert clicks_on(client, created["short_code"]) == 1


def test_an_unknown_short_code_counts_nothing(client):
    created = shorten(client)

    assert client.get(f"/{AN_UNKNOWN_SHORT_CODE}").status_code == 404

    listed = list_short_links(client)
    assert [link["short_code"] for link in listed] == [created["short_code"]]
    assert listed[0]["clicks"] == 0


def test_two_short_links_to_one_destination_count_independently(client):
    first = shorten(client)
    second = shorten(client)

    client.get(f"/{first['short_code']}")
    client.get(f"/{first['short_code']}")
    client.get(f"/{second['short_code']}")

    assert clicks_on(client, first["short_code"]) == 2
    assert clicks_on(client, second["short_code"]) == 1


def test_visitors_arriving_at_the_same_time_all_count(client):
    created = shorten(client)
    followers = [f"/{created['short_code']}"] * PARALLEL_FOLLOWS

    with ThreadPoolExecutor(max_workers=len(followers)) as pool:
        responses = list(pool.map(client.get, followers))

    assert [response.status_code for response in responses] == [302] * len(followers)
    assert clicks_on(client, created["short_code"]) == len(followers)


def test_a_click_survives_a_restart(client, build_client):
    created = shorten(client)
    client.get(f"/{created['short_code']}")

    with build_client() as restarted:
        assert clicks_on(restarted, created["short_code"]) == 1
