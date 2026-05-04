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

# 5. Verify configuration provisioning
# Scenario A: Provisioning when no config exists
CONFIG_FILE="$HOME/.config/inquery/actions.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "PASS: Configuration provisioned at $CONFIG_FILE"
    # Ensure the provisioned file is an exact copy of the default
    if diff "$CONFIG_FILE" "$APP_ROOT/config/actions.json" > /dev/null; then
        echo "PASS: Provisioned config matches default config."
    else
        echo "FAIL: Provisioned config does not match default."
        exit 1
    fi
else
    echo "FAIL: Configuration was not provisioned."
    exit 1
fi

# Scenario B: No overwriting when config already exists
echo '{"custom": "data"}' > "$CONFIG_FILE"
echo "Re-running install.sh to test idempotency..."
./install.sh
if grep -q '"custom": "data"' "$CONFIG_FILE"; then
    echo "PASS: Existing configuration was not overwritten."
else
    echo "FAIL: Existing configuration was overwritten!"
    exit 1
fi

echo "All installation tests passed."
