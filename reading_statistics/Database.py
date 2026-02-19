import sqlalchemy


class Database:
    location: str
    engine: sqlalchemy.Engine
    connection: sqlalchemy.Connection

    def commit():
        Database.connection.commit()

    def close():
        Database.connection.close()
