#!/bin/bash
# 免 Python 依赖的 MySQL SQL 导入工具。
# 依靠系统已安装的 mysql 命令行客户端。
# 实现了与 Python 脚本相同的幂等性过滤机制（忽略 1007, 1050, 1060, 1061, 1062, 1091 等错误码）。

cd "$(dirname "$0")/.."

DEFAULT_ADMIN_API_KEY="YZnxdJLZ0Hwf7IpHXHkYDZYI-CUsTafRjGeANklakuA"
MYSQL_PORT_INPUT=3306

read -r -p "MySQL host: " MYSQL_HOST_INPUT
read -r -p "MySQL port [3306]: " MYSQL_PORT_INPUT
read -r -p "MySQL user: " MYSQL_USER_INPUT
read -r -s -p "MySQL password: " MYSQL_PASSWORD_INPUT
echo
read -r -p "Target database: " MYSQL_DATABASE_INPUT

MYSQL_PORT_INPUT=${MYSQL_PORT_INPUT:-3306}

if [ -z "$MYSQL_HOST_INPUT" ] || [ -z "$MYSQL_USER_INPUT" ] || [ -z "$MYSQL_DATABASE_INPUT" ]; then
    echo "❌ Host、User、Target database 都必须手动输入。"
    exit 1
fi

if ! command -v mysql >/dev/null 2>&1; then
    echo "❌ 错误: 未在系统 PATH 中找到 'mysql' 命令行客户端。"
    echo "请先安装 mysql-client，或使用带 Python 虚拟环境的 ./apply-sql.sh 脚本。"
    exit 1
fi

echo "---------------------------------------------------"
echo "请确认本次 SQL 执行目标："
echo "  Host     : $MYSQL_HOST_INPUT"
echo "  Port     : $MYSQL_PORT_INPUT"
echo "  User     : $MYSQL_USER_INPUT"
echo "  Database : $MYSQL_DATABASE_INPUT"
echo "  Password : ******"
if [ $# -eq 0 ]; then
    echo "  SQL files: db-prod/V*.sql"
else
    echo "  SQL file : $*"
fi
read -r -p "确认无误请输入 YES 继续执行：" CONFIRM_INPUT
CONFIRM_UPPER=$(echo "$CONFIRM_INPUT" | tr '[:lower:]' '[:upper:]')
if [ "$CONFIRM_UPPER" != "YES" ]; then
    echo "❌ 已取消，未执行 SQL。"
    exit 1
fi

IGNORED_ERRORS="1007|1050|1060|1061|1062|1091"

MYSQL_BASE_CMD="mysql -h $MYSQL_HOST_INPUT -P $MYSQL_PORT_INPUT -u $MYSQL_USER_INPUT -p$MYSQL_PASSWORD_INPUT"
CREATE_DB_SQL="CREATE DATABASE IF NOT EXISTS \`$MYSQL_DATABASE_INPUT\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo "🔌 正在连接 MySQL 并确保目标数据库已存在..."
if ! echo "$CREATE_DB_SQL" | $MYSQL_BASE_CMD >/dev/null 2>&1; then
    echo "❌ 数据库连接或创建失败，请检查连接参数（如 Host、User、Password）或数据库服务状态。"
    exit 1
fi

MYSQL_CMD="$MYSQL_BASE_CMD $MYSQL_DATABASE_INPUT"

print_admin_login_hint() {
    echo -e "\033[1;32m===================================================\033[0m"
    echo -e "\033[1;32m🔑 首次登录重要指引：\033[0m"
    echo -e "  - \033[1;36m默认用户名\033[0m  : admin"
    echo -e "  - \033[1;36m预置 API Key\033[0m: $DEFAULT_ADMIN_API_KEY"
    echo -e "  - \033[1;33m登录方式\033[0m    : 在系统登录框中复制并粘贴上述 API Key 即可登录。"
    echo -e "  - \033[1;31m安全提醒\033[0m    : 首次登录成功后，请务必前往【用户管理】"
    echo -e "                或【个人中心】为 admin 设置密码，以启用常规密码登录。"
    echo -e "\033[1;32m===================================================\033[0m"
}

execute_sql_file() {
    local sql_file="$1"
    echo "📖 Reading $sql_file..."

    local err_log
    err_log=$(mktemp)

    local stmt=""
    local in_string=0

    while IFS= read -r line || [[ -n "$line" ]]; do
        clean_line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [ $in_string -eq 0 ]; then
            if [ -z "$clean_line" ] || [[ "$clean_line" =~ ^-- ]] || [[ "$clean_line" =~ ^/\* ]]; then
                continue
            fi
        fi

        stmt="$stmt $line"

        local temp
        temp="${line//\\\'/}"
        temp="${temp//\'\'/}"
        local only_quotes
        only_quotes="${temp//[^\']/}"
        local num_quotes=${#only_quotes}

        if (( num_quotes % 2 != 0 )); then
            in_string=$((1 - in_string))
        fi

        if [ $in_string -eq 0 ] && [[ "$clean_line" =~ \;$ ]]; then
            if [[ "$stmt" =~ ^[[:space:]]*(CREATE[[:space:]]+DATABASE|USE)[[:space:]] ]]; then
                echo "⚠️  Skipping database-switching statement"
                stmt=""
                continue
            fi

            set +e
            echo "$stmt" | $MYSQL_CMD 2>"$err_log"
            status=$?
            set -e

            if [ $status -ne 0 ]; then
                err_msg=$(cat "$err_log")
                is_ignored=0
                for code in ${IGNORED_ERRORS//|/ }; do
                    if [[ "$err_msg" =~ "ERROR $code" ]] || [[ "$err_msg" =~ "Error $code" ]]; then
                        echo "   -> Skipping (already applied): $err_msg"
                        is_ignored=1
                        break
                    fi
                done

                if [ $is_ignored -eq 0 ]; then
                    echo "❌ Error executing statement:"
                    echo "Statement: ${stmt:0:150}..."
                    echo "Error message: $err_msg"
                    rm -f "$err_log"
                    return 1
                fi
            fi
            stmt=""
        fi
    done < "$sql_file"

    if [ -n "$stmt" ]; then
        local clean_stmt
        clean_stmt=$(echo "$stmt" | sed '/^[[:space:]]*--/d; /^[[:space:]]*#/d; s/^[[:space:]]*//; s/[[:space:]]*$//')
        if [ -n "$clean_stmt" ]; then
            if ! [[ "$clean_stmt" =~ ^[[:space:]]*(CREATE[[:space:]]+DATABASE|USE)[[:space:]] ]]; then
                set +e
                echo "$clean_stmt" | $MYSQL_CMD 2>"$err_log"
                status=$?
                set -e
                if [ $status -ne 0 ]; then
                    err_msg=$(cat "$err_log")
                    is_ignored=0
                    for code in ${IGNORED_ERRORS//|/ }; do
                        if [[ "$err_msg" =~ "ERROR $code" ]] || [[ "$err_msg" =~ "Error $code" ]]; then
                            echo "   -> Skipping (already applied): $err_msg"
                            is_ignored=1
                            break
                        fi
                    done
                    if [ $is_ignored -eq 0 ]; then
                        echo "❌ Error executing statement:"
                        echo "Statement: ${clean_stmt:0:150}..."
                        echo "Error message: $err_msg"
                        rm -f "$err_log"
                        return 1
                    fi
                fi
            fi
        fi
    fi

    rm -f "$err_log"
    return 0
}

if [ $# -eq 0 ]; then
    DB_DIR="db-prod"
    if [ ! -d "$DB_DIR" ]; then
        echo "❌ 找不到目录 $DB_DIR"
        exit 1
    fi

    FILES=$(ls "$DB_DIR"/V*.sql 2>/dev/null | sort -V)
    if [ -z "$FILES" ]; then
        echo "❌ 未在 $DB_DIR 中找到任何 V*.sql 迁移文件"
        exit 1
    fi

    for f in $FILES; do
        echo "---------------------------------------------------"
        echo "🚀 Applying $f..."
        if ! execute_sql_file "$f"; then
            echo "❌ Failed to apply $f"
            exit 1
        fi
    done
    echo "---------------------------------------------------"
    echo "✅ 所有数据库结构初始化迁移 SQL 文件执行成功。"

    read -r -p "是否需要顺带导入默认管理员账号和预置 API Key 凭证？ (推荐首次部署时导入) [Y/N]: " RUN_INIT_ADMIN
    RUN_INIT_ADMIN_UPPER=$(echo "$RUN_INIT_ADMIN" | tr '[:lower:]' '[:upper:]')
    if [ "$RUN_INIT_ADMIN_UPPER" == "Y" ] || [ "$RUN_INIT_ADMIN_UPPER" == "YES" ]; then
        ADMIN_SQL="db-prod/INIT-USER-ADMIN.sql"
        if [ -f "$ADMIN_SQL" ]; then
            echo "---------------------------------------------------"
            echo "🚀 正在导入默认管理员账号数据 ($ADMIN_SQL)..."
            if ! execute_sql_file "$ADMIN_SQL"; then
                echo "❌ 默认管理员账号数据导入失败。"
                exit 1
            fi
            echo "---------------------------------------------------"
            echo "✅ 默认管理员账号数据导入成功！"
            print_admin_login_hint
        else
            echo "⚠️ 未找到默认管理员数据文件 $ADMIN_SQL，跳过导入。"
        fi
    else
        echo "💡 已跳过默认管理员账号数据的导入。"
    fi
else
    for f in "$@"; do
        echo "---------------------------------------------------"
        echo "🚀 Applying $f..."
        if ! execute_sql_file "$f"; then
            echo "❌ Failed to apply $f"
            exit 1
        fi
        if [[ "$f" =~ INIT-USER-ADMIN.sql$ ]]; then
            print_admin_login_hint
        fi
    done
fi
