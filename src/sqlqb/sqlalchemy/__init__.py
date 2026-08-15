from sqlalchemy import create_engine as _create_engine
from sqlalchemy import text
from sqlalchemy.engine import Connection as _Connection
from sqlalchemy.engine import Engine as _Engine

from sqlqb import Delete as _Delete
from sqlqb import Insert as _Insert
from sqlqb import Select as _Select
from sqlqb import Update as _Update


class Select(_Select):
    def __init__(self, connection: _Connection, *args):
        super().__init__(*args)
        self.__connection = connection

    def execute(self):
        return self.__connection.execute(text(self.sql), self.params)

    def fetchone(self):
        row = self.execute().mappings().fetchone()
        return dict(row) if row is not None else None

    def fetchall(self) -> list:
        return [dict(row) for row in self.execute().mappings()]


class Insert(_Insert):
    def __init__(self, connection: _Connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(text(self.sql), self.params).rowcount


class Update(_Update):
    def __init__(self, connection: _Connection, table: str):
        super().__init__(table)
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(text(self.sql), self.params).rowcount


class Delete(_Delete):
    def __init__(self, connection: _Connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        return self.__connection.execute(text(self.sql), self.params).rowcount


class Connection(_Connection):
    def Select(self, *args) -> Select:
        return Select(self, *args)

    def Insert(self) -> Insert:
        return Insert(self)

    def Update(self, table: str) -> Update:
        return Update(self, table)

    def Delete(self) -> Delete:
        return Delete(self)


class Engine(_Engine):
    def connect(self) -> Connection:
        conn = super().connect()
        conn.__class__ = Connection
        return conn


def create_engine(url: str, **kwargs) -> Engine:
    engine = _create_engine(url, **kwargs)
    engine.__class__ = Engine
    return engine
