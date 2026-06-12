import io


class Select:
    def __init__(self, *args):
        self.__columns = list(args)
        self.__table = None
        self.__wheres = []
        self.__params = []
        self.__joins = []
        self.__orderby = []
        self.__groupby = []
        self.__limit = None
        self.__offset = None

    def Columns(self, *columns) -> "Select":
        self.__columns = list(columns)
        return self

    def From(self, table: str) -> "Select":
        self.__table = table
        return self

    def Join(self, join: str, *args) -> "Select":
        self.__joins.append(join)
        self.__params += args
        return self

    def Where(self, condition: str, *args) -> "Select":
        self.__wheres.append(condition)
        self.__params += args
        return self

    def OrderBy(self, column: str, direction="ASC") -> "Select":
        self.__orderby.append((column, direction))
        return self

    def GroupBy(self, *columns) -> "Select":
        self.__groupby += columns
        return self

    def Limit(self, limit: int) -> "Select":
        self.__limit = limit
        return self

    def Offset(self, offset: int) -> "Select":
        self.__offset = offset
        return self

    @property
    def params(self) -> list:
        return self.__params

    @property
    def sql(self) -> str:
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
