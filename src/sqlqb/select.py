import io


class Select:
    def __init__(self, *args: str):
        self.__columns: tuple[str] = args
        self.__table: str | None = None
        self.__joins: list[str] = []
        self.__wheres: list[str] = []
        self.__orderby: list[tuple[str, str]] = []
        self.__groupby: list[str] = []
        self.__limit: int | None = None
        self.__offset: int | None = None
        self.__params: dict = {}

    def Columns(self, *columns: str) -> "Select":
        if not columns:
            raise ValueError("error: specify at least one column")
        self.__columns = columns
        return self

    def From(self, table: str) -> "Select":
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        return self

    def Join(self, join: str, **kwargs) -> "Select":
        self.__joins.append(join)
        self.__params.update(kwargs)
        return self

    def Where(self, condition: str, **kwargs) -> "Select":
        self.__wheres.append(condition)
        self.__params.update(kwargs)
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
    def params(self) -> dict:
        return self.__params

    @property
    def sql(self) -> str:
        if not self.__table or not str(self.__table).strip():
            raise ValueError("error: table name must not be empty")
        sql = io.StringIO()
        sql.write("SELECT ")
        sql.write(", ".join(self.__columns or "*"))
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
