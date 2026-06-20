import pytest

from sqlqb import Insert


class TestInsertBasic:
    def test_single_row(self):
        q = Insert().Into("users").Values(name="Alice", email="alice@example.com")
        assert q.sql == "INSERT INTO users (name, email) VALUES (?, ?)"

    def test_str_equals_sql(self):
        q = Insert().Into("users").Values(name="Alice")
        assert str(q) == q.sql

    def test_params_single_row(self):
        q = Insert().Into("users").Values(name="Alice", email="alice@example.com")
        assert q.params == ["Alice", "alice@example.com"]

    def test_multiple_rows(self):
        q = Insert().Into("users").Values(name="Alice").Values(name="Bob")
        assert q.sql == "INSERT INTO users (name) VALUES (?), (?)"
        assert q.params == ["Alice", "Bob"]

    def test_multiple_columns_multiple_rows(self):
        q = Insert().Into("orders").Values(user_id=1, total=99).Values(user_id=2, total=50)
        assert q.sql == "INSERT INTO orders (user_id, total) VALUES (?, ?), (?, ?)"
        assert q.params == [1, 99, 2, 50]

    def test_method_chaining_returns_insert(self):
        q = Insert()
        assert q.Into("t") is q
        assert q.Values(x=1) is q

    def test_no_table_raises(self):
        with pytest.raises(ValueError):
            Insert().Values(name="Alice").sql

    def test_no_values_raises(self):
        with pytest.raises(ValueError):
            Insert().Into("users").sql

    def test_empty_table_raises(self):
        with pytest.raises(ValueError):
            Insert().Into("")

    def test_blank_table_raises(self):
        with pytest.raises(ValueError):
            Insert().Into("   ")

    def test_empty_values_raises(self):
        with pytest.raises(ValueError):
            Insert().Into("users").Values()

    def test_params_empty_before_values(self):
        q = Insert().Into("users")
        assert q.params == []

    def test_various_value_types(self):
        q = Insert().Into("events").Values(user_id=42, active=True, score=3.14, label=None)
        assert q.params == [42, True, 3.14, None]
