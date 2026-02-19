import json
from io import StringIO
from sqlalchemy import create_engine, text, exc, MetaData, Table, Column, String, Integer, Float
from typing import Optional
from .constants import *
from .Book import Book
from .Database import Database

db = Database
db.engine = create_engine(f"sqlite+pysqlite:///{DATABASE_LOCATION}")
db.connection = db.engine.connect()


def load_book(json: dict) -> Book:
    """Extract data about individual book from json file and return a Book object containing that data

    Args:
        json (dict): JSON object containing book's data

    Returns:
        Book: Object containing book's data
    """
    return Book(json["author_name"],
                json["series_name"],
                json["isbn"],
                json["title"],
                json["series_index"],
                json["chapters"],
                json["pages"],
                json["released"],
                json["finished"],
                json["speed"],
                json["time"])


def check_tables(queries: list[str]) -> list[str]:
    """Using provided list of queries check if tables contain all columns

    Args:
        queries (list[str]): List of queries used to check if tables are corrupted

    Returns:
        list[str]: List of errors encountered
    """
    errors = []
    for query in queries:
        if query == "authors":
            q = "select author_id, name from authors"
        elif query == "series":
            q = "select series_id, name, author_id from series"
        elif query == "books":
            q = "select isbn, series_id, series_index, title from books"
        elif query == "statistics":
            q = "select isbn, chapters, pages, released, finished, speed, time from statistics"
        else:
            q = query
        try:
            db.connection.execute(text(q))
        except exc.OperationalError as e:
            errors.append(e)
    return errors


def create_tables():
    """Create needed tables in database
    """
    print("Creating tables")
    # for i in CREATE_TABLES:
    #     db.connection.execute(text(i))
    metadata_obj = MetaData()
    author = Table('authors',
                   metadata_obj,
                   Column('author_id', Integer,
                          primary_key=True, autoincrement=True),
                   Column('name', String, unique=True, nullable=False))
    series = Table('series',
                   metadata_obj,
                   Column('series_id', Integer,
                          primary_key=True, autoincrement=True),
                   Column('name', String, nullable=False),
                   Column('author_id', Integer, nullable=False))
    books = Table('books',
                  metadata_obj,
                  Column('isbn', Integer, primary_key=True, unique=True),
                  Column('series_id', Integer, nullable=True),
                  Column('series_index', Float, nullable=True),
                  Column('title', String, nullable=True)
                  )
    statistics = Table('statistics',
                       metadata_obj,
                       Column('isbn', Integer, primary_key=True, unique=True),
                       Column('chapters', Integer, nullable=True),
                       Column('pages', Integer, nullable=True),
                       Column('released', String, nullable=True),
                       Column('finished', String, nullable=True),
                       Column('speed', Integer, nullable=True),
                       Column('time', Float, nullable=True))
    metadata_obj.create_all(db.engine)


def create_views(views_location: str):
    """Load queries to create views

    Args:
        views_location (str): Location of json file with queries to load views
    """
    errors = check_tables(["authors", "series", "books", "statistics"])
    if errors.__len__() == 0:
        print("Creating views")
        with open(views_location, "r") as file:
            data = json.load(file)
            for v in data["views"]:
                x = v.get("view")
                db.connection.execute(text(x))
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def load_library_from_json(library_location: str):
    """Load books from json file

    Args:
        library_location (str): Location of json file to load books from
    """
    errors = check_tables(["authors", "series", "books", "statistics"])
    if errors.__len__() == 0:
        count = 0
        print("Adding books from json")
        with open(library_location, "r") as file:
            data = json.load(file)
            for b in data["books"]:
                book = load_book(b)
                if book.author_name != None:
                    insert_author(book.author_name)
                    author_id = get_author_id(book.author_name)
                if book.series_name != None:
                    insert_series(author_id, book.series_name)
                    series_id = get_series_id(book.series_name, author_id)
                if book.isbn != None:
                    insert_book(book.isbn, series_id,
                                book.series_index, book.title)
                    insert_statistics(book.isbn, book.chapters, book.pages,
                                      book.released, book.finished, book.speed, book.time)
                count += 1
        print(f"Loaded {count} books.")
    else:
        print(
            f"\nAt least one table is corrupted. Please fix them manually:\n{errors}")


def insert_author(name: str):
    """Add new author if they're not in the database yet

    Args:
        name (str): Name of the author
    """
    if get_author_id(name) == None and name != '':
        max_id = get_max_author_id()
        db.connection.execute(
            text(f"insert into authors values ({max_id+1}, \"{name}\")"))


def get_author_id(name: str) -> Optional[int]:
    """Get the author's ID from the database

    Args:
        name (str): Name of the author

    Returns:
        Optional[int]: ID of the author or None if author was not found
    """
    if name == '':
        return None
    else:
        result = db.connection.execute(
            text(f"select author_id from authors where name = \"{name}\""))
        rows = result.all().copy()
        if rows.__len__() == 0:
            return None
        else:
            return rows[0][0]


def get_max_author_id() -> Optional[int]:
    """Use to get the highest author_id from authors table

    Returns:
        Optional[int]: Highest ID in author_id field
    """
    result = db.connection.execute(text(f"select max(author_id) from authors"))
    rows = result.all().copy()
    id = rows[0][0]
    if id == None:
        return 0
    else:
        return id


def get_author_name(id: int) -> Optional[str]:
    """Get author's name using given ID

    Args:
        id (int): ID of the author to find

    Returns:
        Optional[str]: Author's name connected to given ID
    """
    if id == None:
        return None
    else:
        results = db.connection.execute(
            text(f"select name from authors where author_id = {id}"))
        rows = results.all().copy()
        if rows.__len__() == 0:
            return None
        else:
            return rows[0][0]


def update_author_name(id: int, name: str):
    """Update the given author's ID name to provided string

    Args:
        id (int): ID of the author to update
        name (str): New name to be used for the author of given ID
    """
    if get_author_name(id) != None:
        db.connection.execute(
            text(f"update authors set name = \"{name}\" where author_id = {id}"))


def delete_author_id(author_id: int):
    """Delete author with provided id

    Args:
        id (int): ID of the author to delete
    """
    db.connection.execute(
        text(f"delete from authors where author_id = {author_id}"))


def insert_series(author_id: int, series_name: str):
    """Add new series if it's not in the database yet

    Args:
        author_id (int): ID of the author
        series_name (str): Name of the series
    """
    if get_series_id(series_name, author_id) == None:
        max_id = get_max_series_id()
        db.connection.execute(
            text(f"insert into series values ({max_id+1}, \"{series_name}\", {author_id})"))


def get_series_id(name: str, author_id: int) -> Optional[int]:
    """Get the series ID from the database

    Args:
        name (str): Series name
        author_id (int): ID of the author of the series

    Returns:
        Optional[int]: ID of the series or None if series was not found
    """
    if name == '' or author_id == None:
        return None
    else:
        result = db.connection.execute(text(
            f"select series_id from series where name = \"{name}\" and author_id = {author_id}"))
        rows = result.all().copy()
        if rows.__len__() == 0:
            return None
        else:
            return rows[0][0]


def get_max_series_id() -> int:
    """Use to get the highest series_id from series table

    Returns:
        int: Highest ID in series_id field
    """
    result = db.connection.execute(text(f"select max(series_id) from series"))
    rows = result.all().copy()
    id = rows[0][0]
    if id == None:
        return 0
    else:
        return id


def get_authors_number_of_series(author_id: int) -> int:
    """Return number of series connected to author_id

    Args:
        author_id (int): ID of the author

    Returns:
        int: Number of series written by the author
    """
    if author_id == None:
        return 0
    else:
        result = db.connection.execute(
            text(f"select count(*) from series where author_id = {author_id}"))
        rows = result.all().copy()
        return 0 if rows.__len__() == 0 else rows[0][0]


def get_series_author_id(series_id: int) -> Optional[int]:
    """Return ID of the author of series_id

    Args:
        series_id (int): ID of the series

    Returns:
        Optional[int]: ID of the author
    """
    result = db.connection.execute(
        text(f"select author_id from series where series_id = {series_id}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_series_name(series_id: int) -> Optional[str]:
    """Return series name

    Args:
        series_id (int): ID of the series

    Returns:
        Optional[str]: Name of the series
    """
    result = db.connection.execute(
        text(f"select name from series where series_id = {series_id}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_series_number_of_books(series_id: int) -> int:
    """Return the number of books connected to series_id

    Args:
        series_id (int): ID of the series

    Returns:
        int: Number of books in the series
    """
    if series_id == None:
        return 0
    else:
        result = db.connection.execute(
            text(f"select count(*) from books where series_id = {series_id}"))
        rows = result.all().copy()
        return 0 if rows.__len__() == 0 else rows[0][0]


def update_authors_series(old_author_id: int, new_author_id: int):
    """Update all series from author's name connected to old_id to author's name connected to new_id

    Args:
        old_author_id (int): ID of new author's name
        new_author_id (int): ID of the series to be updated
    """
    db.connection.execute(text(
        f"update series set author_id = {new_author_id} where author_id = {old_author_id}"))


def update_series_author(series_id: int, author_id: int):
    """Update the author of the series

    Args:
        series_id (int): ID of the series to be updated
        author_id (int): ID of new author's name
    """
    db.connection.execute(
        text(f"update series set author_id = {author_id} where series_id = {series_id}"))


def update_series_name(series_id: int, new_name: str):
    """Update series name using series_id

    Args:
        series_id (int): ID of the series
        new_name (str): New name for the series
    """
    db.connection.execute(
        text(f"update series set name = \"{new_name}\" where series_id = {series_id}"))


def delete_series_id(series_id: int):
    """Delete series with provided id

    Args:
        series_id (int): ID of the series to delete
    """
    db.connection.execute(
        text(f"delete from series where series_id = {series_id}"))


def insert_book(isbn: int, series_id: int, series_index: float, title: str):
    """Add new book if it's not in the database yet

    Args:
        isbn (int): ISBN identifier
        series_id (int): ID of the series
        series_index (float): Book's position in the series
        title (str): Title of the book
    """
    if get_book_isbn(isbn) == None:
        query_builder = StringIO()
        query_builder.write(f"insert into books values ({isbn}, ")
        query_builder.write(
            f"{series_id}, " if series_id != None else "NULL, ")
        query_builder.write(
            f"{series_index:f}, " if series_index != None else "NULL, ")
        query_builder.write(f"\"{title}\")" if title != None else "NULL)")
        db.connection.execute(text(query_builder.getvalue()))


def get_books_info(isbn: int, author: str, series: str, title: str) -> list[Book]:
    """Return a list of all data for books matching search parameters

    Args:
        isbn (int): ISBN identifier
        author (str): Name of the author
        series (str): Name of the series
        title (str): Title of the book

    Returns:
        list[Book]: List of Book objects containing data matching search parameters
    """
    list_of_books = []
    result = db.connection.execute(text(
        f"select b.isbn, a.name as 'author', s.name as 'series', b.series_index as 'index', b.title, released, finished, chapters, pages, speed, time from statistics left join books as b using (isbn) left join series as s using (series_id) left join authors as a using (author_id) where b.isbn like '%{isbn}%' and a.name like '%{author}%' and s.name like '%{series}%' and b.title like '%{title}%' order by released"))
    rows = result.all().copy()
    if rows.__len__() > 0:
        for row in rows:
            book = Book(isbn=row[0],
                        author_name=row[1],
                        series_name=row[2],
                        series_index=row[3],
                        title=row[4],
                        released=row[5],
                        finished=row[6],
                        chapters=row[7],
                        pages=row[8],
                        speed=row[9],
                        time=row[10])
            list_of_books.append(book)
    return list_of_books


def get_book_isbn(isbn: int) -> Optional[int]:
    """Check if a book identified by ISBN is in the books table

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[int]: Searched ISBN number or None if ISBN is not found in books table
    """
    if isbn == None or isbn == '':
        return None
    else:
        result = db.connection.execute(
            text(f"select * from books where isbn = {isbn}"))
        rows = result.all().copy()
        if rows.__len__() == 0:
            return None
        else:
            return rows[0][0]


def get_book_series_id(isbn: int) -> Optional[int]:
    """Return series_id connected to provided ISBN

    Args:
        isbn (int): ID of the book 

    Returns:
        Optional[int]: ID of the series
    """
    result = db.connection.execute(
        text(f"select series_id from books where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_book_series_index(isbn: int) -> Optional[int]:
    """Return series_index connected to provided ISBN

    Args:
        isbn (int): ID of the book 

    Returns:
        Optional[int]: Index in the series
    """
    result = db.connection.execute(
        text(f"select series_index from books where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_book_title(isbn: int) -> Optional[str]:
    """Return title of the book

    Args:
        isbn (int): ID of the book 

    Returns:
        Optional[int]: Title of the book
    """
    result = db.connection.execute(
        text(f"select title from books where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def update_book_isbn(old_isbn: int, new_isbn: int):
    """Update book's ISBN

    Args:
        old_isbn (int): Current ISBN
        new_isbn (int): New ISBN for the book
    """
    if get_book_isbn(new_isbn) == None:
        db.connection.execute(
            text(f"update books set isbn = {new_isbn} where isbn = {old_isbn}"))


def update_book_series(isbn: int, series_name: str, author_name: str):
    """Update book's series

    Args:
        isbn (int): Book's ISBN
        series_name (str): Name of the series to find the ID
        author_name (str): Author's name
    """
    author_id = get_author_id(author_name)
    if author_id == None:
        insert_author(author_name)
        author_id = get_author_id(author_name)
    series_id = get_series_id(series_name, author_id)
    if series_id == None:
        insert_series(author_id, series_name)
        series_id = get_series_id(series_name, author_id)
    db.connection.execute(
        text(f"update books set series_id = {series_id} where isbn = {isbn}"))


def update_book_series_index(isbn: int, series_index: int):
    """Update book's index in the series

    Args:
        isbn (int): Book's ISBN
        series_index (int): New series index for the book
    """
    db.connection.execute(
        text(f"update books set series_index = {series_index} where isbn = {isbn}"))


def update_book_title(isbn: int, title: str):
    """Update book's title

    Args:
        isbn (int): Book's ISBN
        title (str): New title for the book
    """
    db.connection.execute(
        text(f"update books set title = \"{title}\" where isbn = {isbn}"))


def delete_book_isbn(isbn: int):
    """Delete book with provided isbn

    Args:
        series_id (int): ISBN of the book to delete
    """
    db.connection.execute(text(f"delete from books where isbn = {isbn}"))


def insert_statistics(isbn: int, chapters: Optional[int] = None, pages: Optional[int] = None, released: Optional[str] = None, finished: Optional[str] = None, speed: Optional[int] = None, time: Optional[float] = None):
    """Add book's statistics if they're not in the database yet

    Args:
        isbn (int): ISBN identifier
        chapters (Optional[int], optional): Number of chapters. Defaults to None.
        pages (Optional[int], optional): Number of pages. Defaults to None.
        released (Optional[str], optional): Date the book was released. Defaults to None.
        finished (Optional[str], optional): Date the book was read. Defaults to None.
        speed (Optional[int], optional): Number of words per minute achieved when reading the book. Defaults to None.
        time (Optional[float], optional): Hours taken to finish reading the book. Defaults to None.
    """
    id = get_statistics_isbn(isbn)
    if id == None:
        query_builder = StringIO()
        query_builder.write(f"insert into statistics values ({isbn}, ")
        query_builder.write(f"{chapters}, " if chapters != None else "NULL, ")
        query_builder.write(f"{pages}, " if pages != None else "NULL, ")
        query_builder.write(
            f"\"{released}\", " if released != None else "NULL, ")
        query_builder.write(
            f"\"{finished}\", " if finished != None else "NULL, ")
        query_builder.write(f"{speed}, " if speed != None else "NULL, ")
        query_builder.write(f"{time})" if time != None else "NULL)")
        db.connection.execute(text(f"{query_builder.getvalue()}"))


def get_statistics_isbn(isbn: int) -> Optional[int]:
    """Check if a book identified by ISBN is in the statistics table

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[int]: Searched ISBN number or None if ISBN is not found in statistics table
    """
    if isbn == None or isbn == '':
        return None
    else:
        result = db.connection.execute(
            text(f"select isbn from statistics where isbn = {isbn}"))
        rows = result.all().copy()
        if rows.__len__() == 0:
            return None
        else:
            return rows[0][0]


def get_statistics_chapters(isbn: int) -> Optional[int]:
    """Get number of chapters in a book identified by ISBN

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[int]: Number of chapters in a book
    """
    result = db.connection.execute(
        text(f"select chapters from statistics where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_statistics_pages(isbn: int) -> Optional[int]:
    """Get number of pages in a book identified by ISBN

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[int]: Number of pages in a book
    """
    result = db.connection.execute(
        text(f"select pages from statistics where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_statistics_released(isbn: int) -> Optional[str]:
    """Get a date when a book was released

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[str]: Date when a book was released
    """
    result = db.connection.execute(
        text(f"select released from statistics where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_statistics_finished(isbn: int) -> Optional[str]:
    """Get a date when book was finished

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[str]: Date when a book was finished
    """
    result = db.connection.execute(
        text(f"select finished from statistics where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_statistics_speed(isbn: int) -> Optional[int]:
    """Get a number of words per minute achieved while reading

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[int]: Average words/minute achieved while reading
    """
    result = db.connection.execute(
        text(f"select speed from statistics where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def get_statistics_time(isbn: int) -> Optional[float]:
    """Get number of hours needed to read a book

    Args:
        isbn (int): ISBN number of the book

    Returns:
        Optional[float]: Number of hours needed to finish a book
    """
    result = db.connection.execute(
        text(f"select time from statistics where isbn = {isbn}"))
    rows = result.all().copy()
    if rows.__len__() == 0:
        return None
    else:
        return rows[0][0]


def update_statistics_isbn(old_isbn: int, new_isbn: int):
    """Update book's ISBN

    Args:
        old_isbn (int): Current ISBN
        new_isbn (int): New ISBN for the book
    """
    if get_statistics_isbn(new_isbn) == None:
        db.connection.execute(
            text(f"update statistics set isbn = {new_isbn} where isbn = {old_isbn}"))


def update_statistics_chapters(isbn: int, chapters: int):
    """Update book's number of chapters

    Args:
        isbn (int): Book's ISBN
        chapters (int): New number of chapters
    """
    db.connection.execute(
        text(f"update statistics set chapters = {chapters} where isbn = {isbn}"))


def update_statistics_pages(isbn: int, pages: int):
    """Update book's number of pages

    Args:
        isbn (int): Book's ISBN
        pages (int): New number of pages
    """
    db.connection.execute(
        text(f"update statistics set pages = {pages} where isbn = {isbn}"))


def update_statistics_released(isbn: int, released: str):
    """Update book's release date

    Args:
        isbn (int): Book's ISBN
        released (str): New release date
    """
    db.connection.execute(
        text(f"update statistics set released = \"{released}\" where isbn = {isbn}"))


def update_statistics_finished(isbn: int, finished: str):
    """Update book's finish date

    Args:
        isbn (int): Book's ISBN
        finished (str): New finish date
    """
    db.connection.execute(
        text(f"update statistics set finished = \"{finished}\" where isbn = {isbn}"))


def update_statistics_speed(isbn: int, speed: int):
    """Update book's speed [w/m]

    Args:
        isbn (int): Book's ISBN
        speed (int): New speed for the book
    """
    db.connection.execute(
        text(f"update statistics set speed = {speed} where isbn = {isbn}"))


def update_statistics_time(isbn: int, time: float):
    """Update book's reading time

    Args:
        isbn (int): Book's ISBN
        time (float): New time
    """
    db.connection.execute(
        text(f"update statistics set time = {time} where isbn = {isbn}"))


def delete_statistics_isbn(isbn: int):
    """Delete statistics with provided isbn

    Args:
        series_id (int): ISBN of the statistics to delete
    """
    db.connection.execute(text(f"delete from statistics where isbn = {isbn}"))
