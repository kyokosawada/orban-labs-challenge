def create_note(client, **payload):
    response = client.post("/notes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_a_note_survives_a_create_and_is_read_back_in_the_listing(client):
    created = create_note(client, title="Buy milk", body="Semi-skimmed")

    listed = client.get("/notes").json()

    assert listed == [created]
    assert created["title"] == "Buy milk"
    assert created["body"] == "Semi-skimmed"
    assert created["id"] > 0


def test_a_note_can_be_written_with_a_title_alone(client):
    created = create_note(client, title="Ring the dentist")

    assert created["body"] == ""
    assert client.get("/notes").json() == [created]


def test_a_title_is_stored_without_its_surrounding_spaces(client):
    created = create_note(client, title="   Padded   ")

    assert created["title"] == "Padded"


def test_a_note_carries_the_times_it_was_created_and_last_changed(client):
    created = create_note(client, title="Timestamped")

    assert created["created_at"] == created["updated_at"]
    assert created["created_at"].startswith("20")


def test_notes_are_listed_most_recently_changed_first(client):
    first = create_note(client, title="Oldest")
    second = create_note(client, title="Middle")
    third = create_note(client, title="Newest")

    listed = client.get("/notes").json()

    assert [note["id"] for note in listed] == [
        third["id"],
        second["id"],
        first["id"],
    ]


def test_the_listing_is_empty_before_anything_is_written(client):
    assert client.get("/notes").json() == []


def test_notes_survive_a_restart_because_schema_creation_is_idempotent(
    client, build_client
):
    created = create_note(client, title="Written before the restart")

    with build_client() as restarted:
        assert restarted.get("/notes").json() == [created]
