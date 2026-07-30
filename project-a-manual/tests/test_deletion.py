from backend.config import get_settings
from backend.db import connect


def create_note(client, **payload):
    response = client.post("/notes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def delete_note(client, note):
    response = client.delete(f"/notes/{note['id']}")
    assert response.status_code == 204, response.text
    return response


def titles_listed(client):
    response = client.get("/notes")
    assert response.status_code == 200, response.text
    return [note["title"] for note in response.json()]


def in_storage(statement, parameters):
    connection = connect(get_settings().database_path)
    try:
        return connection.execute(statement, parameters).fetchall()
    finally:
        connection.close()


def test_a_deleted_note_disappears_from_the_listing(client):
    invoice = create_note(client, title="Invoice")

    delete_note(client, invoice)

    assert titles_listed(client) == []


def test_deleting_one_note_leaves_the_others_alone(client):
    create_note(client, title="Keep me")
    invoice = create_note(client, title="Throw me away")
    create_note(client, title="Keep me too")

    delete_note(client, invoice)

    assert titles_listed(client) == ["Keep me too", "Keep me"]


def test_deleting_answers_with_nothing_to_read(client):
    invoice = create_note(client, title="Invoice")

    response = delete_note(client, invoice)

    assert response.content == b""


def test_a_deleted_note_stays_in_storage_to_be_recovered_by_hand(client):
    invoice = create_note(client, title="Deleted by mistake", body="Still wanted")

    delete_note(client, invoice)

    retained = in_storage(
        "SELECT title, body, deleted_at FROM notes WHERE id = ?", (invoice["id"],)
    )
    assert len(retained) == 1
    assert retained[0]["title"] == "Deleted by mistake"
    assert retained[0]["body"] == "Still wanted"
    assert retained[0]["deleted_at"] is not None


def test_a_note_is_read_in_full_by_its_identifier(client):
    invoice = create_note(client, title="Invoice", body="Due Friday", tags=["work"])

    response = client.get(f"/notes/{invoice['id']}")

    assert response.status_code == 200, response.text
    assert response.json() == invoice


def test_a_deleted_note_cannot_be_fetched_by_its_identifier(client):
    invoice = create_note(client, title="Invoice")

    delete_note(client, invoice)

    response = client.get(f"/notes/{invoice['id']}")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_a_deleted_note_answers_exactly_as_one_that_was_never_written(client):
    invoice = create_note(client, title="Invoice")
    delete_note(client, invoice)

    deleted = client.get(f"/notes/{invoice['id']}")
    never_written = client.get("/notes/99999")

    assert deleted.status_code == never_written.status_code
    assert deleted.json() == never_written.json()


def test_deleting_a_note_twice_answers_as_though_it_never_existed(client):
    invoice = create_note(client, title="Invoice")
    delete_note(client, invoice)

    second = client.delete(f"/notes/{invoice['id']}")
    never_written = client.delete("/notes/99999")

    assert second.status_code == 404
    assert second.json() == never_written.json()


def test_deleting_a_note_that_was_never_written_is_refused(client):
    response = client.delete("/notes/99999")

    assert response.status_code == 404
    error = response.json()
    assert error["code"] == "not_found"
    assert set(error) <= {"code", "message", "fields"}


def test_an_identifier_that_is_not_a_number_is_refused_naming_the_field(client):
    response = client.delete("/notes/not-a-number")

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert [field["field"] for field in error["fields"]] == ["note_id"]


def test_a_deleted_note_is_still_gone_after_a_restart(client, build_client):
    invoice = create_note(client, title="Invoice")
    create_note(client, title="Standup")

    delete_note(client, invoice)

    with build_client() as restarted:
        assert titles_listed(restarted) == ["Standup"]
        assert restarted.get(f"/notes/{invoice['id']}").status_code == 404


def test_no_published_address_offers_a_way_back_to_a_deleted_note(client):
    schema = client.get("/openapi.json").json()

    addresses = " ".join(schema["paths"])
    assert "deleted" not in addresses
    assert "restore" not in addresses

    parameters = [
        parameter["name"]
        for operations in schema["paths"].values()
        for operation in operations.values()
        for parameter in operation.get("parameters", [])
    ]
    assert [name for name in parameters if "deleted" in name] == []
