"""Oracle DSN 构建与 yovole-nanzi-ai-agent-platform 语义对齐。"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Optional

import pytest

oracledb = pytest.importorskip("oracledb")

from app.services.pool_manager import DataSourcePoolManager


def _dsn(host: str, port: int, database_name: str, extra_params: Optional[dict]):
    return DataSourcePoolManager._build_oracle_dsn(
        SimpleNamespace(host=host, port=port, database_name=database_name, extra_params=extra_params)
    )


def test_oracle_dsn_default_uses_sid():
    dsn = _dsn("db.example.com", 1521, "ORCL", None)
    assert "SID=ORCL" in dsn.replace(" ", "")
    assert "HOST=db.example.com" in dsn.replace(" ", "")
    assert "PORT=1521" in dsn.replace(" ", "")


def test_oracle_dsn_explicit_service_name_in_extra():
    dsn = _dsn("db.example.com", 1521, "ignored", {"service_name": "ORCLPDB1"})
    assert "SERVICE_NAME=ORCLPDB1" in dsn.replace(" ", "")
    assert "SID=" not in dsn.replace(" ", "")


def test_oracle_dsn_database_name_as_service_when_flag():
    dsn = _dsn("db.example.com", 1521, "MY_SERVICE", {"oracle_use_service_name": True})
    assert "SERVICE_NAME=MY_SERVICE" in dsn.replace(" ", "")


def test_oracle_dsn_service_name_wins_over_use_service_flag():
    dsn = _dsn(
        "h", 1521, "DB_AS_SERVICE",
        {"service_name": "FROM_EXTRA", "oracle_use_service_name": True},
    )
    assert "SERVICE_NAME=FROM_EXTRA" in dsn.replace(" ", "")


def test_oracle_dsn_requires_database_when_sid_mode():
    with pytest.raises(ValueError, match="database_name"):
        DataSourcePoolManager._build_oracle_dsn(
            SimpleNamespace(host="h", port=1521, database_name=None, extra_params=None)
        )
