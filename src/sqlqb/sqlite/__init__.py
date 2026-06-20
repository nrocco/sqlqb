import sqlite3

from sqlqb import Select as _Select


class Select(_Select):
    def __init__(self, connection, *columns):
        super().__init__(*columns)
        self._connection = connection

    def execute(self) -> sqlite3.Cursor:
        return self._connection.execute(self.sql, self.params)

    def fetchone(self):
        return self.execute().fetchone()

    def fetchall(self) -> list:
        return self.execute().fetchall()


class Connection(sqlite3.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))

    def Select(self, *args, **kwargs) -> Select:
        return Select(self, *args, **kwargs)


def connect(database, **kwargs) -> Connection:
    return sqlite3.connect(database, factory=Connection, **kwargs)
