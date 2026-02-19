import pytest
from .test_fixtures import test_no_db, test_empty_db
from reading_statistics.constants import LIBRARY_LOCATION, VIEWS_LOCATION
from reading_statistics.sqlite import load_library_from_json, check_tables, create_views, get_books_info


def test_load_library_from_json_errors(test_no_db, capfd):
    load_library_from_json(LIBRARY_LOCATION)
    out = capfd.readouterr()
    assert out[0].startswith(
        "\nAt least one table is corrupted. Please fix them manually:")


def test_check_tables(test_no_db):
    assert check_tables(["authors", "series", "books",
                        "statistics"]).__len__() == 4


def test_create_tables(test_empty_db):
    assert check_tables(["authors", "series", "books",
                        "statistics"]).__len__() == 0


def test_load_library_from_json(test_empty_db):
    result = get_books_info("", "", "", "")
    before = result.__len__()
    assert before == 0
    load_library_from_json(LIBRARY_LOCATION)
    result = get_books_info("", "", "", "")
    after = result.__len__()
    assert before < after


@pytest.mark.parametrize("query", [("select * from 'Unread Series by Date'")])
def test_create_views(test_empty_db, query):
    assert check_tables([query]).__len__() == 1
    create_views(VIEWS_LOCATION)
    assert check_tables([query]).__len__() == 0
