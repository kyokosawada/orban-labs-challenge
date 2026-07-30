from concurrent.futures import ThreadPoolExecutor

from tests.test_clicks import clicks_on
from tests.test_short_links import A_DESTINATION, shorten

PARALLEL_FOLLOWS = 12


def test_visitors_arriving_at_the_same_time_are_all_served_and_all_counted(client):
    created = shorten(client)
    follows = [f"/{created['short_code']}"] * PARALLEL_FOLLOWS

    with ThreadPoolExecutor(max_workers=len(follows)) as pool:
        responses = list(pool.map(client.get, follows))

    assert [response.status_code for response in responses] == [302] * len(follows)
    assert {response.headers["location"] for response in responses} == {A_DESTINATION}
    assert clicks_on(client, created["short_code"]) == len(follows)
