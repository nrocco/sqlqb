import io


class Insert:
    def __init__(self):
        self.__table: str | None = None
        self.__values: list[dict] = []

    def Into(self, table: str) -> "Insert":
        if not table or not table.strip():
            raise ValueError("error: table name must not be empty")
        self.__table = table
        return self

    def Values(self, **kwargs) -> "Insert":
        if not kwargs:
            raise ValueError("error: specify at least one column value")
        self.__values.append(kwargs)
        return self

    @property
    def params(self) -> list:
        return self.__values

    @property
    def sql(self) -> str:
        if not self.__table:
            raise ValueError("error: no table specified")
        if not self.__values:
            raise ValueError("error: no values specified")
        columns = self.__values[0].keys()
        sql = io.StringIO()
        sql.write("INSERT INTO ")
        sql.write(self.__table)
        sql.write(" (")
        sql.write(", ".join(columns))
        sql.write(") VALUES (")
        sql.write(", ".join([f":{column}" for column in columns]))  # TODO this assumes :style parameters
        sql.write(")")
        return sql.getvalue()

    def __str__(self) -> str:
        return self.sql
