#!/usr/bin/env bash
set -u

TARGET="${1:-tests/test_login.py}"

# 1. Run test suite via run_tests.py (forwarding extra pytest args from "${@:2}")
python run_tests.py --target "$TARGET" --locale en --platform android "${@:2}"
TEST_EXIT_CODE=$?

# 2. Locate the newest timestamped run directory inside logs/
RUN_LOG_DIR=$(ls -dt logs/*/ 2>/dev/null | head -1 | sed 's:/*$::')

if [ -n "$RUN_LOG_DIR" ] && [ -f "$RUN_LOG_DIR/suite.log" ]; then
    # 3. Generate standalone HTML report from suite.log
    python generate_report.py --log "$RUN_LOG_DIR/suite.log" --output "$RUN_LOG_DIR/report.html"
    # 4. Print final report location
    echo "Report generated at $RUN_LOG_DIR/report.html"
else
    echo "Error: Could not find suite.log inside logs/ directory."
    exit 1
fi

exit $TEST_EXIT_CODE

