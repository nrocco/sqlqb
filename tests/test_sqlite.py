import pytest

from sqlqb import sqlite


@pytest.fixture
def conn():
    c = sqlite.connect(":memory:")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    c.executemany("INSERT INTO users VALUES (?, ?, ?)", [(1, "Alice", 30), (2, "Bob", 17), (3, "Carol", 25)])
    c.commit()
    return c


def test_connect_returns_connection(conn):
    assert isinstance(conn, sqlite.Connection)


def test_fetchall(conn):
    rows = conn.Select("id", "name").From("users").fetchall()
    assert rows == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Carol"}]


def test_fetchone(conn):
    row = conn.Select("name").From("users").Where("id = ?", 1).fetchone()
    assert row == {"name": "Alice"}


def test_where_with_param(conn):
    rows = conn.Select("name").From("users").Where("age >= ?", 18).fetchall()
    assert rows == [{"name": "Alice"}, {"name": "Carol"}]


def test_execute_returns_cursor(conn):
    cursor = conn.Select("*").From("users").execute()
    assert cursor.fetchone() == {"id": 1, "name": "Alice", "age": 30}


def test_chaining(conn):
    rows = (
        conn.Select("name")
        .From("users")
        .Where("age >= ?", 18)
        .OrderBy("name")
        .fetchall()
    )
    assert rows == [{"name": "Alice"}, {"name": "Carol"}]


def test_limit(conn):
    rows = conn.Select("id").From("users").Limit(2).fetchall()
    assert rows == [{"id": 1}, {"id": 2}]
