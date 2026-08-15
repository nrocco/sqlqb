import pytest

from sqlqb import sqlite3


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    c.executemany(
        "INSERT INTO users VALUES (:id, :name, :age)",
        [{"id": 1, "name": "Alice", "age": 30}, {"id": 2, "name": "Bob", "age": 17}, {"id": 3, "name": "Carol", "age": 25}],
    )
    c.commit()
    return c


class TestSelect:
    def test_fetchall(self, conn):
        rows = conn.Select("id", "name").From("users").fetchall()
        assert rows == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Carol"}]

    def test_fetchone(self, conn):
        row = conn.Select("name").From("users").Where("id = :id", id=1).fetchone()
        assert row == {"name": "Alice"}

    def test_where_with_param(self, conn):
        rows = conn.Select("name").From("users").Where("age >= :age", age=18).fetchall()
        assert rows == [{"name": "Alice"}, {"name": "Carol"}]

    def test_execute_returns_cursor(self, conn):
        cursor = conn.Select("*").From("users").execute()
        assert cursor.fetchone() == {"id": 1, "name": "Alice", "age": 30}

    def test_chaining(self, conn):
        rows = conn.Select("name").From("users").Where("age >= :age", age=18).OrderBy("name").fetchall()
        assert rows == [{"name": "Alice"}, {"name": "Carol"}]

    def test_limit(self, conn):
        rows = conn.Select("id").From("users").Limit(2).fetchall()
        assert rows == [{"id": 1}, {"id": 2}]


class TestInsert:
    def test_insert_returns_rowcount(self, conn):
        count = conn.Insert().Into("users").Values(id=4, name="Dave", age=40).execute()
        assert count == 1

    def test_insert_row_is_queryable(self, conn):
        conn.Insert().Into("users").Values(id=4, name="Dave", age=40).executemany()
        row = conn.Select("name").From("users").Where("id = :id", id=4).fetchone()
        assert row == {"name": "Dave"}

    def test_insert_multiple_rows(self, conn):
        count = conn.Insert().Into("users").Values(id=4, name="Dave", age=40).Values(id=5, name="Eve", age=22).execute()
        assert count == 2

    def test_insert_multiple_rows_are_queryable(self, conn):
        conn.Insert().Into("users").Values(id=4, name="Dave", age=40).Values(id=5, name="Eve", age=22).execute()
        rows = conn.Select("name").From("users").Where("id = :id", id=4).fetchall()
        assert rows == [{"name": "Dave"}]

    def test_executemany_all_rows_persisted(self, conn):
        conn.Insert().Into("users").Values(id=4, name="Dave", age=40).Values(id=5, name="Eve", age=22).Values(id=6, name="Frank", age=35).execute()
        rows = conn.Select("id", "name", "age").From("users").OrderBy("id").fetchall()
        assert {"id": 4, "name": "Dave", "age": 40} in rows
        assert {"id": 5, "name": "Eve", "age": 22} in rows
        assert {"id": 6, "name": "Frank", "age": 35} in rows


class TestUpdate:
    def test_update_returns_rowcount(self, conn):
        count = conn.Update("users").Set(name="Alicia").Where("id = :id", id=1).execute()
        assert count == 1

    def test_update_is_reflected(self, conn):
        conn.Update("users").Set(name="Alicia").Where("id = :id", id=1).execute()
        row = conn.Select("name").From("users").Where("id = :id", id=1).fetchone()
        assert row == {"name": "Alicia"}

    def test_update_multiple_columns(self, conn):
        conn.Update("users").Set(name="Bobby", age=18).Where("id = :id", id=2).execute()
        row = conn.Select("name", "age").From("users").Where("id = :id", id=2).fetchone()
        assert row == {"name": "Bobby", "age": 18}

    def test_update_affects_correct_rows_only(self, conn):
        conn.Update("users").Set(age=99).Where("id = :id", id=1).execute()
        rows = conn.Select("age").From("users").fetchall()
        assert rows == [{"age": 99}, {"age": 17}, {"age": 25}]

    def test_update_no_where_affects_all(self, conn):
        count = conn.Update("users").Set(age=0).execute()
        assert count == 3


class TestDelete:
    def test_delete_returns_rowcount(self, conn):
        count = conn.Delete().From("users").Where("id = :id", id=1).execute()
        assert count == 1

    def test_delete_row_is_gone(self, conn):
        conn.Delete().From("users").Where("id = :id", id=1).execute()
        row = conn.Select("*").From("users").Where("id = :id", id=1).fetchone()
        assert row is None

    def test_delete_no_where_clears_table(self, conn):
        count = conn.Delete().From("users").execute()
        assert count == 3
        rows = conn.Select("*").From("users").fetchall()
        assert rows == []
