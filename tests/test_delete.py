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
            _ = Delete().sql

    def test_empty_table_raises(self):
        with pytest.raises(ValueError):
            _ = Delete().From("").sql

    def test_blank_table_raises(self):
        with pytest.raises(ValueError):
            _ = Delete().From("   ").sql

    def test_params_empty_by_default(self):
        q = Delete().From("users")
        assert q.params == {}


class TestDeleteWhere:
    def test_single_where(self):
        q = Delete().From("users").Where("id = :id", id=1)
        assert q.sql == "DELETE FROM users WHERE id = :id"
        assert q.params == {"id": 1}

    def test_multiple_wheres_joined_with_and(self):
        q = Delete().From("users").Where("active = :active", active=False).Where("role = :role", role="guest")
        assert q.sql == "DELETE FROM users WHERE active = :active AND role = :role"
        assert q.params == {"active": False, "role": "guest"}

    def test_where_no_params(self):
        q = Delete().From("sessions").Where("expired_at IS NOT NULL")
        assert q.sql == "DELETE FROM sessions WHERE expired_at IS NOT NULL"
        assert q.params == {}

    def test_no_where_absent(self):
        q = Delete().From("users")
        assert "WHERE" not in q.sql


class TestDeleteChaining:
    def test_method_chaining_returns_delete(self):
        q = Delete()
        assert q.From("t") is q
        assert q.Where("1=1") is q

    def test_full_query(self):
        q = Delete().From("logs").Where("level = :level", level="debug")
        assert q.sql == "DELETE FROM logs WHERE level = :level"
        assert q.params == {"level": "debug"}
