from concurrent.futures import ThreadPoolExecutor

PARALLEL_READS = ["/notes", "/tags"] * 8


def test_the_service_answers_callers_arriving_at_the_same_time(client):
    client.post("/notes", json={"title": "Invoice", "tags": ["work"]})

    with ThreadPoolExecutor(max_workers=len(PARALLEL_READS)) as pool:
        responses = list(pool.map(client.get, PARALLEL_READS))

    assert [response.status_code for response in responses] == [200] * len(
        PARALLEL_READS
    )
