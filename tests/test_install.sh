#!/bin/bash
# tests/test_install.sh - Automated integration test for install.sh

set -e

APP_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TEST_DIR="/tmp/inquery-install-test.$$"
mkdir -p "$TEST_DIR"

# Mock environment
export HOME="$TEST_DIR/fake_home"
export BIN_DIR="$HOME/.local/bin"
export APP_DIR="$HOME/.local/share/applications"
mkdir -p "$HOME"

echo "Testing install.sh execution..."

# Cleanup on exit
trap 'rm -rf "$TEST_DIR"' EXIT

# 1. Test direct execution (verifies +x permission)
cd "$APP_ROOT"
./install.sh

# 2. Verify symlink creation
if [ -L "$BIN_DIR/inquery" ]; then
    echo "PASS: Symlink created at $BIN_DIR/inquery"
else
    echo "FAIL: Symlink not found."
    exit 1
fi

# 3. Verify desktop file creation and path replacement
DESKTOP_FILE="$APP_DIR/inquery.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    echo "PASS: Desktop file created at $DESKTOP_FILE"
    if grep -q "Exec=$APP_ROOT/bin/inquery" "$DESKTOP_FILE"; then
        echo "PASS: Absolute path correctly replaced in desktop file."
    else
        echo "FAIL: Path replacement failed in desktop file."
        grep "Exec=" "$DESKTOP_FILE"
        exit 1
    fi
else
    echo "FAIL: Desktop file not found."
    exit 1
fi

# 4. Verify bin/inquery execution permission after install
if [ -x "$APP_ROOT/bin/inquery" ]; then
    echo "PASS: bin/inquery is executable."
else
    echo "FAIL: bin/inquery is not executable."
    exit 1
fi

echo "All installation tests passed."
