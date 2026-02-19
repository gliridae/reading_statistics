import pytest
from .test_fixtures import test_no_db, test_empty_db
from reading_statistics.sqlite import insert_series, get_series_id, get_max_series_id, get_authors_number_of_series, get_series_author_id, get_series_name, update_authors_series, update_series_author, update_series_name, delete_series_id


@pytest.mark.parametrize("author_id, name", [(1, "Test Series")])
def test_insert_series(test_empty_db, author_id, name):
    assert get_series_id(name, author_id) == None
    insert_series(author_id, name)
    assert get_series_id(name, author_id) != None


@pytest.mark.parametrize("author_id, name, series_id", [(1, "Test Series", 1)])
def test_get_series_id(test_empty_db, author_id, name, series_id):
    assert get_series_id(name, author_id) == None
    insert_series(author_id, name)
    assert get_series_id(name, author_id) == series_id


@pytest.mark.parametrize("author_id, name, series_id", [(1, "Test Series", 1)])
def test_get_max_series_id(test_empty_db, author_id, name, series_id):
    assert get_max_series_id() == 0
    insert_series(author_id, name)
    assert get_max_series_id() == series_id


@pytest.mark.parametrize("author_id, series_name", [(1, "Series 1")])
def test_get_authors_number_of_series(test_empty_db, author_id, series_name):
    assert get_authors_number_of_series(author_id) == 0
    insert_series(author_id, series_name)
    assert get_authors_number_of_series(author_id) == 1


@pytest.mark.parametrize("author_id, name", [(1, "Test Series")])
def test_get_series_author_id(test_empty_db, author_id, name):
    assert get_series_author_id(1) == None
    insert_series(author_id, name)
    assert get_series_author_id(1) == author_id


@pytest.mark.parametrize("author_id, name, series_id", [(1, "Test Series", 1)])
def test_get_series_name(test_empty_db, author_id, name, series_id):
    assert get_series_name(series_id) == None
    insert_series(author_id, name)
    assert get_series_name(series_id) == name


@pytest.mark.parametrize("old_author_id, new_author_id, series_name", [(1, 2, "Test Series")])
def test_update_authors_series(test_empty_db, old_author_id, new_author_id, series_name):
    insert_series(old_author_id, series_name)
    assert get_series_author_id(1) == old_author_id
    update_authors_series(old_author_id, new_author_id)
    assert get_series_author_id(1) == new_author_id


@pytest.mark.parametrize("old_author_id, new_author_id, series_name", [(1, 2, "Test Series")])
def test_update_series_author(test_empty_db, old_author_id, new_author_id, series_name):
    insert_series(old_author_id, series_name)
    assert get_series_author_id(1) == old_author_id
    update_series_author(1, new_author_id)
    assert get_series_author_id(1) == new_author_id


@pytest.mark.parametrize("author_id, series_id, old_series_name, new_series_name", [(1, 1, "Old Series", "New Series")])
def test_update_series_name(test_empty_db, author_id, series_id, old_series_name, new_series_name):
    insert_series(author_id, old_series_name)
    update_series_name(1, new_series_name)
    assert get_series_name(series_id) == new_series_name


@pytest.mark.parametrize("author_id, series_name", [(1, "Series")])
def test_delete_series_name(test_empty_db, author_id, series_name):
    insert_series(author_id, series_name)
    series_id = get_series_id(series_name, author_id)
    assert series_id != None
    delete_series_id(series_id)
    assert get_series_id(series_name, author_id) == None
