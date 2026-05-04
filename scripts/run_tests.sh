#!/bin/bash
# scripts/run_tests.sh - Test runner for inquery

set -e

APP_ROOT=$(cd "$(dirname "$0")/.." && pwd)
export PYTHONPATH="$APP_ROOT:$PYTHONPATH"

check_permissions() {
    echo "Checking script permissions..."
    local failed=0
    # List of files that MUST be executable
    local exec_files=(
        "bin/inquery"
        "install.sh"
        "scripts/run_tests.sh"
        "tests/test_ui.sh"
        "tests/test_install.sh"
    )

    for f in "${exec_files[@]}"; do
        if [ ! -x "$APP_ROOT/$f" ]; then
            echo "ERROR: Execution permission (+x) missing for $f"
            failed=1
        fi
    done

    if [ $failed -ne 0 ]; then
        echo "Permission check FAILED."
        exit 1
    fi
    echo "Permission check passed."
}

echo "=== Running Static Analysis ==="
check_permissions

if command -v shellcheck >/dev/null 2>&1; then
    echo "Running ShellCheck..."
    shellcheck "$APP_ROOT/bin/inquery" "$APP_ROOT/lib/ui.sh" "$APP_ROOT/install.sh"
else
    echo "WARNING: shellcheck not found, skipping."
fi

if python3 -m ruff --version >/dev/null 2>&1; then
    echo "Running Ruff..."
    python3 -m ruff check "$APP_ROOT"
else
    echo "WARNING: ruff not found, skipping."
fi

echo -e "\n=== Running Python Unit Tests ==="
if python3 -m pytest --version >/dev/null 2>&1; then
    python3 -m pytest "$APP_ROOT/tests"
else
    echo "WARNING: pytest not found. Falling back to unittest..."
    python3 -m unittest discover -s "$APP_ROOT/tests" -p "test_*.py"
fi

echo -e "\n=== Running Bash Integration Tests ==="
bash "$APP_ROOT/tests/test_ui.sh"
bash "$APP_ROOT/tests/test_install.sh"

echo -e "\nDone."
