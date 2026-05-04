#!/bin/bash
# install.sh - Automated installer for inquery

set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Installing inquery..."

APP_ROOT=$(cd "$(dirname "$0")" && pwd)
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"

# 1. Ensure executable permissions
chmod +x "$APP_ROOT/bin/inquery"
echo -e "${GREEN}✓${NC} Set executable permissions for bin/inquery"

# 2. Create bin directory if it doesn't exist
mkdir -p "$BIN_DIR"

# 3. Create symlink for the executable (force overwrite)
ln -sf "$APP_ROOT/bin/inquery" "$BIN_DIR/inquery"
echo -e "${GREEN}✓${NC} Created symlink at $BIN_DIR/inquery"

# 4. Setup desktop integration
mkdir -p "$APP_DIR"
DESKTOP_FILE="$APP_DIR/inquery.desktop"

# Generate desktop file from example
sed "s|/path/to/inquery|$APP_ROOT|g" "$APP_ROOT/assets/inquery.desktop.example" > "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"
echo -e "${GREEN}✓${NC} Installed desktop entry at $DESKTOP_FILE"

# 5. Provision default configuration if it doesn't already exist
# We respect user's existing settings and only provide a default if none exists.
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/inquery"
CONFIG_FILE="$CONFIG_DIR/actions.json"

mkdir -p "$CONFIG_DIR"
if [ ! -f "$CONFIG_FILE" ]; then
    cp "$APP_ROOT/config/actions.json" "$CONFIG_FILE"
    echo -e "${GREEN}✓${NC} Provisioned default configuration at $CONFIG_FILE"
else
    # Maintain user's current settings by not overwriting existing file
    echo -e "${GREEN}✓${NC} Existing configuration found at $CONFIG_FILE (skipped)"
fi

echo -e "\n${GREEN}Installation complete!${NC}"
echo "You can now launch 'inquery' from your application menu or by typing 'inquery' in the terminal."
echo "Note: Make sure $BIN_DIR is in your PATH."
