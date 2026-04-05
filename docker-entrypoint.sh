#!/bin/bash
# ============================================================
# Financial Integrity Ecosystem — Docker Entrypoint
# Orchestrates: MySQL wait → JSON Server → Flask → pytest
# ============================================================
set -e

echo "=== Financial Integrity Ecosystem — Docker Test Runner ==="

# 1. Wait for MySQL (if DB_TYPE=mysql)
if [ "$DB_TYPE" = "mysql" ]; then
    echo "[1/5] Waiting for MySQL at $MYSQL_HOST..."
    until mysqladmin ping -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --skip-ssl --silent 2>/dev/null; do
        sleep 2
    done
    echo "  MySQL is ready"
else
    echo "[1/5] Skipping MySQL (DB_TYPE=$DB_TYPE)"
fi

# 2. Start JSON Server in background
echo "[2/5] Starting JSON Server on port 3000..."
cd /app/json-server && npx json-server db.json --port 3000 --host 0.0.0.0 --quiet &
JSON_PID=$!
cd /app

# 3. Start Flask Server in background
echo "[3/5] Starting Flask Server on port 5000..."
python server/app.py &
FLASK_PID=$!

# 4. Wait for servers to be ready
echo "[4/5] Waiting for servers..."
for i in $(seq 1 20); do
    if curl -s http://localhost:3000/expenses > /dev/null 2>&1; then
        echo "  JSON Server is ready"
        break
    fi
    sleep 1
done

for i in $(seq 1 15); do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "  Flask Server is ready"
        break
    fi
    sleep 1
done

# 5. Run tests
echo "[5/5] Running tests..."
echo ""
pytest -m "not mobile" -v --alluredir=allure-results
TEST_EXIT_CODE=$?

# Cleanup
kill $JSON_PID $FLASK_PID 2>/dev/null
exit $TEST_EXIT_CODE
