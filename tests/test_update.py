import pytest

from sqlqb import Update


class TestUpdateBasic:
    def test_single_column(self):
        q = Update("users").Set(name="Alice")
        assert q.sql == "UPDATE users SET name = ?"
        assert q.params == ["Alice"]

    def test_multiple_columns(self):
        q = Update("users").Set(name="Alice", active=True)
        assert q.sql == "UPDATE users SET name = ?, active = ?"
        assert q.params == ["Alice", True]

    def test_str_equals_sql(self):
        q = Update("users").Set(name="Alice")
        assert str(q) == q.sql

    def test_empty_table_raises(self):
        with pytest.raises(ValueError):
            Update("")

    def test_blank_table_raises(self):
        with pytest.raises(ValueError):
            Update("   ")

    def test_no_set_sql_raises(self):
        with pytest.raises(ValueError):
            Update("users").sql

    def test_empty_set_raises(self):
        with pytest.raises(ValueError):
            Update("users").Set()

    def test_params_empty_before_set(self):
        q = Update("users")
        assert q.params == []

    def test_chained_set_merges_columns(self):
        q = Update("users").Set(name="Alice").Set(active=False)
        assert "name = ?" in q.sql
        assert "active = ?" in q.sql
        assert q.params == ["Alice", False]

    def test_chained_set_overwrites_same_column(self):
        q = Update("users").Set(name="Alice").Set(name="Bob")
        assert q.params == ["Bob"]

    def test_various_value_types(self):
        q = Update("t").Set(x=42, flag=True, score=3.14, label=None)
        assert q.params == [42, True, 3.14, None]


class TestUpdateWhere:
    def test_single_where(self):
        q = Update("users").Set(active=False).Where("id = ?", 1)
        assert q.sql == "UPDATE users SET active = ? WHERE id = ?"
        assert q.params == [False, 1]

    def test_multiple_wheres_joined_with_and(self):
        q = Update("users").Set(role="guest").Where("active = ?", False).Where("role = ?", "admin")
        assert "WHERE active = ? AND role = ?" in q.sql
        assert q.params == ["guest", False, "admin"]

    def test_where_no_params(self):
        q = Update("sessions").Set(expired=True).Where("token IS NOT NULL")
        assert "WHERE token IS NOT NULL" in q.sql

    def test_set_params_before_where_params(self):
        q = Update("t").Set(x=1).Where("y = ?", 2)
        assert q.params == [1, 2]

    def test_no_where_absent(self):
        q = Update("users").Set(active=True)
        assert "WHERE" not in q.sql


class TestUpdateLimit:
    def test_limit(self):
        q = Update("logs").Set(processed=True).Limit(100)
        assert "LIMIT 100" in q.sql

    def test_no_limit_absent(self):
        q = Update("users").Set(active=True)
        assert "LIMIT" not in q.sql


class TestUpdateChaining:
    def test_method_chaining_returns_update(self):
        q = Update("t")
        assert q.Set(x=1) is q
        assert q.Where("1=1") is q
        assert q.Limit(5) is q

    def test_full_query(self):
        q = Update("users").Set(role="admin", active=True).Where("id = ?", 42).Limit(1)
        assert q.sql == "UPDATE users SET role = ?, active = ? WHERE id = ? LIMIT 1"
        assert q.params == ["admin", True, 42]
