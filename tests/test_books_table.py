import pytest
from .test_fixtures import test_no_db, test_empty_db
from reading_statistics.sqlite import insert_author, insert_series, get_author_id, get_series_id, insert_book, get_book_isbn, get_book_series_id, get_book_series_index, get_book_title, get_series_number_of_books, update_book_isbn, update_book_series, update_book_series_index, update_book_title, delete_book_isbn


@pytest.mark.parametrize("isbn, series_id, series_index, title", [(123456789, 1, 1, "Test Title")])
def test_insert_book(test_empty_db, isbn, series_id, series_index, title):
    assert get_book_isbn(isbn) == None
    insert_book(isbn, series_id, series_index, title)
    assert get_book_isbn(isbn) != None


@pytest.mark.parametrize("isbn, series_id, series_index, title", [(123456789, 1, 1, "Test Title")])
def test_get_book_isbn(test_empty_db, isbn, series_id, series_index, title):
    assert get_book_isbn(isbn) == None
    insert_book(isbn, series_id, series_index, title)
    assert get_book_isbn(isbn) == isbn


@pytest.mark.parametrize("isbn, series_id, series_index, title", [(123456789, 1, 1, "Test Title")])
def test_get_book_series_id(test_empty_db, isbn, series_id, series_index, title):
    assert get_book_series_id(isbn) == None
    insert_book(isbn, series_id, series_index, title)
    assert get_book_series_id(isbn) == series_id


@pytest.mark.parametrize("isbn, series_id, series_index, title", [(123456789, 11, 2, "Test Title")])
def test_get_book_series_index(test_empty_db, isbn, series_id, series_index, title):
    assert get_book_series_index(isbn) == None
    insert_book(isbn, series_id, series_index, title)
    assert get_book_series_index(isbn) == series_index


@pytest.mark.parametrize("isbn, series_id, series_index, title", [(123456789, 1, 1, "Test Title")])
def test_get_book_title(test_empty_db, isbn, series_id, series_index, title):
    assert get_book_title(isbn) == None
    insert_book(isbn, series_id, series_index, title)
    assert get_book_title(isbn) == title


@pytest.mark.parametrize("isbn, series_id, series_index, title", [(123456789, 2, 1.0, "Test Title 1")])
def test_get_series_number_of_books(test_empty_db, isbn, series_id, series_index, title):
    assert get_series_number_of_books(series_id) == 0
    insert_book(isbn, series_id, series_index, title)
    assert get_series_number_of_books(series_id) == 1


@pytest.mark.parametrize("old_isbn, new_isbn, series_id, series_index, title", [(123456789, 987654321, 2, 1.0, "Test Title")])
def test_update_book_isbn(test_empty_db, old_isbn, new_isbn, series_id, series_index, title):
    assert get_book_isbn(old_isbn) == None
    assert get_book_isbn(new_isbn) == None
    insert_book(old_isbn, series_id, series_index, title)
    assert get_book_isbn(old_isbn) == old_isbn
    update_book_isbn(old_isbn, new_isbn)
    assert get_book_isbn(old_isbn) == None
    assert get_book_isbn(new_isbn) == new_isbn


@pytest.mark.parametrize("isbn, old_series_name, new_series_name, old_author_name, new_author_name, series_index, title", [(123456789, "Old Series", "New Series", "Old Author", "New Author", 1, "Test Title")])
def test_update_book_series(test_empty_db, isbn, old_series_name, new_series_name, old_author_name, new_author_name, series_index, title):
    insert_author(old_author_name)
    old_author_id = get_author_id(old_author_name)
    insert_series(old_author_id, old_series_name)
    old_series_id = get_series_id(
        old_series_name, get_author_id(old_author_name))
    assert get_book_series_id(isbn) == None
    insert_book(isbn, old_series_id, series_index, title)
    assert get_book_series_id(isbn) == old_series_id
    update_book_series(isbn, new_series_name, new_author_name)
    new_series_id = get_series_id(
        new_series_name, get_author_id(new_author_name))
    assert get_book_series_id(isbn) == new_series_id


@pytest.mark.parametrize("isbn, series_id, old_series_index, new_series_index, title", [(123456789, 1, 1, 3.0, "Test Title")])
def test_update_book_series_index(test_empty_db, isbn, series_id, old_series_index, new_series_index, title):
    assert get_book_series_index(isbn) == None
    insert_book(isbn, series_id, old_series_index, title)
    assert get_book_series_index(isbn) == old_series_index
    update_book_series_index(isbn, new_series_index)
    assert get_book_series_index(isbn) == new_series_index


@pytest.mark.parametrize("isbn, series_id, series_index, old_title, new_title", [(123456789, 5, 1, "Old Title", "New Title")])
def test_update_book_title(test_empty_db, isbn, series_id, series_index, old_title, new_title):
    assert get_book_title(isbn) == None
    insert_book(isbn, series_id, series_index, old_title)
    assert get_book_title(isbn) == old_title
    update_book_title(isbn, new_title)
    assert get_book_title(isbn) == new_title


@pytest.mark.parametrize("isbn, series_id, series_index, title", [(123456789, 5, 1.5, "Title")])
def test_delete_book_isbn(test_empty_db, isbn, series_id, series_index, title):
    insert_book(isbn, series_id, series_index, title)
    assert get_book_isbn(isbn) != None
    delete_book_isbn(isbn)
    assert get_book_isbn(isbn) == None
