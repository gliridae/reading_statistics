import pytest
from .test_fixtures import test_no_db, test_empty_db
from reading_statistics.sqlite import insert_author, get_author_id, get_author_name, update_author_name, delete_author_id


@pytest.mark.parametrize("name", [("Test Name")])
def test_insert_author(test_empty_db, name):
    assert get_author_id(name) == None
    insert_author(name)
    assert get_author_id(name) != 0


@pytest.mark.parametrize("id, name", [(1, "Test Name"), (None, None)])
def test_get_author_name(test_empty_db, id, name):
    assert get_author_name(id) == None
    if id != None:
        insert_author(name)
        assert get_author_name(id) == name


@pytest.mark.parametrize("old_name, new_name", [("Test Name", "John Doe")])
def test_update_author_name(test_empty_db, old_name, new_name):
    assert get_author_id(old_name) == None
    assert get_author_id(new_name) == None
    insert_author(old_name)
    id = get_author_id(old_name)
    update_author_name(id, new_name)
    assert get_author_name(id) == new_name


@pytest.mark.parametrize("name", [("Test Name")])
def test_delete_author_name(test_empty_db, name):
    insert_author(name)
    id = get_author_id(name)
    assert id != None
    delete_author_id(id)
    assert get_author_id(name) == None
