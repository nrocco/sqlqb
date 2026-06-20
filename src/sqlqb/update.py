import io


class Update:
    def __init__(self, table: str):
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        self.__sets: dict[str, object] = {}
        self.__wheres: list[str] = []
        self.__where_params: list = []
        self.__limit: int | None = None

    def Set(self, **kwargs) -> "Update":
        if not kwargs:
            raise ValueError("error: specify at least one column value")
        self.__sets.update(kwargs)
        return self

    def Where(self, condition: str, *args) -> "Update":
        self.__wheres.append(condition)
        self.__where_params += args
        return self

    def Limit(self, limit: int) -> "Update":
        self.__limit = limit
        return self

    @property
    def params(self) -> list:
        if not self.__sets:
            return []
        return list(self.__sets.values()) + self.__where_params

    @property
    def sql(self) -> str:
        if not self.__sets:
            raise ValueError("error: no SET values specified")
        sql = io.StringIO()
        sql.write("UPDATE ")
        sql.write(self.__table)
        sql.write(" SET ")
        sql.write(", ".join([f"{col} = ?" for col in self.__sets]))
        if self.__wheres:
            sql.write(" WHERE ")
            sql.write(" AND ".join(self.__wheres))
        if self.__limit is not None:
            sql.write(f" LIMIT {self.__limit}")
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
