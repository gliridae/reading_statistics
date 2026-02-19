import pytest
from .test_fixtures import test_no_db, test_empty_db, test_db
from reading_statistics.constants import LIBRARY_LOCATION, VIEWS_LOCATION
from reading_statistics.sqlite import check_tables, get_max_author_id, get_author_id, get_series_id, get_book_isbn, get_author_name, get_series_name, get_series_author_id, get_book_series_id, get_statistics_time, get_authors_number_of_series, get_series_number_of_books, insert_book
from reading_statistics.reading_statistics import database_setup, load_json, views_setup, add_a_book, get_books, update_author, update_series, update_book, update_statistics, delete_author, delete_series, delete_book, delete_statistics


def test_load_json_error(test_no_db, capfd):
    load_json(LIBRARY_LOCATION)
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


def test_views_setup_error(test_no_db, capfd):
    views_setup(VIEWS_LOCATION)
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


def test_add_a_book_error(test_no_db, capfd):
    add_a_book()
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


def test_get_books_error(test_no_db, capfd):
    get_books()
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


def test_update_author_error(test_no_db, capfd):
    update_author()
    out = capfd.readouterr()
    assert out[0].startswith("\nTable corrupted.")


def test_update_series_error(test_no_db, capfd):
    update_series()
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


def test_update_book_error(test_no_db, capfd):
    update_book()
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


@pytest.mark.parametrize("isbn, output",
                         [("test", "\nUnable to convert some inputs to number")])
def test_update_book_isbn_conversion_error(test_db, monkeypatch, capfd, isbn, output):
    # Needed seperate test just to check ISBN conversion error flow.
    responses = iter([isbn])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        update_book()
    except StopIteration:
        ending = "try again.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].__contains__(output)
        assert out[0].endswith(f"{ending}\n")


def test_update_statistics_error(test_no_db, capfd):
    update_statistics()
    out = capfd.readouterr()
    assert out[0].startswith("\nTable corrupted.")


@pytest.mark.parametrize("isbn, output",
                         [("test", "\nUnable to convert some inputs to number")])
def test_update_statistics_isbn_conversion_error(test_db, monkeypatch, capfd, isbn, output):
    # Needed seperate test just to check ISBN conversion error flow.
    responses = iter([isbn])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        update_statistics()
    except StopIteration:
        ending = "try again.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].__contains__(output)
        assert out[0].endswith(f"{ending}\n")


def test_delete_author_error(test_no_db, capfd):
    delete_author()
    out = capfd.readouterr()
    assert out[0].startswith("\nTable corrupted.")


def test_delete_series_error(test_no_db, capfd):
    delete_series()
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


def test_delete_book_error(test_no_db, capfd):
    delete_book()
    out = capfd.readouterr()
    assert out[0].startswith("\nAt least one table is corrupted.")


def test_delete_statistics_error(test_no_db, capfd):
    delete_statistics()
    out = capfd.readouterr()
    assert out[0].startswith("\nTable corrupted.")


def test_database_setup(test_no_db):
    assert check_tables(["authors", "series", "books",
                        "statistics"]).__len__() > 0
    database_setup()
    assert check_tables(["authors", "series", "books",
                        "statistics"]).__len__() == 0


@pytest.mark.parametrize("library", [LIBRARY_LOCATION, "./tests/test_library.json"])
def test_load_json(test_empty_db, library):
    assert get_max_author_id() == 0
    load_json(library)
    assert get_max_author_id() != 0


@pytest.mark.parametrize("query", [["select * from 'Unread Series by Date'"]])
def test_views_setup(test_empty_db, query):
    assert check_tables(query).__len__() == 1
    views_setup(VIEWS_LOCATION)
    assert check_tables(query).__len__() == 0


@pytest.mark.parametrize("isbn, title, series, index, author, chapters, pages, released, finished, speed, time, output",
                         [(9780804139021, "The Martian", "The Martian", 1, "Andy Weir", 26, 384, "2011-09-27", "2023-06-20", 150, 8, "\nAdded book with ISBN: "),
                          ("9780804139021", "The Martian", "The Martian", "1", "Andy Weir", "26",
                           "384", "2011-09-27", "2023-06-20", "150", "8", "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "Andy Weir",
                           "", "", "", "", "", "", "\nAdded book with ISBN:"),
                          (9780804139021, "", "The Martian", 1, "Andy Weir", 26, 384, "2011-09-27",
                           "2023-06-20", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "", 1, "Andy Weir", 26, 384, "2011-09-27",
                           "2023-06-20", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", "", "Andy Weir", 26, 384,
                           "2011-09-27", "2023-06-20", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "", 26, 384, "2011-09-27",
                           "2023-06-20", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "Andy Weir", "", 384,
                           "2011-09-27", "2023-06-20", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "Andy Weir", 26, "",
                           "2011-09-27", "2023-06-20", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "Andy Weir", 26, 384,
                           "", "2023-06-20", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "Andy Weir", 26, 384,
                           "2011-09-27", "", 150, 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "Andy Weir", 26, 384,
                           "2011-09-27", "2023-06-20", "", 8, "\nAdded book with ISBN:"),
                          (9780804139021, "The Martian", "The Martian", 1, "Andy Weir", 26, 384,
                           "2011-09-27", "2023-06-20", 150, "", "\nAdded book with ISBN:"),
                          (9780804139021, "", "", "1,0", "", "", "", "", "",
                           "", "", "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "test", "", "", "", "", "",
                           "", "", "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "", "", "test", "", "", "",
                           "", "", "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "", "", "", "test", "", "",
                           "", "", "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "", "", "", "", "", "", "test",
                           "", "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "", "", "", "", "", "", "",
                           "test", "\nUnable to convert some inputs to number"),
                          ("", "The Martian", "The Martian", 1, "Andy Weir", 26, 384,
                           "2011-09-27", "2023-06-20", 150, 8, "\nISBN was empty"),
                          ("", "", "", "", "", "", "", "", "", "", "", "\nInputs were empty")])
def test_add_a_book(test_empty_db, monkeypatch, capfd, isbn, title, series, index, author, chapters, pages, released, finished, speed, time, output):
    responses = iter([isbn, title, series, index, author,
                     chapters, pages, released, finished, speed, time])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        add_a_book()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        ending = get_book_isbn(isbn)
        if ending == None:
            ending = "cancelling.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("isbn, author, series, title, output",
                         [(1234, "", "", "", "\nNo books found"),
                          (9780804139021, "", "", "", "\nFound 1 book(s):"),
                          ("9780804139021", "", "", "", "\nFound 1 book(s):"),
                          ("", "", "Mary", "Hail", "\nFound 1 book(s):"),
                          ("", "Weir", "", "", "\nFound 3 book(s):"),
                          ("", "", "", "", "\nInputs were empty"),
                          ("test", "", "", "", "\nUnable to convert ISBN to number")])
def test_get_books(test_db, monkeypatch, capfd, isbn, author, series, title, output):
    responses = iter([isbn, author, series, title])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        ending = None
        get_books()
        if isbn != "" or author != "" or series != "" or title != "":
            ending = "Time:\t\t"
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        if ending == None:
            ending = "cancelling.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].__contains__(f"{ending}")


@pytest.mark.parametrize("author_old, author_new, output",
                         [("Andy Weir", "Weir Andy", "\nName has been changed"),
                          ("Andy Weir", "", "\nProvided new name"),
                          ("", "Weir Andy", "\nProvided old name"),
                          ("Weir Andy", "Weir Andy", "\nThe name "),
                          ("", "", "\nInputs were empty")])
def test_update_author(test_db, monkeypatch, capfd, author_old, author_new, output):
    author_id = get_author_id(author_old)
    responses = iter([author_old, author_new])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        update_author()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        ending = get_author_id(author_new)
        if ending == None:
            ending = "cancelling.\n"
        else:
            ending = f"'{author_new}'.\n"
            assert get_author_name(author_id) == author_new
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("old_series, old_author, new_series, new_author, output",
                         [("The Martian", "Andy Weir", "", "Weir Andy", "\nUpdated author from"),
                          ("The Martian", "Andy Weir", "Martian",
                           "", "\nUpdated series name from"),
                          ("", "Andy Weir", "Martian", "Weir Andy",
                           "\nOne of the mandatory fields was empty"),
                          ("The Martian", "Weir Andy", "Martian", "Weir Andy",
                           f"\nSeries \"The Martian\" written by \"Weir Andy\" does not exist"),
                          ("The Martian", "Andy Weir", "Artemis", "Andy Weir",
                           f"\nSeries \"Artemis\" written by \"Andy Weir\" already exists"),
                          ("Andy Weir", "The Martian", "", "",
                           "\nMandatory fields were empty"),
                          ("", "", "Martian", "Weir Andy", "\nMandatory fields were empty")])
def test_update_series(test_db, monkeypatch, capfd, old_series, old_author, new_series, new_author, output):
    author_id = get_author_id(old_author)
    series_id = get_series_id(old_series, author_id)
    responses = iter([old_series, old_author, new_series, new_author])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        update_series()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        if (old_series == "" and old_author == "") or (new_series == "" and new_author == ""):
            ending = "cancelling.\n"
        elif new_series != "":
            ending = f"to \"{new_series}\".\n"
            assert get_series_name(series_id) == new_series
        else:
            ending = f"to \"{new_author}\".\n"
            assert get_series_author_id(series_id) == get_author_id(new_author)
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("old_isbn, new_isbn, title, series_name, series_index, author_name, output",
                         [(9780804139021, 1234567890, "Martian", "Martian", 10, "Weir Andy",  "\n\tUpdated data to:\nISBN:\t\t"), (9780804139021, "", "Martian", "Martian", 10, "Weir Andy",  "\n\tUpdated data to:\nISBN:\t\t"),
                          (9780804139021, "", "", "", "", "",
                           "\nDid not provide updated data"),
                          ("", "", "", "", "", "", "\nInputs were empty")])
def test_update_book(test_db, monkeypatch, capfd, old_isbn, new_isbn, title, series_name, series_index, author_name, output):
    responses = iter([old_isbn, new_isbn, title,
                     series_name, series_index, author_name])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        update_book()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        if old_isbn == "":
            ending = "cancelling.\n"
        else:
            if new_isbn == "":
                isbn = old_isbn
            else:
                isbn = new_isbn
            ending = f"\nAuthor:\t\t{get_author_name(get_series_author_id(get_book_series_id(isbn)))}\n\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].__contains__(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("old_isbn, new_isbn, chapters, pages, released, finished, speed, time, output",
                         [(9780804139021, 1234567890, 33, 404, "2020-20-20", "2012-12-12", 128, 9.54, "\n\tUpdated data to:\nISBN:\t\t"),
                          ("9780804139021", "1234567890", "33", "404", "2020-20-20",
                           "2012-12-12", "128", "16", "\n\tUpdated data to:\nISBN:\t\t"),
                          (9780804139021, "", "", "", "", "", "", "",
                           "\nDid not provide updated data"),
                          ("", "", "", "", "", "", "", "", "\nISBN was empty"),
                          (9780804139021, "test", "", "", "", "", "", "", ""),
                          (9780804139021, "", "test", "", "", "", "", "",
                           "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "test", "", "", "", "",
                           "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "", "", "", "test", "",
                           "\nUnable to convert some inputs to number"),
                          (9780804139021, "", "", "", "", "", "", "test", "\nUnable to convert some inputs to number")])
def test_update_statistics(test_db, monkeypatch, capfd, old_isbn, new_isbn, chapters, pages, released, finished, speed, time, output):
    responses = iter([old_isbn, new_isbn, chapters, pages,
                     released, finished, speed, time])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        update_statistics()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        if old_isbn == "":
            ending = "cancelling.\n"
        else:
            isbn = new_isbn
            ending = f"Time:\t\t{get_statistics_time(isbn)}\n\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].__contains__(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("author, output",
                         [("Kit Frick", "\nAuthor \"Kit Frick\""),
                          ("Andy Weir", "\nCould not remove author "),
                          ("Weir Andy", "\nAuthor \"Weir Andy\" does NOT exist"),
                          ("", "\nInput was empty")])
def test_delete_author(test_db, monkeypatch, capfd, author, output):
    responses = iter([author])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        delete_author()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "Try again.\n"
    else:
        author_id = get_author_id(author)
        if get_authors_number_of_series(author_id) > 0:
            ending = "unlink them from the author first.\n"
        elif author_id == None and author != "":
            ending = "was removed.\n"
        else:
            ending = "cancelling.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("series, author, output",
                         [("Silo", "Hugh Howey", "\nSeries \"Silo\" by \"Hugh Howey\""),
                          ("The Martian", "Andy Weir",
                           "\nCould not remove series \"The Martian\"."), ("Silo", "Kit Frick", "\nSeries \"Silo\" by \"Kit Frick\" does NOT exist"),
                          ("Silo", "", "\nOne of the inputs was empty"),
                          ("", "", "\nInputs were empty")])
def test_delete_series(test_db, monkeypatch, capfd, series, author, output):
    responses = iter([series, author])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        delete_series()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        if get_series_number_of_books(get_series_id(series, get_author_id(author))) > 0:
            ending = "unlink them first.\n"
        else:
            ending = "try again.\n"
    else:
        if series != "" and author != "":
            ending = "was removed.\n"
        else:
            ending = "cancelling.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("isbn, output",
                         [(1234567890123, "\nBook with ISBN \"1234567890123\""),
                          ("1234567890123", "\nBook with ISBN \"1234567890123\""),
                          (9780553448122, "\nThere are some statistics available"),
                          ("9780553448122", "\nThere are some statistics available"),
                          (1234567890, "\nBook with ISBN 1234567890 does NOT exist"),
                          ("", "\nInput was empty"),
                          ("test", "\nUnable to convert ISBN to number")])
def test_delete_book(test_db, monkeypatch, capfd, isbn, output):
    if isbn == 1234567890123 or isbn == "1234567890123":
        insert_book(isbn, 1, 1, "Test")
    responses = iter([isbn])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        delete_book()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        if isbn == "":
            ending = "cancelling.\n"
        else:
            ending = "was removed.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].endswith(f"{ending}\n")


@pytest.mark.parametrize("isbn, output",
                         [(9780593135204, "\nStatistics for ISBN \"9780593135204\""),
                          (1234567890, "\nStatistics for ISBN 1234567890 do NOT exist"),
                          ("", "\nInput was empty"),
                          ("test", "\nUnable to convert ISBN to number")])
def test_delete_statistics(test_db, monkeypatch, capfd, isbn, output):
    responses = iter([isbn])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    try:
        delete_statistics()
    except StopIteration:
        # Needed to check cases when at least one input is empty
        ending = "try again.\n"
    else:
        if isbn == "":
            ending = "cancelling.\n"
        else:
            ending = "were removed.\n"
    finally:
        out = capfd.readouterr()
        print(out[0])
        assert out[0].startswith(output)
        assert out[0].endswith(f"{ending}\n")
