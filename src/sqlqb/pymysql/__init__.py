from pymysql.connections import Connection as _Connection
from pymysql.cursors import DictCursor

from sqlqb import Select as _Select
from sqlqb import Insert as _Insert
from sqlqb import Update as _Update
from sqlqb import Delete as _Delete


class Select(_Select):
    def __init__(self, connection, *args):
        super().__init__(*args)
        self.__connection = connection

    def execute(self):
        cursor = self.__connection.cursor()
        cursor.execute(self.sql, self.params)
        return cursor

    def fetchone(self):
        with self.__connection.cursor() as cursor:
            cursor.execute(self.sql, self.params)
            result = cursor.fetchone()
        return result

    def fetchall(self):
        with self.__connection.cursor() as cursor:
            cursor.execute(self.sql, self.params)
            result = cursor.fetchall()
        return result


class Insert(_Insert):
    def __init__(self, connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        with self.__connection.cursor() as cursor:
            cursor.execute(self.sql, self.params)
            return cursor.rowcount


class Update(_Update):
    def __init__(self, connection, table: str):
        super().__init__(table)
        self.__connection = connection

    def execute(self) -> int:
        with self.__connection.cursor() as cursor:
            cursor.execute(self.sql, self.params)
            return cursor.rowcount


class Delete(_Delete):
    def __init__(self, connection):
        super().__init__()
        self.__connection = connection

    def execute(self) -> int:
        with self.__connection.cursor() as cursor:
            cursor.execute(self.sql, self.params)
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

    def Delete(self) -> Delete:
        return Delete(self)

    def Update(self, table: str) -> Update:
        return Update(self, table)
