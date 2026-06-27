import pytest
from unittest.mock import MagicMock, patch

from sqlqb import pymysql
from sqlqb.pymysql import Select, Insert, Update, Delete, Connection, _to_pymysql
from pymysql.cursors import DictCursor


@pytest.fixture
def mock_conn():
    """Mock pymysql connection whose cursor supports both direct use and context manager."""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = False
    return conn, cursor


@pytest.fixture
def connection():
    """pymysql.Connection instance with the pymysql parent __init__ patched out."""
    with patch.object(pymysql._Connection, "__init__", return_value=None):
        conn = pymysql.Connection.__new__(pymysql.Connection)
        yield conn


class TestSelect:
    def test_execute_returns_cursor(self, mock_conn):
        conn, cursor = mock_conn
        result = Select(conn, "id", "name").From("users").execute()
        assert result is cursor

    def test_execute_calls_cursor_execute_with_sql_and_params(self, mock_conn):
        conn, cursor = mock_conn
        q = Select(conn, "name").From("users").Where("id = :id", id=1)
        q.execute()
        expected_sql, expected_params = _to_pymysql(q.sql, q.params)
        cursor.execute.assert_called_once_with(expected_sql, expected_params)

    def test_execute_does_not_use_context_manager(self, mock_conn):
        conn, cursor = mock_conn
        Select(conn, "id").From("users").execute()
        cursor.__enter__.assert_not_called()

    def test_fetchone_returns_result(self, mock_conn):
        conn, cursor = mock_conn
        cursor.fetchone.return_value = {"id": 1, "name": "Alice"}
        result = Select(conn, "id", "name").From("users").Where("id = :id", id=1).fetchone()
        assert result == {"id": 1, "name": "Alice"}

    def test_fetchone_returns_none_when_no_row(self, mock_conn):
        conn, cursor = mock_conn
        cursor.fetchone.return_value = None
        result = Select(conn, "id").From("users").Where("id = :id", id=999).fetchone()
        assert result is None

    def test_fetchone_calls_cursor_execute(self, mock_conn):
        conn, cursor = mock_conn
        q = Select(conn, "name").From("users").Where("id = :id", id=1)
        q.fetchone()
        expected_sql, expected_params = _to_pymysql(q.sql, q.params)
        cursor.execute.assert_called_once_with(expected_sql, expected_params)

    def test_fetchone_uses_context_manager(self, mock_conn):
        conn, cursor = mock_conn
        Select(conn, "name").From("users").fetchone()
        cursor.__enter__.assert_called_once()

    def test_fetchall_returns_result(self, mock_conn):
        conn, cursor = mock_conn
        cursor.fetchall.return_value = [{"id": 1}, {"id": 2}]
        result = Select(conn, "id").From("users").fetchall()
        assert result == [{"id": 1}, {"id": 2}]

    def test_fetchall_returns_empty_list(self, mock_conn):
        conn, cursor = mock_conn
        cursor.fetchall.return_value = []
        result = Select(conn, "id").From("users").fetchall()
        assert result == []

    def test_fetchall_calls_cursor_execute(self, mock_conn):
        conn, cursor = mock_conn
        q = Select(conn, "id").From("users")
        q.fetchall()
        cursor.execute.assert_called_once_with(q.sql, q.params)

    def test_fetchall_uses_context_manager(self, mock_conn):
        conn, cursor = mock_conn
        Select(conn, "id").From("users").fetchall()
        cursor.__enter__.assert_called_once()

    def test_multiple_where_params_passed_correctly(self, mock_conn):
        conn, cursor = mock_conn
        q = Select(conn, "name").From("users").Where("age > :age", age=18).Where("active = :active", active=True)
        q.fetchall()
        expected_sql, expected_params = _to_pymysql(q.sql, q.params)
        cursor.execute.assert_called_once_with(expected_sql, expected_params)

    def test_chaining_with_order_and_limit(self, mock_conn):
        conn, cursor = mock_conn
        cursor.fetchall.return_value = [{"name": "Alice"}]
        result = Select(conn, "name").From("users").Where("age >= :age", age=18).OrderBy("name").Limit(1).fetchall()
        assert result == [{"name": "Alice"}]


class TestInsert:
    def test_execute_returns_rowcount(self, mock_conn):
        conn, cursor = mock_conn
        cursor.rowcount = 1
        count = Insert(conn).Into("users").Values(id=1, name="Alice").execute()
        assert count == 1

    def test_execute_calls_cursor_execute(self, mock_conn):
        conn, cursor = mock_conn
        q = Insert(conn).Into("users").Values(id=1, name="Alice")
        q.execute()
        cursor.execute.assert_called_once_with(q.sql, q.params)

    def test_execute_uses_context_manager(self, mock_conn):
        conn, cursor = mock_conn
        Insert(conn).Into("users").Values(id=1, name="Alice").execute()
        cursor.__enter__.assert_called_once()

    def test_execute_multiple_rows_rowcount(self, mock_conn):
        conn, cursor = mock_conn
        cursor.rowcount = 2
        count = Insert(conn).Into("users").Values(id=1, name="Alice").Values(id=2, name="Bob").execute()
        assert count == 2


class TestUpdate:
    def test_execute_returns_rowcount(self, mock_conn):
        conn, cursor = mock_conn
        cursor.rowcount = 1
        count = Update(conn, "users").Set(name="Alice").Where("id = :id", id=1).execute()
        assert count == 1

    def test_execute_calls_cursor_execute(self, mock_conn):
        conn, cursor = mock_conn
        q = Update(conn, "users").Set(name="Alice").Where("id = :id", id=1)
        q.execute()
        expected_sql, expected_params = _to_pymysql(q.sql, q.params)
        cursor.execute.assert_called_once_with(expected_sql, expected_params)

    def test_execute_uses_context_manager(self, mock_conn):
        conn, cursor = mock_conn
        Update(conn, "users").Set(name="Alice").execute()
        cursor.__enter__.assert_called_once()

    def test_execute_no_where_returns_affected_rowcount(self, mock_conn):
        conn, cursor = mock_conn
        cursor.rowcount = 5
        count = Update(conn, "users").Set(active=False).execute()
        assert count == 5

    def test_execute_multiple_set_columns(self, mock_conn):
        conn, cursor = mock_conn
        cursor.rowcount = 1
        q = Update(conn, "users").Set(name="Bob", age=20).Where("id = :id", id=2)
        count = q.execute()
        expected_sql, expected_params = _to_pymysql(q.sql, q.params)
        cursor.execute.assert_called_once_with(expected_sql, expected_params)
        assert count == 1


class TestDelete:
    def test_execute_returns_rowcount(self, mock_conn):
        conn, cursor = mock_conn
        cursor.rowcount = 1
        count = Delete(conn).From("users").Where("id = :id", id=1).execute()
        assert count == 1

    def test_execute_calls_cursor_execute(self, mock_conn):
        conn, cursor = mock_conn
        q = Delete(conn).From("users").Where("id = :id", id=1)
        q.execute()
        expected_sql, expected_params = _to_pymysql(q.sql, q.params)
        cursor.execute.assert_called_once_with(expected_sql, expected_params)

    def test_execute_uses_context_manager(self, mock_conn):
        conn, cursor = mock_conn
        Delete(conn).From("users").Where("id = :id", id=1).execute()
        cursor.__enter__.assert_called_once()

    def test_execute_no_where_returns_all_rowcount(self, mock_conn):
        conn, cursor = mock_conn
        cursor.rowcount = 3
        count = Delete(conn).From("users").execute()
        assert count == 3


class TestToPymysql:
    def test_dict_params_converts_placeholders(self):
        sql, params = _to_pymysql(
            "SELECT * FROM t WHERE id = :id AND name = :name",
            {"id": 1, "name": "Alice"},
        )
        assert sql == "SELECT * FROM t WHERE id = %(id)s AND name = %(name)s"
        assert params == {"id": 1, "name": "Alice"}

    def test_dict_params_single_placeholder(self):
        sql, params = _to_pymysql("DELETE FROM t WHERE id = :id", {"id": 42})
        assert sql == "DELETE FROM t WHERE id = %(id)s"
        assert params == {"id": 42}


class TestConnection:
    def test_default_cursorclass_is_dictcursor(self):
        with patch.object(pymysql._Connection, "__init__", return_value=None) as mock_init:
            Connection(host="localhost", user="root", password="secret", db="mydb")
            kwargs = mock_init.call_args[1]
            assert kwargs["cursorclass"] is DictCursor

    def test_custom_cursorclass_is_not_overridden(self):
        custom_cursor = MagicMock()
        with patch.object(pymysql._Connection, "__init__", return_value=None) as mock_init:
            Connection(host="localhost", cursorclass=custom_cursor)
            kwargs = mock_init.call_args[1]
            assert kwargs["cursorclass"] is custom_cursor

    def test_select_returns_select_instance(self, connection):
        result = connection.Select("id", "name")
        assert isinstance(result, Select)

    def test_insert_returns_insert_instance(self, connection):
        result = connection.Insert()
        assert isinstance(result, Insert)

    def test_delete_returns_delete_instance(self, connection):
        result = connection.Delete()
        assert isinstance(result, Delete)

    def test_update_returns_update_instance(self, connection):
        result = connection.Update("users")
        assert isinstance(result, Update)
