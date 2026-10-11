SCHEMA_DESCRIPTION = """
Table employees:
  employee_id TEXT PRIMARY KEY, name TEXT, department TEXT, job_title TEXT, location TEXT,
  hire_date TEXT (YYYY-MM-DD), termination_date TEXT (nullable, YYYY-MM-DD), salary_band TEXT, base_salary REAL

Table pay_periods:
  employee_id TEXT (FK -> employees.employee_id), pay_period TEXT (YYYY-MM),
  gross_pay REAL, overtime_hours REAL, overtime_pay REAL, deductions REAL, bonus REAL, net_pay REAL
"""

ALLOWED_TABLES = {"employees", "pay_periods"}
ALLOWED_COLUMNS = {
    "employees": {"employee_id", "name", "department", "job_title", "location", "hire_date",
                  "termination_date", "salary_band", "base_salary"},
    "pay_periods": {"employee_id", "pay_period", "gross_pay", "overtime_hours", "overtime_pay",
                     "deductions", "bonus", "net_pay"},
}
