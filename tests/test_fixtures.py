import pytest
from sqlalchemy import create_engine, text
from reading_statistics.Database import Database
from reading_statistics.sqlite import create_tables, load_library_from_json


@pytest.fixture(scope="function")
def test_no_db():
    db = Database
    db.location = "sqlite+pysqlite:///:memory:"
    db.engine = create_engine(db.location)
    db.connection = db.engine.connect()
    yield db.connection
    db.close()


@pytest.fixture(scope="function")
def test_empty_db():
    db = Database
    db.location = "sqlite+pysqlite:///:memory:"
    db.engine = create_engine(db.location)
    db.connection = db.engine.connect()
    create_tables()
    yield db.connection
    db.close()


@pytest.fixture(scope="function")
def test_db():
    db = Database
    db.location = "sqlite+pysqlite:///:memory:"
    db.engine = create_engine(db.location)
    db.connection = db.engine.connect()
    create_tables()
    load_library_from_json("./tests/test_library.json")
    yield db.connection
    db.close()
