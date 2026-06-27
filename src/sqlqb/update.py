import io


class Update:
    def __init__(self, table: str):
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        self.__sets: dict[str, object] = {}
        self.__wheres: list[str] = []
        self.__params: dict[str, object] = {}

    def Set(self, **kwargs) -> "Update":
        if not kwargs:
            raise ValueError("error: specify at least one column value")
        self.__sets.update(kwargs)
        return self

    def Where(self, condition: str, **kwargs) -> "Update":
        self.__wheres.append(condition)
        self.__params.update(kwargs)
        return self

    @property
    def params(self) -> dict:
        return self.__sets | self.__params

    @property
    def sql(self) -> str:
        if not self.__sets:
            raise ValueError("error: no SET values specified")
        sql = io.StringIO()
        sql.write("UPDATE ")
        sql.write(self.__table)
        sql.write(" SET ")
        sql.write(", ".join([f"{col} = :{col}" for col in self.__sets]))
        if self.__wheres:
            sql.write(" WHERE ")
            sql.write(" AND ".join(self.__wheres))
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
