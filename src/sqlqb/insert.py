import io


class Insert:
    def __init__(self):
        self.__table: str | None = None
        self.__rows: list[dict] = []

    def Into(self, table: str) -> "Insert":
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        return self

    def Values(self, **kwargs) -> "Insert":
        if not kwargs:
            raise ValueError("error: specify at least one column value")
        self.__rows.append(kwargs)
        return self

    @property
    def params(self) -> list:
        if not self.__rows:
            return []
        return [v for row in self.__rows for v in row.values()]

    @property
    def sql(self) -> str:
        if not self.__table:
            raise ValueError("error: no table specified")
        if not self.__rows:
            raise ValueError("error: no values specified")
        columns = list(self.__rows[0].keys())
        sql = io.StringIO()
        sql.write("INSERT INTO ")
        sql.write(self.__table)
        sql.write(" (")
        sql.write(", ".join(columns))
        sql.write(") VALUES ")
        placeholder = "(" + ", ".join(["?"] * len(columns)) + ")"
        sql.write(", ".join([placeholder] * len(self.__rows)))
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
