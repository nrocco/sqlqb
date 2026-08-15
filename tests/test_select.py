import pytest

from sqlqb import Select


class TestSelectBasic:
    def test_simple_select_all(self):
        q = Select().From("users")
        assert q.sql == "SELECT * FROM users"

    def test_str_equals_sql(self):
        q = Select().From("users")
        assert str(q) == q.sql

    def test_columns_via_constructor(self):
        q = Select("id", "name").From("users")
        assert q.sql == "SELECT id, name FROM users"

    def test_single_column_via_constructor(self):
        q = Select("id").From("users")
        assert q.sql == "SELECT id FROM users"

    def test_columns_via_method(self):
        q = Select().Columns("id", "name").From("users")
        assert q.sql == "SELECT id, name FROM users"

    def test_columns_method_overrides_constructor(self):
        q = Select("a", "b").Columns("c", "d").From("users")
        assert q.sql == "SELECT c, d FROM users"

    def test_from_sets_table(self):
        q = Select("id").From("orders")
        assert "FROM orders" in q.sql

    def test_table_empty_raises(self):
        with pytest.raises(ValueError):
            _ = Select("1").sql

    def test_columns_empty_raises(self):
        with pytest.raises(ValueError):
            _ = Select().Columns()

    def test_from_empty_raises(self):
        with pytest.raises(ValueError):
            _ = Select().From("")

    def test_from_blank_raises(self):
        with pytest.raises(ValueError):
            _ = Select().From("   ")

    def test_method_chaining_returns_select(self):
        q = Select()
        assert q.From("t") is q
        assert q.Columns("a") is q
        assert q.Where("1=1") is q
        assert q.Join("JOIN foo ON foo.id = t.foo_id") is q
        assert q.OrderBy("id") is q
        assert q.GroupBy("id") is q
        assert q.Limit(10) is q
        assert q.Offset(5) is q


class TestWhere:
    def test_single_where(self):
        q = Select("id").From("users").Where("id = :id", id=1)
        assert q.sql == "SELECT id FROM users WHERE id = :id"
        assert q.params == {"id": 1}

    def test_multiple_wheres_joined_with_and(self):
        q = Select("id").From("users").Where("active = :active", active=True).Where("role = :role", role="admin")
        assert q.sql == "SELECT id FROM users WHERE active = :active AND role = :role"
        assert q.params == {"active": True, "role": "admin"}

    def test_where_no_params(self):
        q = Select("id").From("users").Where("deleted_at IS NULL")
        assert "WHERE deleted_at IS NULL" in q.sql
        assert q.params == {}

    def test_no_where_clause_absent(self):
        q = Select("id").From("users")
        assert "WHERE" not in q.sql


class TestJoin:
    def test_single_join(self):
        q = Select("u.id").From("users u").Join("JOIN orders o ON o.user_id = u.id")
        assert q.sql == "SELECT u.id FROM users u JOIN orders o ON o.user_id = u.id"

    def test_multiple_joins(self):
        q = Select("u.id").From("users u").Join("JOIN orders o ON o.user_id = u.id").Join("JOIN items i ON i.order_id = o.id")
        assert "JOIN orders o ON o.user_id = u.id" in q.sql
        assert "JOIN items i ON i.order_id = o.id" in q.sql

    def test_join_with_params(self):
        q = Select("u.id").From("users u").Join("JOIN orders o ON o.user_id = u.id AND o.status = :status", status="active")
        assert q.params == {"status": "active"}

    def test_join_and_where_params(self):
        q = Select("u.id").From("users u").Join("JOIN orders o ON o.user_id = u.id AND o.type = :type", type="sale").Where("u.active = :active", active=True)
        assert q.params == {"type": "sale", "active": True}

    def test_no_join_absent(self):
        q = Select("id").From("users")
        assert "JOIN" not in q.sql


class TestOrderBy:
    def test_order_by_default_asc(self):
        q = Select("id").From("users").OrderBy("name")
        assert q.sql == "SELECT id FROM users ORDER BY name ASC"

    def test_order_by_desc(self):
        q = Select("id").From("users").OrderBy("created_at", "DESC")
        assert q.sql == "SELECT id FROM users ORDER BY created_at DESC"

    def test_multiple_order_by(self):
        q = Select("id").From("users").OrderBy("name").OrderBy("created_at", "DESC")
        assert q.sql == "SELECT id FROM users ORDER BY name ASC, created_at DESC"

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError):
            Select("id").From("users").OrderBy("id", "RANDOM")

    def test_no_order_by_absent(self):
        q = Select("id").From("users")
        assert "ORDER BY" not in q.sql


class TestGroupBy:
    def test_single_group_by(self):
        q = Select("status", "COUNT(*)").From("orders").GroupBy("status")
        assert q.sql == "SELECT status, COUNT(*) FROM orders GROUP BY status"

    def test_multiple_group_by_single_call(self):
        q = Select("a", "b").From("t").GroupBy("a", "b")
        assert "GROUP BY a, b" in q.sql

    def test_multiple_group_by_chained(self):
        q = Select("a", "b").From("t").GroupBy("a").GroupBy("b")
        assert "GROUP BY a, b" in q.sql

    def test_no_group_by_absent(self):
        q = Select("id").From("users")
        assert "GROUP BY" not in q.sql


class TestLimitOffset:
    def test_limit(self):
        q = Select("id").From("users").Limit(10)
        assert q.sql == "SELECT id FROM users LIMIT 10"

    def test_offset(self):
        q = Select("id").From("users").Offset(20)
        assert q.sql == "SELECT id FROM users OFFSET 20"

    def test_limit_and_offset(self):
        q = Select("id").From("users").Limit(10).Offset(20)
        assert q.sql == "SELECT id FROM users LIMIT 10 OFFSET 20"

    def test_offset_without_limit(self):
        q = Select("id").From("users").Offset(5)
        assert "LIMIT" not in q.sql
        assert "OFFSET 5" in q.sql

    def test_limit_zero(self):
        q = Select("id").From("users").Limit(0)
        assert "LIMIT 0" in q.sql

    def test_no_limit_absent(self):
        q = Select("id").From("users")
        assert "LIMIT" not in q.sql

    def test_no_offset_absent(self):
        q = Select("id").From("users")
        assert "OFFSET" not in q.sql


class TestParams:
    def test_params_empty_by_default(self):
        q = Select("id").From("users")
        assert q.params == {}

    def test_params_accumulate_across_joins_and_wheres(self):
        q = Select("id").From("users").Join("JOIN t ON t.id = users.t_id AND t.x = :x", x=42).Where("active = :active", active=True).Where("role = :role", role="admin")
        assert q.params == {"x": 42, "active": True, "role": "admin"}


class TestClauseOrdering:
    def test_full_query_clause_order(self):
        sql = Select("u.id", "u.name").From("users u").Join("JOIN orders o ON o.user_id = u.id").Where("u.active = :active", active=True).GroupBy("u.id", "u.name").OrderBy("u.name").Limit(25).Offset(50).sql
        assert sql == "SELECT u.id, u.name FROM users u JOIN orders o ON o.user_id = u.id WHERE u.active = :active GROUP BY u.id, u.name ORDER BY u.name ASC LIMIT 25 OFFSET 50"

    def test_group_by_before_order_by(self):
        sql = Select("a").From("t").OrderBy("a").GroupBy("a").sql
        group_pos = sql.index("GROUP BY")
        order_pos = sql.index("ORDER BY")
        assert group_pos < order_pos

    def test_order_by_before_limit(self):
        sql = Select("a").From("t").Limit(5).OrderBy("a").sql
        order_pos = sql.index("ORDER BY")
        limit_pos = sql.index("LIMIT")
        assert order_pos < limit_pos

    def test_limit_before_offset(self):
        sql = Select("a").From("t").Offset(10).Limit(5).sql
        limit_pos = sql.index("LIMIT")
        offset_pos = sql.index("OFFSET")
        assert limit_pos < offset_pos
