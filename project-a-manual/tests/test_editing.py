from datetime import datetime

import pytest

from backend.config import get_settings
from backend.db import connect


def create_note(client, **payload):
    response = client.post("/notes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def edit_note(client, note_id, **payload):
    response = client.put(f"/notes/{note_id}", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def listed(client, **params):
    response = client.get("/notes", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def tags_in_use(client):
    response = client.get("/tags")
    assert response.status_code == 200, response.text
    return response.json()


def moment(value):
    return datetime.fromisoformat(value)


def delete_note(note):
    connection = connect(get_settings().database_path)
    try:
        with connection:
            connection.execute(
                "UPDATE notes SET deleted_at = ? WHERE id = ?",
                ("2026-02-03T09:00:00+00:00", note["id"]),
            )
    finally:
        connection.close()


def test_a_notes_title_and_body_are_changed(client):
    written = create_note(client, title="Buy milk", body="Semi-skimmed")

    edited = edit_note(client, written["id"], title="Buy oat milk", body="Barista")

    assert edited["title"] == "Buy oat milk"
    assert edited["body"] == "Barista"


def test_the_listing_shows_the_change_rather_than_what_was_written(client):
    written = create_note(client, title="Buy milk", body="Semi-skimmed")

    edited = edit_note(client, written["id"], title="Buy oat milk", body="Barista")

    assert listed(client) == [edited]


def test_an_edit_changes_a_note_rather_than_writing_a_second_one(client):
    written = create_note(client, title="Buy milk")

    edited = edit_note(client, written["id"], title="Buy oat milk")

    assert edited["id"] == written["id"]
    assert edited["created_at"] == written["created_at"]
    assert len(listed(client)) == 1


def test_a_note_records_when_it_was_last_changed(client):
    written = create_note(client, title="Buy milk")

    edited = edit_note(client, written["id"], title="Buy oat milk")

    assert moment(edited["updated_at"]) > moment(written["updated_at"])


def test_the_time_a_note_was_last_changed_is_not_accepted_from_the_caller(client):
    written = create_note(client, title="Buy milk")

    response = client.put(
        f"/notes/{written['id']}",
        json={"title": "Buy oat milk", "updated_at": "1999-01-01T00:00:00+00:00"},
    )

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert "updated_at" in [field["field"] for field in error["fields"]]
    assert listed(client) == [written]


def test_an_edited_note_rises_to_the_top_of_the_listing(client):
    oldest = create_note(client, title="Oldest")
    create_note(client, title="Middle")
    create_note(client, title="Newest")

    edit_note(client, oldest["id"], title="Oldest, revisited")

    assert [note["title"] for note in listed(client)] == [
        "Oldest, revisited",
        "Newest",
        "Middle",
    ]


def test_a_notes_tags_are_replaced_wholesale(client):
    written = create_note(client, title="Invoice", tags=["work", "finance"])

    edited = edit_note(client, written["id"], title="Invoice", tags=["home"])

    assert edited["tags"] == ["home"]
    assert listed(client, tag="home") == [edited]
    assert listed(client, tag="work") == []


def test_a_notes_tags_can_be_replaced_with_none(client):
    written = create_note(client, title="Invoice", tags=["work"])

    edited = edit_note(client, written["id"], title="Invoice", tags=[])

    assert edited["tags"] == []
    assert listed(client, tag="work") == []


def test_an_edit_that_names_no_tags_leaves_the_note_carrying_none(client):
    written = create_note(client, title="Invoice", tags=["work"])

    assert edit_note(client, written["id"], title="Invoice")["tags"] == []


def test_an_edit_that_names_no_body_leaves_the_note_without_one(client):
    written = create_note(client, title="Invoice", body="Due Friday")

    assert edit_note(client, written["id"], title="Invoice")["body"] == ""


def test_a_body_can_be_emptied_by_an_edit(client):
    written = create_note(client, title="Invoice", body="Due Friday")

    edited = edit_note(client, written["id"], title="Invoice", body="")

    assert edited["body"] == ""
    assert listed(client) == [edited]


def test_replacing_tags_does_not_disturb_the_same_tags_on_other_notes(client):
    invoice = create_note(client, title="Invoice", tags=["work", "finance"])
    standup = create_note(client, title="Standup", tags=["work"])

    edit_note(client, invoice["id"], title="Invoice", tags=["home"])

    assert listed(client, tag="work") == [standup]
    assert tags_in_use(client) == ["home", "work"]


def test_a_tag_the_edit_left_attached_to_nothing_stops_being_offered(client):
    invoice = create_note(client, title="Invoice", tags=["work", "finance"])
    create_note(client, title="Recipe", tags=["cooking"])

    edit_note(client, invoice["id"], title="Invoice", tags=["finance"])

    assert tags_in_use(client) == ["cooking", "finance"]


def test_a_tag_an_edit_brought_back_is_offered_again(client):
    invoice = create_note(client, title="Invoice", tags=["work"])

    edit_note(client, invoice["id"], title="Invoice", tags=[])
    edit_note(client, invoice["id"], title="Invoice", tags=["Work"])

    assert tags_in_use(client) == ["work"]


def test_tags_are_stored_in_their_normalised_form_as_they_are_on_creation(client):
    written = create_note(client, title="Invoice")

    edited = edit_note(
        client, written["id"], title="Invoice", tags=["  Work  ", "WORK", "finance"]
    )

    assert edited["tags"] == ["finance", "work"]


def test_editing_a_note_that_does_not_exist_is_refused(client):
    response = client.put("/notes/404", json={"title": "Nothing to change"})

    assert response.status_code == 404
    error = response.json()
    assert error["code"] == "not_found"
    assert set(error) <= {"code", "message", "fields"}
    assert isinstance(error["message"], str) and error["message"]


def test_a_refused_edit_writes_no_note_and_no_tag(client):
    client.put("/notes/404", json={"title": "Nothing to change", "tags": ["work"]})

    assert listed(client) == []
    assert tags_in_use(client) == []


def test_editing_a_deleted_note_is_refused_as_though_it_never_existed(client):
    written = create_note(client, title="Invoice", tags=["work"])
    delete_note(written)

    response = client.put(f"/notes/{written['id']}", json={"title": "Invoice again"})

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_an_edit_without_a_key_is_refused_and_changes_nothing(
    client, anonymous_client
):
    written = create_note(client, title="Buy milk")

    response = anonymous_client.put(
        f"/notes/{written['id']}", json={"title": "Buy something else"}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"
    assert listed(client) == [written]


REJECTED_EDITS = [
    pytest.param({"body": "No title at all"}, "title", id="title-missing"),
    pytest.param({"title": "   "}, "title", id="title-only-spaces"),
    pytest.param({"title": "x" * 201}, "title", id="title-too-long"),
    pytest.param({"title": "Fine", "body": "x" * 10_001}, "body", id="body-too-long"),
    pytest.param({"title": "Fine", "tags": ["two words"]}, "tags", id="tag-with-a-space"),
    pytest.param({"title": "Fine", "tags": ["x" * 51]}, "tags", id="tag-too-long"),
    pytest.param(
        {"title": "Fine", "tags": [f"tag-{index}" for index in range(21)]},
        "tags",
        id="more-than-twenty-tags",
    ),
    pytest.param({"title": "Fine", "tittle": "typo"}, "tittle", id="unrecognised-field"),
]


@pytest.mark.parametrize("payload, offending_field", REJECTED_EDITS)
def test_an_edit_obeys_the_rules_that_applied_on_creation(
    client, payload, offending_field
):
    written = create_note(client, title="Invoice", body="Due Friday", tags=["work"])

    response = client.put(f"/notes/{written['id']}", json=payload)

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert offending_field in [field["field"] for field in error["fields"]]


@pytest.mark.parametrize("payload, offending_field", REJECTED_EDITS)
def test_a_rejected_edit_leaves_the_note_as_it_was(client, payload, offending_field):
    written = create_note(client, title="Invoice", body="Due Friday", tags=["work"])

    client.put(f"/notes/{written['id']}", json=payload)

    assert listed(client) == [written]
    assert tags_in_use(client) == ["work"]


def test_an_edit_keeps_a_title_without_its_surrounding_spaces(client):
    written = create_note(client, title="Invoice")

    assert edit_note(client, written["id"], title="   Padded   ")["title"] == "Padded"


def test_an_edited_note_survives_a_restart(client, build_client):
    written = create_note(client, title="Invoice", tags=["work"])

    edited = edit_note(client, written["id"], title="Invoice, revised", tags=["home"])

    with build_client() as restarted:
        assert restarted.get("/notes").json() == [edited]
        assert restarted.get("/tags").json() == ["home"]
