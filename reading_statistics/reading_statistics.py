from .constants import DATABASE_LOCATION, LIBRARY_LOCATION, VIEWS_LOCATION
from .sqlite import *
from .Book import Book

# TODO: refactor logic to prevent creating duplicates when updating existing data because right now it's not working as expected
# TODO: check if the logic for each add, update or delete can be simplified
# TODO: add functionality to load the book's data from json file to add a new book or update its information if it already exists in the database


def database_setup():
    """Create needed tables in database
    """
    create_tables()
    db.commit()
    print("\nTables created\n")


def views_setup(views_location: str):
    """Create views using SQL statements in a provided json file

    Args:
        views_location (str): Path to a json file containing SQL statements to create views
    """
    create_views(views_location)
    db.commit()
    print("\nViews created\n")


def load_json(library_location: str):
    """Loads books data from json file

    Args:
        library_location (str): Path to a json file containing books data
    """
    load_library_from_json(library_location)
    db.commit()
    print("\nLoading completed\n")


def update_author():
    """Update existing author's name
    """
    errors = check_tables(["authors"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            old_name = input("Old name: ")
            new_name = input("New name: ")
            author_id = get_author_id(old_name)
            if old_name == "":
                if new_name == "":
                    condition = False
                    print("\nInputs were empty, cancelling.\n")
                else:
                    print("\nProvided old name was empty, try again.\n")
            elif new_name == "":
                print("\nProvided new name was empty, try again.\n")
            elif author_id == None:
                print(
                    f"\nThe name \"{old_name}\" does not exist in the database, try again.\n")
            else:
                update_author_name(author_id, new_name)
                db.commit()
                condition = False
                print(f"\nName has been changed to '{new_name}'.\n")
    else:
        print(f"\nTable corrupted. Please fix it manually:\n{errors}")


def delete_author():
    """Delete Author but only if they have no series
    """
    errors = check_tables(["authors", "series"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            author_name = input("Author's name: ")
            if author_name != "":
                author_id = get_author_id(author_name)
                if author_id != None:
                    number_of_series = get_authors_number_of_series(author_id)
                    if number_of_series == 0:
                        delete_author_id(get_author_id(author_name))
                        db.commit()
                        condition = False
                        id = get_author_id(author_name)
                        if id != None:
                            print(
                                f"\nAuthor \"{author_name}\" was NOT removed.\n")
                        else:
                            print(f"\nAuthor \"{author_name}\" was removed.\n")
                    else:
                        condition = False
                        print(
                            f"\nCould not remove author \"{author_name}\". There are still {number_of_series} series connected to this author, unlink them from the author first.\n")
                else:
                    print(
                        f"\nAuthor \"{author_name}\" does NOT exist in the database. Try again.\n")
            else:
                condition = False
                print("\nInput was empty, cancelling.\n")
    else:
        print(f"\nTable corrupted. Please fix it manually:\n{errors}")


def update_series():
    """Update existing series
    """
    errors = check_tables(["authors", "series"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            old_series_name = input("Series current name: ")
            old_author_name = input("Author's current name: ")
            new_series_name = input("Series new name: ")
            new_author_name = input("Author's new name: ")
            old_author_id = get_author_id(old_author_name)
            new_author_id = get_author_id(new_author_name)
            old_series_id = get_series_id(old_series_name, old_author_id)
            new_series_id = get_series_id(new_series_name, new_author_id)
            if (old_series_name == "" and old_author_name == "") or (new_series_name == "" and new_author_name == ""):
                condition = False
                print("\nMandatory fields were empty, cancelling.\n")
            elif old_series_name == "" or old_author_name == "":
                print("\nOne of the mandatory fields was empty, try again.\n")
            elif old_series_id == None:
                print(
                    f"\nSeries \"{old_series_name}\" written by \"{old_author_name}\" does not exist in the database, try again.\n")
            elif new_series_id != None:
                print(
                    f"\nSeries \"{new_series_name}\" written by \"{old_author_name}\" already exists in the database, try again.\n")
            else:
                if new_series_name != "":
                    update_series_name(old_series_id, new_series_name)
                    db.commit()
                    condition = False
                    print(
                        f"\nUpdated series name from \"{old_series_name}\" to \"{new_series_name}\".\n")
                if new_author_name != "":
                    insert_author(new_author_name)
                    new_author_id = get_author_id(new_author_name)
                    update_series_author(old_series_id, new_author_id)
                    db.commit()
                    condition = False
                    print(
                        f"\nUpdated author from \"{old_author_name}\" to \"{new_author_name}\".\n")
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def delete_series():
    """Delete Series but only if it has no books
    """
    errors = check_tables(["series", "books"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            series_name = input("Series name: ")
            author_name = input("Author's name: ")
            if author_name != "" and series_name != "":
                author_id = get_author_id(author_name)
                series_id = get_series_id(series_name, author_id)
                if series_id != None:
                    number_of_books = get_series_number_of_books(series_id)
                    if number_of_books == 0:
                        delete_series_id(series_id)
                        db.commit()
                        condition = False
                        id = get_series_id(series_name, author_id)
                        if id != None:
                            print(
                                f"\nSeries \"{series_name}\" by \"{author_name}\" was NOT removed.\n")
                        else:
                            print(
                                f"\nSeries \"{series_name}\" by \"{author_name}\" was removed.\n")
                    else:
                        print(
                            f"\nCould not remove series \"{series_name}\". There is/are still {number_of_books} book(s) connected to this series, unlink them first.\n")
                else:
                    print(
                        f"\nSeries \"{series_name}\" by \"{author_name}\" does NOT exist in the database, try again.\n")
            elif series_name == "" and author_name == "":
                condition = False
                print("\nInputs were empty, cancelling.\n")
            else:
                print("\nOne of the inputs was empty, try again.\n")
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def add_a_book():
    """Add book's data from user input
    """
    errors = check_tables(["authors", "series", "books", "statistics"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            book = Book
            book.isbn = input("Book's ISBN: ")
            book.title = input("Book's title: ")
            book.series_name = input("Series name: ")
            book.series_index = input("Series index: ")
            book.author_name = input("Author's name: ")
            book.chapters = input("Number of chapters: ")
            book.pages = input("Number of pages: ")
            book.released = input("Release date: ")
            book.finished = input("Date when finished reading: ")
            book.speed = input("Reading speed [w/m]: ")
            book.time = input("Reading time [h]: ")
            try:
                if book.isbn != "" and book.isbn != None:
                    if book.author_name == "":
                        book.author_name = None
                        author_id = None
                    else:
                        insert_author(book.author_name)
                        author_id = get_author_id(book.author_name)
                    if book.series_name == "" or author_id == None:
                        series_id = None
                    else:
                        insert_series(author_id, book.series_name)
                        series_id = get_series_id(book.series_name, author_id)
                    if book.title == "":
                        book.title = None
                    if book.series_index == "":
                        book.series_index = None
                    else:
                        book.series_index = float(book.series_index)
                        book.isbn = int(book.isbn)
                    if book.chapters == "":
                        book.chapters = None
                    else:
                        book.chapters = int(book.chapters)
                    if book.pages == "":
                        book.pages = None
                    else:
                        book.pages = int(book.pages)
                    if book.released == "":
                        book.released = None
                    if book.finished == "":
                        book.finished = None
                    if book.speed == "":
                        book.speed = None
                    else:
                        book.speed = int(book.speed)
                    if book.time == "":
                        book.time = None
                    else:
                        book.time = float(book.time)
                    insert_book(book.isbn, series_id,
                                book.series_index, book.title)
                    insert_statistics(book.isbn, book.chapters, book.pages,
                                      book.released, book.finished, book.speed, book.time)
                    db.commit()
                    condition = False
                    id_book = get_book_isbn(book.isbn)
                    id_statistics = get_statistics_isbn(book.isbn)
                    if id_book == id_statistics:
                        print(f"\nAdded book with ISBN: {id_book}")
                    else:
                        print(
                            f"\nSomething went wrong. There's a mismatch between added ISBN numbers in tables:\nBook:\t{id_book}\nStatistics:\t{id_statistics}\n")
                elif book.isbn == "" and (book.author_name != "" or
                                          book.series_name != "" or
                                          book.series_index != "" or
                                          book.title != "" or
                                          book.chapters != "" or
                                          book.pages != "" or
                                          book.released != "" or
                                          book.finished != "" or
                                          book.speed != "" or
                                          book.time != ""):
                    print(
                        "\nISBN was empty while at least one other input was not, try again.\n")
                else:
                    condition = False
                    print("\nInputs were empty, cancelling.\n")
            except ValueError:
                print("\nUnable to convert some inputs to number, try again.\n")
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def get_books():
    """Get information about books matching search parameters
    """
    errors = check_tables(["authors", "series", "books", "statistics"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            isbn = input("ISBN: ")
            author = input("Author's name: ")
            series = input("Series name: ")
            title = input("Book's title: ")
            try:
                if isbn == "" and author == "" and series == "" and title == "":
                    condition = False
                    print("\nInputs were empty, cancelling.\n")
                else:
                    if isbn != '':
                        isbn = int(isbn)
                    list_of_books = get_books_info(isbn, author, series, title)
                    if list_of_books.__len__() == 0:
                        print("\nNo books found mathing the inputs, try again.\n")
                    else:
                        print(f"\nFound {list_of_books.__len__()} book(s):")
                        for index, book in enumerate(list_of_books):
                            print(f"\n\tBook #{index+1}:")
                            book.print()
                        condition = False
            except ValueError:
                print("\nUnable to convert ISBN to number, try again.\n")
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def update_book():
    """Update existing book's data
    """
    errors = check_tables(["authors", "series", "books"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            book = Book
            book.isbn = input("Current ISBN: ")
            try:
                if book.isbn != "":
                    book.isbn = int(book.isbn)
                    book.title = get_book_title(book.isbn)
                    book.series_name = get_series_name(
                        get_book_series_id(book.isbn))
                    book.series_index = get_book_series_index(book.isbn)
                    book.author_name = get_author_name(
                        get_series_author_id(get_book_series_id(book.isbn)))
                    print(
                        f"\n\tCurrent data:\nISBN:\t\t{book.isbn}\nTitle:\t\t{book.title}\nSeries name:\t{book.series_name}\nIndex:\t\t{book.series_index}\nAuthor:\t\t{book.author_name}\n\n")
                    isbn = input("New ISBN: ")
                    title = input("New title: ")
                    series_name = input("New series name: ")
                    series_index = input("New series index: ")
                    author_name = input("New author's name: ")
                    if isbn == "" and title == "" and series_name == "" and series_index == "" and author_name == "":
                        print("\nDid not provide updated data, try again.\n")
                    else:
                        if isbn != "":
                            update_book_isbn(book.isbn, int(isbn))
                            book.isbn = int(isbn)
                        if title != "":
                            book.title = title
                            update_book_title(book.isbn, book.title)
                        if series_name != "" and author_name != "":
                            book.series_name = series_name
                            book.author_name = author_name
                            update_book_series(
                                book.isbn, book.series_name, book.author_name)
                        if series_index != "":
                            book.series_index = float(series_index)
                            update_book_series_index(
                                book.isbn, book.series_index)
                        db.commit()
                        condition = False
                        print(
                            f"\n\tUpdated data to:\nISBN:\t\t{book.isbn}\nTitle:\t\t{book.title}\nSeries name:\t{book.series_name}\nIndex:\t\t{book.series_index}\nAuthor:\t\t{book.author_name}\n\n")
                else:
                    condition = False
                    print("\nInputs were empty, cancelling.\n")
            except ValueError:
                print("\nUnable to convert some inputs to number, try again.\n")
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def delete_book():
    """Delete Book but only if it has no statistics
    """
    errors = check_tables(["books", "statistics"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            isbn = input("Book's ISBN: ")
            try:
                if isbn != "":
                    isbn = int(isbn)
                    book_id = get_book_isbn(isbn)
                    if book_id != None:
                        statistics_id = get_statistics_isbn(isbn)
                        if statistics_id == None:
                            delete_book_isbn(book_id)
                            db.commit()
                            condition = False
                            id = get_book_isbn(book_id)
                            if id != None:
                                print(
                                    f"\nBook with ISBN \"{isbn}\" was NOT removed.\n")
                            else:
                                print(
                                    f"\nBook with ISBN \"{isbn}\" was removed.\n")
                        else:
                            print(
                                f"\nThere are some statistics available for ISBN {isbn}, remove them first and try again.\n")
                    else:
                        print(
                            f"\nBook with ISBN {isbn} does NOT exist in the database, try again.\n")
                else:
                    condition = False
                    print("\nInput was empty, cancelling.\n")
            except ValueError:
                print("\nUnable to convert ISBN to number, try again.\n")
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def update_statistics():
    """Update statistics for a book
    """
    errors = check_tables(["statistics"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            book = Book
            book.isbn = input("Book's ISBN: ")
            if book.isbn != "":
                try:
                    book.isbn = int(book.isbn)
                    book.chapters = get_statistics_chapters(book.isbn)
                    book.pages = get_statistics_pages(book.isbn)
                    book.released = get_statistics_released(book.isbn)
                    book.finished = get_statistics_finished(book.isbn)
                    book.speed = get_statistics_speed(book.isbn)
                    book.time = get_statistics_time(book.isbn)
                    print(
                        f"\n\tCurrent data:\nISBN:\t\t{book.isbn}\nChapters:\t{book.chapters}\nPages:\t\t{book.pages}\nReleased:\t{book.released}\nFinished:\t{book.finished}\nSpeed:\t\t{book.speed}\nTime:\t\t{book.time}\n\n")
                    isbn = input("New ISBN: ")
                    chapters = input("Number of chapters: ")
                    pages = input("Number of pages: ")
                    released = input("Release date: ")
                    finished = input("Date when finished reading: ")
                    speed = input("Reading speed [w/m]: ")
                    time = input("Reading time [h]: ")
                    if chapters == "" and pages == "" and released == "" and finished == "" and speed == "" and time == "":
                        print(f"\nDid not provide updated data, try again.\n")
                    else:
                        if isbn != "":
                            update_statistics_isbn(book.isbn, int(isbn))
                            book.isbn = isbn
                        if chapters != "":
                            update_statistics_chapters(
                                book.isbn, int(chapters))
                            book.chapters = chapters
                        if pages != "":
                            update_statistics_pages(book.isbn, int(pages))
                            book.pages = pages
                        if released != "":
                            update_statistics_released(book.isbn, released)
                            book.released = released
                        if finished != "":
                            update_statistics_finished(book.isbn, finished)
                            book.finished = finished
                        if speed != "":
                            update_statistics_speed(book.isbn, int(speed))
                            book.speed = speed
                        if time != "":
                            update_statistics_time(book.isbn, float(time))
                            book.time = float(time)
                        db.commit()
                        condition = False
                        print(
                            f"\n\tUpdated data to:\nISBN:\t\t{book.isbn}\nChapters:\t{book.chapters}\nPages:\t\t{book.pages}\nReleased:\t{book.released}\nFinished:\t{book.finished}\nSpeed:\t\t{book.speed}\nTime:\t\t{book.time}\n\n")
                except ValueError:
                    print("\nUnable to convert some inputs to number, try again.\n")
            else:
                condition = False
                print("\nISBN was empty, cancelling.\n")
    else:
        print(f"\nTable corrupted. Please fix it manually:\n{errors}")


def delete_statistics():
    """Delete statistics of a book
    """
    errors = check_tables(["statistics"])
    if errors.__len__() == 0:
        condition = True
        while condition:
            isbn = input("Books's ISBN: ")
            try:
                if isbn != "":
                    isbn = int(isbn)
                    statistics_id = get_statistics_isbn(isbn)
                    if statistics_id != None:
                        delete_statistics_isbn(isbn)
                        db.commit()
                        condition = False
                        id = get_statistics_isbn(isbn)
                        if id != None:
                            print(
                                f"\nStatistics for ISBN \"{isbn}\" were NOT removed.\n")
                        else:
                            print(
                                f"\nStatistics for ISBN \"{isbn}\" were removed.\n")
                    else:
                        print(
                            f"\nStatistics for ISBN {isbn} do NOT exist in the database, try again.\n")
                else:
                    condition = False
                    print("\nInput was empty, cancelling.\n")
            except ValueError:
                print("\nUnable to convert ISBN to number, try again.\n")
    else:
        print(f"\nTable corrupted. Please fix it manually:\n{errors}")
