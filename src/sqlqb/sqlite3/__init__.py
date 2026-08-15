from sqlite3 import Connection as _Connection
from sqlite3 import Cursor as _Cursor
from sqlite3 import connect as _connect

from sqlqb import Delete as _Delete
from sqlqb import Insert as _Insert
from sqlqb import Select as _Select
from sqlqb import Update as _Update


class Select(_Select):
    def __init__(self, connection: _Connection, *args):
        super().__init__(*args)
        self.__connection = connection

    def execute(self) -> _Cursor:
        return self.__connection.execute(self.sql, self.params)

    def fetchone(self):
        return self.execute().fetchone()

    def fetchall(self) -> list:
        return self.execute().fetchall()


class Insert(_Insert):
    def __init__(self, connection: _Connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        if len(self.params) == 1:
            return self.__connection.execute(self.sql, self.params[0]).rowcount
        return self.__connection.executemany(self.sql, self.params).rowcount

    def executemany(self) -> int:
        return self.execute()


class Update(_Update):
    def __init__(self, connection: _Connection, table: str):
        super().__init__(table)
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(self.sql, self.params).rowcount


class Delete(_Delete):
    def __init__(self, connection: _Connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(self.sql, self.params).rowcount


class Connection(_Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))

    def Select(self, *args, **kwargs) -> Select:
        return Select(self, *args, **kwargs)

    def Insert(self) -> Insert:
        return Insert(self)

    def Update(self, table: str) -> Update:
        return Update(self, table)

    def Delete(self) -> Delete:
        return Delete(self)


def connect(database, **kwargs) -> Connection:
    return _connect(database, factory=Connection, **kwargs)
