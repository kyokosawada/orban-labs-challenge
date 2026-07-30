def titles_found(client, **params):
    response = client.get("/notes", params=params)
    assert response.status_code == 200, response.text
    return [note["title"] for note in response.json()]


def test_a_keyword_narrows_the_listing_to_the_notes_mentioning_it(client, create_note):
    create_note(client, title="Invoice for March")
    create_note(client, title="Standup")

    assert titles_found(client, q="invoice") == ["Invoice for March"]


def test_a_keyword_is_looked_for_in_the_body_as_well_as_the_title(client, create_note):
    create_note(client, title="Monday", body="Chase the invoice")
    create_note(client, title="Tuesday", body="Water the plants")

    assert titles_found(client, q="invoice") == ["Monday"]


def test_a_keyword_matches_wherever_it_appears_rather_than_at_the_start(
    client, create_note
):
    create_note(client, title="Chase the invoice")

    assert titles_found(client, q="invoice") == ["Chase the invoice"]


def test_a_keyword_ignores_capitalisation(client, create_note):
    create_note(client, title="Invoice")

    assert titles_found(client, q="invoice") == ["Invoice"]
    assert titles_found(client, q="INVOICE") == ["Invoice"]


def test_capitalisation_is_ignored_beyond_the_ascii_alphabet(client, create_note):
    create_note(client, title="Café")

    assert titles_found(client, q="café") == ["Café"]
    assert titles_found(client, q="CAFÉ") == ["Café"]


def test_a_letter_that_lowercases_to_itself_matches_only_itself(client, create_note):
    create_note(client, title="Straße")
    create_note(client, title="STRASSE")

    assert titles_found(client, q="straße") == ["Straße"]
    assert titles_found(client, q="strasse") == ["STRASSE"]


def test_part_of_a_word_matches_the_whole_word(client, create_note):
    create_note(client, title="Invoices")

    assert titles_found(client, q="invoice") == ["Invoices"]
    assert titles_found(client, q="voic") == ["Invoices"]


def test_a_keyword_and_a_tag_narrow_together_rather_than_apart(client, create_note):
    create_note(client, title="Invoice for March", tags=["work"])
    create_note(client, title="Standup", tags=["work"])
    create_note(client, title="Invoice from the plumber", tags=["home"])

    assert titles_found(client, q="invoice", tag="work") == ["Invoice for March"]


def test_a_keyword_and_a_tag_that_share_no_note_find_nothing(client, create_note):
    create_note(client, title="Invoice for March", tags=["work"])
    create_note(client, title="Recipe", tags=["cooking"])

    assert titles_found(client, q="invoice", tag="cooking") == []


def test_an_absent_keyword_returns_the_whole_listing(client, create_note):
    create_note(client, title="Invoice")
    create_note(client, title="Standup")

    assert titles_found(client) == ["Standup", "Invoice"]


def test_an_empty_keyword_returns_the_whole_listing_rather_than_nothing(
    client, create_note
):
    create_note(client, title="Invoice")
    create_note(client, title="Standup")

    assert titles_found(client, q="") == ["Standup", "Invoice"]
    assert titles_found(client, q="   ") == ["Standup", "Invoice"]


def test_surrounding_spaces_around_a_keyword_are_ignored(client, create_note):
    create_note(client, title="Invoice")

    assert titles_found(client, q="  invoice  ") == ["Invoice"]


def test_a_keyword_no_note_mentions_finds_nothing_rather_than_everything(
    client, create_note
):
    create_note(client, title="Invoice")

    assert titles_found(client, q="gardening") == []


def test_a_wildcard_is_looked_for_literally_rather_than_matching_anything(
    client, create_note
):
    create_note(client, title="50% off")
    create_note(client, title="Invoice")

    assert titles_found(client, q="%") == ["50% off"]
    assert titles_found(client, q="0% o") == ["50% off"]
    assert titles_found(client, q="_") == []


def test_the_notes_a_keyword_finds_are_still_most_recently_changed_first(
    client, create_note
):
    create_note(client, title="Invoice for March")
    create_note(client, title="Invoice for April")

    assert titles_found(client, q="invoice") == [
        "Invoice for April",
        "Invoice for March",
    ]


def test_a_note_found_by_a_keyword_still_carries_its_tags(client, create_note):
    create_note(client, title="Invoice", tags=["work", "finance"])

    response = client.get("/notes", params={"q": "invoice"})

    assert [note["tags"] for note in response.json()] == [["finance", "work"]]


def test_a_deleted_note_is_not_found_by_a_keyword(client, create_note, delete_note):
    march = create_note(client, title="Invoice for March")
    create_note(client, title="Invoice for April")

    delete_note(client, march)

    assert titles_found(client, q="invoice") == ["Invoice for April"]
