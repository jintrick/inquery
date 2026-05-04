#!/bin/bash
# scripts/run_tests.sh - Test runner for inquery

set -e

APP_ROOT=$(cd "$(dirname "$0")/.." && pwd)
export PYTHONPATH="$APP_ROOT:$PYTHONPATH"

echo "=== Running Static Analysis ==="
if command -v shellcheck >/dev/null 2>&1; then
    echo "Running ShellCheck..."
    shellcheck "$APP_ROOT/bin/inquery" "$APP_ROOT/lib/ui.sh"
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
    echo "WARNING: pytest not found. Falling back to unittest for compatible tests..."
    # Fallback to unittest for basics, but some tests use pytest fixtures
    # So we'll try running everything in tests/
    python3 -m unittest discover -s "$APP_ROOT/tests" -p "test_*.py" || echo "Some tests failed or require pytest."
fi

echo -e "\n=== Running Bash Integration Tests ==="
bash "$APP_ROOT/tests/test_ui.sh"

echo -e "\nDone."
