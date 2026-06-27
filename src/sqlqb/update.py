import io


class Update:
    def __init__(self, table: str):
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        self.__sets: dict[str, object] = {}
        self.__wheres: list[str] = []
        self.__where_params: list = []
        self.__where_named_params: dict = {}
        self.__limit: int | None = None

    def Set(self, **kwargs) -> "Update":
        if not kwargs:
            raise ValueError("error: specify at least one column value")
        self.__sets.update(kwargs)
        return self

    def Where(self, condition: str, *args, **kwargs) -> "Update":
        if args and kwargs:
            raise ValueError("error: cannot mix positional and named params")
        if args and self.__where_named_params:
            raise ValueError("error: cannot mix positional and named params")
        if kwargs and self.__where_params:
            raise ValueError("error: cannot mix positional and named params")
        self.__wheres.append(condition)
        if kwargs:
            self.__where_named_params.update(kwargs)
        else:
            self.__where_params += list(args)
        return self

    def Limit(self, limit: int) -> "Update":
        self.__limit = limit
        return self

    @property
    def params(self) -> list | dict:
        if not self.__sets:
            return []
        if self.__where_named_params:
            named = dict(self.__sets)
            named.update(self.__where_named_params)
            return named
        return list(self.__sets.values()) + self.__where_params

    @property
    def sql(self) -> str:
        if not self.__sets:
            raise ValueError("error: no SET values specified")
        sql = io.StringIO()
        sql.write("UPDATE ")
        sql.write(self.__table)
        sql.write(" SET ")
        if self.__where_named_params:
            sql.write(", ".join([f"{col} = :{col}" for col in self.__sets]))
        else:
            sql.write(", ".join([f"{col} = ?" for col in self.__sets]))
        if self.__wheres:
            sql.write(" WHERE ")
            sql.write(" AND ".join(self.__wheres))
        if self.__limit is not None:
            sql.write(f" LIMIT {self.__limit}")
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
