import io


class Delete:
    def __init__(self):
        self.__table: str | None = None
        self.__wheres: list[str] = []
        self.__params: list = []
        self.__named_params: dict = {}
        self.__limit: int | None = None

    def From(self, table: str) -> "Delete":
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        return self

    def Where(self, condition: str, *args, **kwargs) -> "Delete":
        if args and kwargs:
            raise ValueError("error: cannot mix positional and named params")
        if args and self.__named_params:
            raise ValueError("error: cannot mix positional and named params")
        if kwargs and self.__params:
            raise ValueError("error: cannot mix positional and named params")
        self.__wheres.append(condition)
        if kwargs:
            self.__named_params.update(kwargs)
        else:
            self.__params += list(args)
        return self

    def Limit(self, limit: int) -> "Delete":
        self.__limit = limit
        return self

    @property
    def params(self) -> list | dict:
        if self.__named_params:
            return self.__named_params
        return self.__params

    @property
    def sql(self) -> str:
        if not self.__table:
            raise ValueError("error: no table specified")
        sql = io.StringIO()
        sql.write("DELETE FROM ")
        sql.write(self.__table)
        if self.__wheres:
            sql.write(" WHERE ")
            sql.write(" AND ".join(self.__wheres))
        if self.__limit is not None:
            sql.write(f" LIMIT {self.__limit}")
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
