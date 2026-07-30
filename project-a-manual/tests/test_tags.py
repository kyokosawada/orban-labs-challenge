from backend.config import get_settings
from backend.db import connect


def create_note(client, **payload):
    response = client.post("/notes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def in_storage(statement, parameters):
    connection = connect(get_settings().database_path)
    try:
        with connection:
            return connection.execute(statement, parameters).fetchall()
    finally:
        connection.close()


def delete_note(client, note):
    response = client.delete(f"/notes/{note['id']}")
    assert response.status_code == 204, response.text


def take_tag_off_every_note(name):
    in_storage(
        "DELETE FROM note_tags WHERE tag_id IN (SELECT id FROM tags WHERE name = ?)",
        (name,),
    )


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


def titles_tagged(client, tag):
    response = client.get("/notes", params={"tag": tag})
    assert response.status_code == 200, response.text
    return [note["title"] for note in response.json()]


def test_the_listing_narrows_to_the_notes_carrying_one_tag(client):
    create_note(client, title="Invoice", tags=["work", "finance"])
    create_note(client, title="Standup", tags=["work"])
    create_note(client, title="Recipe", tags=["cooking"])
    create_note(client, title="Unfiled")

    assert titles_tagged(client, "work") == ["Standup", "Invoice"]
    assert titles_tagged(client, "cooking") == ["Recipe"]


def test_the_filter_is_read_in_its_normalised_form_like_the_tag_itself(client):
    create_note(client, title="Invoice", tags=["Work"])

    assert titles_tagged(client, "WORK") == ["Invoice"]
    assert titles_tagged(client, "  work  ") == ["Invoice"]


def test_the_filter_matches_a_whole_tag_rather_than_part_of_one(client):
    create_note(client, title="Homework", tags=["homework"])
    create_note(client, title="In progress", tags=["work-in-progress"])
    create_note(client, title="Invoice", tags=["work"])

    assert titles_tagged(client, "work") == ["Invoice"]


def test_a_tag_no_note_carries_finds_nothing_rather_than_everything(client):
    create_note(client, title="Invoice", tags=["work"])

    assert titles_tagged(client, "gardening") == []


def test_an_empty_filter_returns_everything_rather_than_nothing(client):
    create_note(client, title="Invoice", tags=["work"])
    create_note(client, title="Unfiled")

    assert titles_tagged(client, "") == ["Unfiled", "Invoice"]
    assert titles_tagged(client, "   ") == ["Unfiled", "Invoice"]


def tags_in_use(client):
    response = client.get("/tags")
    assert response.status_code == 200, response.text
    return response.json()


def test_the_tags_offered_are_the_ones_notes_actually_carry(client):
    create_note(client, title="Invoice", tags=["work", "finance"])
    create_note(client, title="Recipe", tags=["cooking"])
    create_note(client, title="Unfiled")

    assert tags_in_use(client) == ["cooking", "finance", "work"]


def test_nothing_is_offered_before_anything_is_tagged(client):
    create_note(client, title="Unfiled")

    assert tags_in_use(client) == []


def test_a_tag_two_notes_share_is_offered_once(client):
    create_note(client, title="Invoice", tags=["Work"])
    create_note(client, title="Standup", tags=["work"])

    assert tags_in_use(client) == ["work"]


def test_a_tag_nothing_carries_is_kept_in_storage_but_never_offered(client):
    create_note(client, title="Invoice", tags=["work", "finance"])

    take_tag_off_every_note("work")

    assert tags_in_use(client) == ["finance"]
    assert in_storage("SELECT name FROM tags WHERE name = ?", ("work",))


def test_a_tag_whose_only_notes_are_deleted_stops_being_offered(client):
    invoice = create_note(client, title="Invoice", tags=["work"])
    create_note(client, title="Recipe", tags=["cooking"])

    delete_note(client, invoice)

    assert tags_in_use(client) == ["cooking"]


def test_a_tag_a_live_note_still_carries_goes_on_being_offered(client):
    invoice = create_note(client, title="Invoice", tags=["work"])
    create_note(client, title="Standup", tags=["work"])

    delete_note(client, invoice)

    assert tags_in_use(client) == ["work"]


def test_a_deleted_note_is_not_found_by_its_tag(client):
    invoice = create_note(client, title="Invoice", tags=["work"])
    create_note(client, title="Standup", tags=["work"])

    delete_note(client, invoice)

    assert titles_tagged(client, "work") == ["Standup"]


def test_a_refused_note_leaves_no_tag_behind_to_be_offered(client):
    client.post("/notes", json={"title": "", "tags": ["work"]})

    assert tags_in_use(client) == []


def test_a_filter_that_could_not_be_a_tag_is_refused_naming_the_field(client):
    response = client.get("/notes", params={"tag": "not a tag!"})

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert [field["field"] for field in error["fields"]] == ["tag"]
