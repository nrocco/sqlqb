import io


class Delete:
    def __init__(self):
        self.__table: str | None = None
        self.__wheres: list[str] = []
        self.__params: dict = {}

    def From(self, table: str) -> "Delete":
        self.__table = table
        return self

    def Where(self, condition: str, **kwargs) -> "Delete":
        self.__wheres.append(condition)
        self.__params.update(kwargs)
        return self

    @property
    def params(self) -> dict:
        return self.__params

    @property
    def sql(self) -> str:
        if not self.__table or not str(self.__table).strip():
            raise ValueError("error: table name must not be empty")
        sql = io.StringIO()
        sql.write("DELETE FROM ")
        sql.write(self.__table)
        if self.__wheres:
            sql.write(" WHERE ")
            sql.write(" AND ".join(self.__wheres))
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
