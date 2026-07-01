"""SQL 执行接口对 SQL Server 的行数限制逻辑。"""
from app.api.v1.endpoints.sql_execution import _enforce_limit


def test_enforce_limit_sqlserver_wraps_top():
    sql = "SELECT * FROM dbo.users"
    limited = _enforce_limit(sql, source_type="sqlserver")
    assert "SELECT TOP" in limited.upper()
    assert "dbo.users" in limited


def test_enforce_limit_sqlserver_skips_when_top_present():
    sql = "SELECT TOP 10 * FROM dbo.users"
    assert _enforce_limit(sql, source_type="sqlserver") == sql
