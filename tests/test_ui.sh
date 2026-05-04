#!/bin/bash
# tests/test_ui.sh - Integration test for ui.sh with zenity mocking

set -e

APP_ROOT=$(cd "$(dirname "$0")/.." && pwd)
export TEST_DIR="/tmp/inquery-test.$$"
mkdir -p "$TEST_DIR/mock_bin"

# Cleanup on exit
trap 'rm -rf "$TEST_DIR"' EXIT

# Create mock zenity
cat << 'EOF' > "$TEST_DIR/mock_bin/zenity"
#!/bin/bash
# Use the exported TEST_DIR variable
if [[ "$*" == *"--list"* ]]; then
    # Capture stdin (labels)
    cat > "$TEST_DIR/zenity_labels"
    # Return a selection that exists in default config to avoid executor error
    echo "Googleで検索"
fi
exit 0
EOF
chmod +x "$TEST_DIR/mock_bin/zenity"

# 1. Test Config Fallback (Default)
echo "Testing Default Config Fallback..."
(
    export PATH="$TEST_DIR/mock_bin:$PATH"
    export HOME="$TEST_DIR/fake_home"
    unset XDG_CONFIG_HOME
    mkdir -p "$HOME"
    
    # Run ui.sh directly
    bash "$APP_ROOT/lib/ui.sh" "search_term" "$APP_ROOT" > /dev/null 2>&1 || true
)

if [ -f "$TEST_DIR/zenity_labels" ] && grep -q "Googleで検索" "$TEST_DIR/zenity_labels"; then
    echo "PASS: Default config loaded correctly."
else
    echo "FAIL: Default config labels not found."
    exit 1
fi

# 2. Test User Config Priority
echo "Testing User Config Priority..."
rm -f "$TEST_DIR/zenity_labels"
(
    export PATH="$TEST_DIR/mock_bin:$PATH"
    export HOME="$TEST_DIR/fake_home"
    unset XDG_CONFIG_HOME
    USER_CONFIG_DIR="$HOME/.config/inquery"
    mkdir -p "$USER_CONFIG_DIR"
    # Important: Selection must match a label in this config or default for executor to succeed
    # But we just want to check if labels were presented.
    echo '{"actions": [{"label": "CUSTOM_ACTION", "type": "url", "url": "test"}]}' > "$USER_CONFIG_DIR/actions.json"
    
    bash "$APP_ROOT/lib/ui.sh" "search_term" "$APP_ROOT" > /dev/null 2>&1 || true
)

if [ -f "$TEST_DIR/zenity_labels" ] && grep -q "CUSTOM_ACTION" "$TEST_DIR/zenity_labels"; then
    echo "PASS: User config prioritized correctly."
else
    echo "FAIL: User config labels not found."
    exit 1
fi

echo "All Bash integration tests passed."
