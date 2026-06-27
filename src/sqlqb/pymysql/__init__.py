import re

from pymysql.connections import Connection as _Connection
from pymysql.cursors import DictCursor

from sqlqb import Select as _Select
from sqlqb import Insert as _Insert
from sqlqb import Update as _Update
from sqlqb import Delete as _Delete


def _to_pymysql(sql: str, params: list | dict) -> tuple[str, list | dict]:
    """Convert :name placeholders to %(name)s style for PyMySQL when params is a dict."""
    if isinstance(params, dict):
        sql = re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)", r"%(\1)s", sql)
    return sql, params


class Select(_Select):
    def __init__(self, connection: _Connection, *args):
        super().__init__(*args)
        self.__connection = connection

    def execute(self):
        sql, params = _to_pymysql(self.sql, self.params)
        cursor = self.__connection.cursor()
        cursor.execute(sql, params)
        return cursor

    def fetchone(self):
        sql, params = _to_pymysql(self.sql, self.params)
        with self.__connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
        return result

    def fetchall(self):
        sql, params = _to_pymysql(self.sql, self.params)
        with self.__connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
        return result


class Insert(_Insert):
    def __init__(self, connection: _Connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        sql, params = _to_pymysql(self.sql, self.params)
        with self.__connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount


class Update(_Update):
    def __init__(self, connection: _Connection, table: str):
        super().__init__(table)
        self.__connection = connection

    def execute(self) -> int:
        sql, params = _to_pymysql(self.sql, self.params)
        with self.__connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount


class Delete(_Delete):
    def __init__(self, connection: _Connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        sql, params = _to_pymysql(self.sql, self.params)
        with self.__connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount


class Connection(_Connection):
    def __init__(self, *args, **kwargs):
        if "cursorclass" not in kwargs:
            kwargs["cursorclass"] = DictCursor
        super().__init__(*args, **kwargs)

    def Select(self, *args, **kwargs) -> Select:
        return Select(self, *args, **kwargs)

    def Insert(self) -> Insert:
        return Insert(self)

    def Update(self, table: str) -> Update:
        return Update(self, table)

    def Delete(self) -> Delete:
        return Delete(self)


connect = Connection
