import io


class Select:
    def __init__(self, *args: str):
        self.__columns: list[str] = list(args)
        self.__table: str | None = None
        self.__wheres: list[str] = []
        self.__params: list = []
        self.__named_params: dict = {}
        self.__joins: list[str] = []
        self.__orderby: list[tuple[str, str]] = []
        self.__groupby: list[str] = []
        self.__limit: int | None = None
        self.__offset: int | None = None

    def Columns(self, *columns: str) -> "Select":
        if not columns:
            raise ValueError("error: specify at least one column")
        self.__columns = list(columns)
        return self

    def From(self, table: str) -> "Select":
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        return self

    def Join(self, join: str, *args, **kwargs) -> "Select":
        if args and kwargs:
            raise ValueError("error: cannot mix positional and named params")
        if args and self.__named_params:
            raise ValueError("error: cannot mix positional and named params")
        if kwargs and self.__params:
            raise ValueError("error: cannot mix positional and named params")
        self.__joins.append(join)
        if kwargs:
            self.__named_params.update(kwargs)
        else:
            self.__params += list(args)
        return self

    def Where(self, condition: str, *args, **kwargs) -> "Select":
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

    def OrderBy(self, column: str, direction: str = "ASC") -> "Select":
        if direction not in ("ASC", "DESC"):
            raise ValueError("error: invalid order by direction")
        self.__orderby.append((column, direction))
        return self

    def GroupBy(self, *columns: str) -> "Select":
        self.__groupby += columns
        return self

    def Limit(self, limit: int) -> "Select":
        self.__limit = limit
        return self

    def Offset(self, offset: int) -> "Select":
        self.__offset = offset
        return self

    @property
    def params(self) -> list | dict:
        if self.__named_params:
            return self.__named_params
        return self.__params

    @property
    def sql(self) -> str:
        sql = io.StringIO()
        sql.write("SELECT ")
        sql.write(", ".join(self.__columns or "*"))
        if self.__table:
            sql.write(" FROM ")
            sql.write(self.__table)
        if self.__joins:
            sql.write(" ")
            sql.write(" ".join(self.__joins))
        if self.__wheres:
            sql.write(" WHERE ")
            sql.write(" AND ".join(self.__wheres))
        if self.__groupby:
            sql.write(" GROUP BY ")
            sql.write(", ".join(self.__groupby))
        if self.__orderby:
            sql.write(" ORDER BY ")
            sql.write(", ".join([f"{column} {order}" for column, order in self.__orderby]))
        if self.__limit is not None:
            sql.write(f" LIMIT {self.__limit}")
        if self.__offset is not None:
            sql.write(f" OFFSET {self.__offset}")
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
