from pymysql.connections import Connection as _Connection
from pymysql.cursors import DictCursor

from sqlqb import Select as _Select


class Select(_Select):
    def __init__(self, connection, *args, **kwargs):
        self.__connection = connection
        super().__init__(*args, **kwargs)

    def fetchone(self, cursor=None):
        cursor = cursor or self.__connection.cursor()
        with cursor as cursor:
            cursor.execute(self.sql, self.params)
            result = cursor.fetchone()
        return result

    def fetchall(self, cursor=None):
        cursor = cursor or self.__connection.cursor()
        with cursor as cursor:
            cursor.execute(self.sql, self.params)
            result = cursor.fetchall()
        return result


class Connection(_Connection):
    def __init__(self, *args, **kwargs):
        if "cursorclass" not in kwargs:
            kwargs["cursorclass"] = DictCursor
        super().__init__(*args, **kwargs)

    def Select(self, *args, **kwargs):
        return Select(self, *args, **kwargs)
