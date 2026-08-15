import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection as _SAConnection
from sqlalchemy.engine import Engine as _SAEngine
from sqlalchemy.pool import StaticPool

from sqlqb.sqlalchemy import Connection, Engine, create_engine


@pytest.fixture(scope="module")
def engine():
    e = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with e.connect() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"))
        conn.Insert().Into("users").Values(id=1, name="Alice", age=30).execute()
        conn.Insert().Into("users").Values(id=2, name="Bob", age=17).execute()
        conn.Insert().Into("users").Values(id=3, name="Carol", age=25).execute()
        conn.commit()
    return e


@pytest.fixture
def conn(engine):
    with engine.connect() as c:
        yield c
        c.rollback()


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class TestEngine:
    def test_create_engine_returns_engine_subclass(self):
        e = create_engine("sqlite:///:memory:")
        assert isinstance(e, Engine)
        assert isinstance(e, _SAEngine)

    def test_connect_returns_connection_subclass(self, engine):
        with engine.connect() as conn:
            assert isinstance(conn, Connection)
            assert isinstance(conn, _SAConnection)

    def test_connect_as_context_manager(self, engine):
        with engine.connect() as conn:
            assert conn is not None

    def test_connect_without_context_manager(self, engine):
        conn = engine.connect()
        assert isinstance(conn, Connection)
        conn.close()

    def test_engine_dialect_accessible(self):
        e = create_engine("sqlite:///:memory:")
        assert e.dialect.name == "sqlite"

    def test_engine_dispose(self):
        e = create_engine("sqlite:///:memory:")
        e.dispose()


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------


class TestConnection:
    def test_sa_methods_are_accessible(self, conn):
        assert callable(conn.commit)
        assert callable(conn.rollback)
        assert callable(conn.close)
        assert callable(conn.execute)

    def test_select_returns_select_instance(self, conn):
        from sqlqb.sqlalchemy import Select

        assert isinstance(conn.Select("id"), Select)

    def test_insert_returns_insert_instance(self, conn):
        from sqlqb.sqlalchemy import Insert

        assert isinstance(conn.Insert(), Insert)

    def test_update_returns_update_instance(self, conn):
        from sqlqb.sqlalchemy import Update

        assert isinstance(conn.Update("users"), Update)

    def test_delete_returns_delete_instance(self, conn):
        from sqlqb.sqlalchemy import Delete

        assert isinstance(conn.Delete(), Delete)


# ---------------------------------------------------------------------------
# Select
# ---------------------------------------------------------------------------


class TestSelect:
    def test_fetchall(self, conn):
        rows = conn.Select("id", "name").From("users").fetchall()
        assert rows == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Carol"}]

    def test_fetchone(self, conn):
        row = conn.Select("name").From("users").Where("id = :id", id=1).fetchone()
        assert row == {"name": "Alice"}

    def test_fetchone_returns_none_when_no_row(self, conn):
        row = conn.Select("name").From("users").Where("id = :id", id=999).fetchone()
        assert row is None

    def test_fetchall_returns_empty_list(self, conn):
        rows = conn.Select("name").From("users").Where("id = :id", id=999).fetchall()
        assert rows == []

    def test_where_single_param(self, conn):
        rows = conn.Select("name").From("users").Where("age >= :age", age=18).fetchall()
        assert rows == [{"name": "Alice"}, {"name": "Carol"}]

    def test_where_multiple_params(self, conn):
        rows = conn.Select("name").From("users").Where("age >= :min_age", min_age=18).Where("age <= :max_age", max_age=29).fetchall()
        assert rows == [{"name": "Carol"}]

    def test_order_by_asc(self, conn):
        rows = conn.Select("name").From("users").OrderBy("name").fetchall()
        assert rows == [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}]

    def test_order_by_desc(self, conn):
        rows = conn.Select("name").From("users").OrderBy("age", "DESC").fetchall()
        assert rows == [{"name": "Alice"}, {"name": "Carol"}, {"name": "Bob"}]

    def test_limit(self, conn):
        rows = conn.Select("id").From("users").Limit(2).fetchall()
        assert rows == [{"id": 1}, {"id": 2}]

    def test_execute_returns_sa_result(self, conn):
        result = conn.Select("id", "name").From("users").execute()
        rows = [dict(r) for r in result.mappings()]
        assert rows == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Carol"}]

    def test_fetchall_returns_plain_dicts(self, conn):
        rows = conn.Select("id").From("users").Limit(1).fetchall()
        assert type(rows[0]) is dict

    def test_fetchone_returns_plain_dict(self, conn):
        row = conn.Select("id").From("users").Where("id = :id", id=1).fetchone()
        assert type(row) is dict


# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------


class TestInsert:
    def test_execute_returns_rowcount(self, conn):
        count = conn.Insert().Into("users").Values(id=4, name="Dave", age=40).execute()
        assert count == 1

    def test_inserted_row_is_queryable(self, conn):
        conn.Insert().Into("users").Values(id=4, name="Dave", age=40).execute()
        row = conn.Select("name").From("users").Where("id = :id", id=4).fetchone()
        assert row == {"name": "Dave"}

    def test_insert_multiple_rows(self, conn):
        count = conn.Insert().Into("users").Values(id=4, name="Dave", age=40).Values(id=5, name="Eve", age=22).execute()
        assert count == 2


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


class TestUpdate:
    def test_execute_returns_rowcount(self, conn):
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

    def test_update_no_where_affects_all(self, conn):
        count = conn.Update("users").Set(age=0).execute()
        assert count == 3

    def test_update_affects_correct_rows_only(self, conn):
        conn.Update("users").Set(age=99).Where("id = :id", id=1).execute()
        rows = conn.Select("id", "age").From("users").fetchall()
        assert rows == [{"id": 1, "age": 99}, {"id": 2, "age": 17}, {"id": 3, "age": 25}]


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


class TestDelete:
    def test_execute_returns_rowcount(self, conn):
        conn.Insert().Into("users").Values(id=4, name="Temp", age=1).execute()
        count = conn.Delete().From("users").Where("id = :id", id=4).execute()
        assert count == 1

    def test_deleted_row_is_gone(self, conn):
        conn.Insert().Into("users").Values(id=4, name="Temp", age=1).execute()
        conn.Delete().From("users").Where("id = :id", id=4).execute()
        row = conn.Select("*").From("users").Where("id = :id", id=4).fetchone()
        assert row is None

    def test_delete_no_where_clears_table(self, conn):
        count = conn.Delete().From("users").execute()
        assert count == 3
        rows = conn.Select("*").From("users").fetchall()
        assert rows == []
