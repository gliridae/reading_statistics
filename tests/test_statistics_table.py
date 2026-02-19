import pytest
from .test_fixtures import test_no_db, test_empty_db
from reading_statistics.sqlite import insert_statistics, get_statistics_isbn, get_statistics_chapters, get_statistics_pages, get_statistics_released, get_statistics_finished, get_statistics_speed, get_statistics_time, update_statistics_isbn, update_statistics_chapters, update_statistics_pages, update_statistics_released, update_statistics_finished, update_statistics_speed, update_statistics_time, delete_statistics_isbn


@pytest.mark.parametrize("isbn", [(123456789)])
def test_insert_statistics(test_empty_db, isbn):
    assert get_statistics_isbn(isbn) == None
    insert_statistics(isbn)
    assert get_statistics_isbn(isbn) != None


@pytest.mark.parametrize("isbn", [(123456789), (None)])
def test_get_statistics_isbn(test_empty_db, isbn):
    assert get_statistics_isbn(isbn) == None
    if isbn != None:
        insert_statistics(isbn)
        assert get_statistics_isbn(isbn) == isbn


@pytest.mark.parametrize("isbn, chapters", [(123456789, 12)])
def test_get_statistics_chapters(test_empty_db, isbn, chapters):
    assert get_statistics_chapters(isbn) == None
    insert_statistics(isbn, chapters=chapters)
    assert get_statistics_chapters(isbn) == chapters


@pytest.mark.parametrize("isbn, pages", [(123456789, 365)])
def test_get_statistics_pages(test_empty_db, isbn, pages):
    assert get_statistics_pages(isbn) == None
    insert_statistics(isbn, pages=pages)
    assert get_statistics_pages(isbn) == pages


@pytest.mark.parametrize("isbn, released", [(123456789, "2000-01-01")])
def test_get_statistics_released(test_empty_db, isbn, released):
    assert get_statistics_released(isbn) == None
    insert_statistics(isbn, released=released)
    assert get_statistics_released(isbn) == released


@pytest.mark.parametrize("isbn, finished", [(123456789, "2000-12-31")])
def test_get_statistics_finished(test_empty_db, isbn, finished):
    assert get_statistics_finished(isbn) == None
    insert_statistics(isbn, finished=finished)
    assert get_statistics_finished(isbn) == finished


@pytest.mark.parametrize("isbn, speed", [(123456789, 150)])
def test_get_statistics_speed(test_empty_db, isbn, speed):
    assert get_statistics_speed(isbn) == None
    insert_statistics(isbn, speed=speed)
    assert get_statistics_speed(isbn) == speed


@pytest.mark.parametrize("isbn, time", [(123456789, 5.12)])
def test_get_statistics_time(test_empty_db, isbn, time):
    assert get_statistics_time(isbn) == None
    insert_statistics(isbn, time=time)
    assert get_statistics_time(isbn) == time


@pytest.mark.parametrize("old_isbn, new_isbn", [(123456789, 987654321)])
def test_update_statistics_isbn(test_empty_db, old_isbn, new_isbn):
    assert get_statistics_isbn(old_isbn) == None
    insert_statistics(old_isbn)
    update_statistics_isbn(old_isbn, new_isbn)
    assert get_statistics_isbn(new_isbn) == new_isbn


@pytest.mark.parametrize("isbn, old_chapters, new_chapters", [(123456789, 12, 36)])
def test_update_statistics_chapters(test_empty_db, isbn, old_chapters, new_chapters):
    assert get_statistics_chapters(isbn) == None
    insert_statistics(isbn, chapters=old_chapters)
    update_statistics_chapters(isbn, new_chapters)
    assert get_statistics_chapters(isbn) == new_chapters


@pytest.mark.parametrize("isbn, old_pages, new_pages", [(123456789, 365, 420)])
def test_update_statistics_pages(test_empty_db, isbn, old_pages, new_pages):
    assert get_statistics_pages(isbn) == None
    insert_statistics(isbn, pages=old_pages)
    update_statistics_pages(isbn, new_pages)
    assert get_statistics_pages(isbn) == new_pages


@pytest.mark.parametrize("isbn, old_released, new_released", [(123456789, "2000-01-01", "2020-01-01")])
def test_update_statistics_released(test_empty_db, isbn, old_released, new_released):
    assert get_statistics_released(isbn) == None
    insert_statistics(isbn, released=old_released)
    update_statistics_released(isbn, new_released)
    assert get_statistics_released(isbn) == new_released


@pytest.mark.parametrize("isbn, old_finished, new_finished", [(123456789, "2000-12-31", "2020-12-31")])
def test_update_statistics_finished(test_empty_db, isbn, old_finished, new_finished):
    assert get_statistics_finished(isbn) == None
    insert_statistics(isbn, finished=old_finished)
    update_statistics_finished(isbn, new_finished)
    assert get_statistics_finished(isbn) == new_finished


@pytest.mark.parametrize("isbn, old_speed, new_speed", [(123456789, 150, 160)])
def test_update_statistics_speed(test_empty_db, isbn, old_speed, new_speed):
    assert get_statistics_speed(isbn) == None
    insert_statistics(isbn, speed=old_speed)
    update_statistics_speed(isbn, new_speed)
    assert get_statistics_speed(isbn) == new_speed


@pytest.mark.parametrize("isbn, old_time, new_time", [(123456789, 5.12, 10.24)])
def test_update_statistics_time(test_empty_db, isbn, old_time, new_time):
    assert get_statistics_time(isbn) == None
    insert_statistics(isbn, time=old_time)
    update_statistics_time(isbn, new_time)
    assert get_statistics_time(isbn) == new_time


@pytest.mark.parametrize("isbn, ", [(123456789)])
def test_delete_statistics_isbn(test_empty_db, isbn):
    insert_statistics(isbn)
    assert get_statistics_isbn(isbn) != None
    delete_statistics_isbn(isbn)
    assert get_statistics_isbn(isbn) == None
