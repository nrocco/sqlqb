import sqlite3

from sqlqb import Select as _Select
from sqlqb import Insert as _Insert
from sqlqb import Update as _Update
from sqlqb import Delete as _Delete


class Select(_Select):
    def __init__(self, connection, *args):
        super().__init__(*args)
        self.__connection = connection

    def execute(self) -> sqlite3.Cursor:
        return self.__connection.execute(self.sql, self.params)

    def fetchone(self):
        return self.execute().fetchone()

    def fetchall(self) -> list:
        return self.execute().fetchall()


class Insert(_Insert):
    def __init__(self, connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(self.sql, self.params).rowcount


class Update(_Update):
    def __init__(self, connection, table: str):
        super().__init__(table)
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(self.sql, self.params).rowcount


class Delete(_Delete):
    def __init__(self, connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(self.sql, self.params).rowcount


class Connection(sqlite3.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))

    def Select(self, *args, **kwargs) -> Select:
        return Select(self, *args, **kwargs)

    def Insert(self) -> Insert:
        return Insert(self)

    def Delete(self) -> Delete:
        return Delete(self)

    def Update(self, table: str) -> Update:
        return Update(self, table)


def connect(database, **kwargs) -> Connection:
    return sqlite3.connect(database, factory=Connection, **kwargs)
