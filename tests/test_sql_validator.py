import pytest
from app.sql_validator import validate_and_cap, SQLValidationError


def test_rejects_non_select():
    with pytest.raises(SQLValidationError):
        validate_and_cap("DELETE FROM employees WHERE employee_id = 'E1'")


def test_rejects_unknown_table():
    with pytest.raises(SQLValidationError):
        validate_and_cap("SELECT * FROM users")


def test_rejects_multiple_statements():
    with pytest.raises(SQLValidationError):
        validate_and_cap("SELECT * FROM employees; DROP TABLE employees;")


def test_injects_limit_when_missing():
    sql = validate_and_cap("SELECT * FROM employees")
    assert "LIMIT 500" in sql.upper()


def test_caps_limit_when_too_large():
    sql = validate_and_cap("SELECT * FROM employees LIMIT 10000")
    assert "LIMIT 500" in sql.upper()


def test_allows_valid_join_query():
    sql = validate_and_cap(
        "SELECT e.department, SUM(p.overtime_pay) FROM pay_periods p "
        "JOIN employees e ON e.employee_id = p.employee_id GROUP BY e.department"
    )
    assert "LIMIT" in sql.upper()
