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


def test_a_filter_that_could_not_be_a_tag_is_refused_naming_the_field(client):
    response = client.get("/notes", params={"tag": "not a tag!"})

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert [field["field"] for field in error["fields"]] == ["tag"]
