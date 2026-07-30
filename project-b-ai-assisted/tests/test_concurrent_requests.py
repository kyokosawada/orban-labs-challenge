from concurrent.futures import ThreadPoolExecutor

from tests.test_short_links import A_DESTINATION, shorten

PARALLEL_FOLLOWS = 12


def test_the_service_answers_visitors_arriving_at_the_same_time(client):
    created = shorten(client)
    follows = [f"/{created['short_code']}"] * PARALLEL_FOLLOWS

    with ThreadPoolExecutor(max_workers=len(follows)) as pool:
        responses = list(pool.map(client.get, follows))

    assert [response.status_code for response in responses] == [302] * len(follows)
    assert {response.headers["location"] for response in responses} == {A_DESTINATION}
