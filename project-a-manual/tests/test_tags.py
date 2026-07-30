def create_note(client, **payload):
    response = client.post("/notes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_a_note_is_written_carrying_several_tags(client):
    created = create_note(client, title="Invoice", tags=["work", "finance"])

    assert created["tags"] == ["finance", "work"]
    assert client.get("/notes").json() == [created]


def test_a_note_written_with_no_tags_carries_none(client):
    assert create_note(client, title="Unfiled")["tags"] == []


def test_differently_capitalised_spellings_are_one_tag(client):
    created = create_note(client, title="Invoice", tags=["Work", "work", "WORK"])

    assert created["tags"] == ["work"]


def test_stray_spaces_around_a_tag_do_not_make_a_second_tag(client):
    created = create_note(client, title="Invoice", tags=["  work  ", "work"])

    assert created["tags"] == ["work"]


def test_duplicate_tags_in_one_request_collapse_rather_than_failing(client):
    created = create_note(
        client, title="Invoice", tags=["work", "work", "finance", "work"]
    )

    assert created["tags"] == ["finance", "work"]
