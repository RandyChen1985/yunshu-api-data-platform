import argparse
import asyncio
import getpass
import os
import re
import sys
from dataclasses import dataclass

import aiomysql


DATABASE_SWITCH_RE = re.compile(r"^\s*(CREATE\s+DATABASE\b|USE\b)", re.IGNORECASE)

# MySQL errors that indicate the migration step was already applied.
IDEMPOTENT_ERROR_CODES = frozenset({1007, 1050, 1060, 1061, 1062, 1091})


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Apply a SQL migration to an explicitly selected MySQL database."
    )
    parser.add_argument("file_path", help="SQL file to execute")
    parser.add_argument("--host", help="MySQL host")
    parser.add_argument("--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--user", help="MySQL user")
    parser.add_argument("--password", help="MySQL password; omit with --interactive to prompt securely")
    parser.add_argument("--database", "--db", dest="database", help="Target database name")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for any missing connection fields before confirming execution",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the per-file confirmation. Use only after an outer wrapper has already confirmed.",
    )
    args = parser.parse_args(argv)

    missing = [name for name in ("host", "user", "database") if not getattr(args, name)]
    if missing and not args.interactive:
        parser.error(
            "missing explicit connection parameter(s): "
            + ", ".join(f"--{name}" for name in missing)
            + ". Use --interactive to enter them safely."
        )

    return args


def prompt_if_missing(label, current, secret=False):
    if current is not None:
        return current
    if secret:
        return getpass.getpass(f"{label}: ")
    return input(f"{label}: ").strip()


def build_config(args):
    return DbConfig(
        host=prompt_if_missing("MySQL host", args.host),
        port=args.port,
        user=prompt_if_missing("MySQL user", args.user),
        password=prompt_if_missing("MySQL password", args.password, secret=True),
        database=prompt_if_missing("Target database", args.database),
    )


def split_sql_statements(sql_content):
    statements = []
    current_statement = []
    in_string = False
    escape = False
    quote_char = None

    for char in sql_content:
        current_statement.append(char)

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
            continue

        if char in ("'", '"', "`"):
            if not in_string:
                in_string = True
                quote_char = char
            elif char == quote_char:
                in_string = False
                quote_char = None

        elif char == ";" and not in_string:
            stmt = "".join(current_statement).strip()
            lines = []
            for line in stmt.splitlines():
                clean_line = line.strip()
                if not clean_line.startswith("--") and not clean_line.startswith("#"):
                    lines.append(line)
            clean_stmt = "\n".join(lines).strip()

            if clean_stmt.endswith(";"):
                clean_stmt = clean_stmt[:-1].strip()

            if clean_stmt:
                if DATABASE_SWITCH_RE.match(clean_stmt):
                    print(f"⚠️  Skipping database-switching statement: {clean_stmt.splitlines()[0]}")
                else:
                    statements.append(clean_stmt)
            current_statement = []

    if current_statement:
        stmt = "".join(current_statement).strip()
        lines = []
        for line in stmt.splitlines():
            clean_line = line.strip()
            if not clean_line.startswith("--") and not clean_line.startswith("#"):
                lines.append(line)
        clean_stmt = "\n".join(lines).strip()
        if clean_stmt.endswith(";"):
            clean_stmt = clean_stmt[:-1].strip()
        if clean_stmt:
            if not DATABASE_SWITCH_RE.match(clean_stmt):
                statements.append(clean_stmt)

    return statements


def confirm_execution(config, file_path):
    print("请确认本次 SQL 执行目标：")
    print(f"  Host     : {config.host}")
    print(f"  Port     : {config.port}")
    print(f"  User     : {config.user}")
    print(f"  Database : {config.database}")
    print(f"  SQL file : {file_path}")
    print("  Password : ******")
    answer = input("确认无误请输入 YES 继续执行：").strip()
    if answer.upper() != "YES":
        print("❌ 已取消，未执行 SQL。")
        raise SystemExit(1)


async def apply_sql(file_path, config):
    print(f"🔌 Connecting to MySQL server to ensure database '{config.database}' exists...")

    try:
        temp_conn = await aiomysql.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            autocommit=True,
        )
        async with temp_conn.cursor() as cur:
            create_db_sql = (
                f"CREATE DATABASE IF NOT EXISTS `{config.database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            await cur.execute(create_db_sql)
        temp_conn.close()
        await temp_conn.ensure_closed()
    except Exception as e:
        print(f"❌ Connection or database creation failed: {e}")
        sys.exit(1)

    print(f"🔌 Connecting to database '{config.database}'...")
    try:
        pool = await aiomysql.create_pool(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            db=config.database,
            autocommit=True,
        )
    except Exception as e:
        print(f"❌ Connection to '{config.database}' failed: {e}")
        sys.exit(1)

    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        print(f"📖 Reading {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        statements = split_sql_statements(sql_content)

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                print(f"🚀 Executing {len(statements)} statements...")
                for i, stmt in enumerate(statements):
                    try:
                        await cur.execute(stmt)
                        print(f"   -> Affected rows: {cur.rowcount}")
                    except Exception as sqle:
                        err_code = getattr(sqle, "args", [0])[0]
                        if err_code in IDEMPOTENT_ERROR_CODES:
                            print(f"   -> Skipping (already applied): {sqle}")
                        else:
                            print(f"❌ Error executing statement #{i + 1}:\n{stmt[:100]}...\nError: {sqle}")
                            sys.exit(1)

            await conn.commit()
            print("✅ Transaction committed.")

        print("✅ SQL applied successfully.")

    finally:
        pool.close()
        await pool.wait_closed()


def main(argv=None):
    args = parse_args(argv)
    config = build_config(args)
    if not args.yes:
        confirm_execution(config, args.file_path)
    asyncio.run(apply_sql(args.file_path, config))


if __name__ == "__main__":
    main()
