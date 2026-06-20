import pytest

from sqlqb import Delete


class TestDeleteBasic:
    def test_delete_all(self):
        q = Delete().From("users")
        assert q.sql == "DELETE FROM users"

    def test_str_equals_sql(self):
        q = Delete().From("users")
        assert str(q) == q.sql

    def test_no_table_raises(self):
        with pytest.raises(ValueError):
            Delete().sql

    def test_empty_table_raises(self):
        with pytest.raises(ValueError):
            Delete().From("")

    def test_blank_table_raises(self):
        with pytest.raises(ValueError):
            Delete().From("   ")

    def test_params_empty_by_default(self):
        q = Delete().From("users")
        assert q.params == []


class TestDeleteWhere:
    def test_single_where(self):
        q = Delete().From("users").Where("id = ?", 1)
        assert q.sql == "DELETE FROM users WHERE id = ?"
        assert q.params == [1]

    def test_multiple_wheres_joined_with_and(self):
        q = Delete().From("users").Where("active = ?", False).Where("role = ?", "guest")
        assert q.sql == "DELETE FROM users WHERE active = ? AND role = ?"
        assert q.params == [False, "guest"]

    def test_where_no_params(self):
        q = Delete().From("sessions").Where("expired_at IS NOT NULL")
        assert q.sql == "DELETE FROM sessions WHERE expired_at IS NOT NULL"
        assert q.params == []

    def test_where_multiple_params(self):
        q = Delete().From("t").Where("a = ? AND b = ?", 1, 2)
        assert q.params == [1, 2]

    def test_no_where_absent(self):
        q = Delete().From("users")
        assert "WHERE" not in q.sql


class TestDeleteLimit:
    def test_limit(self):
        q = Delete().From("logs").Limit(100)
        assert "LIMIT 100" in q.sql

    def test_no_order_by_absent(self):
        q = Delete().From("users")
        assert "ORDER BY" not in q.sql

    def test_no_limit_absent(self):
        q = Delete().From("users")
        assert "LIMIT" not in q.sql


class TestDeleteChaining:
    def test_method_chaining_returns_delete(self):
        q = Delete()
        assert q.From("t") is q
        assert q.Where("1=1") is q
        assert q.Limit(5) is q

    def test_full_query(self):
        q = Delete().From("logs").Where("level = ?", "debug").Limit(500)
        assert q.sql == "DELETE FROM logs WHERE level = ? LIMIT 500"
        assert q.params == ["debug"]
