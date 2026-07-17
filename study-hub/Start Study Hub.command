#!/bin/bash
# WGU Study Hub launcher (macOS) — double-click me.
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  exec python3 wgu_study_hub.py "$@"
fi

echo ""
echo "  Python 3 was not found on this Mac."
echo ""
echo "  Easiest fix: open Terminal and run    xcode-select --install"
echo "  (or download Python from https://www.python.org/downloads/)"
echo "  then double-click 'Start Study Hub.command' again."
echo ""
echo "  Nothing else to install — no npm, no Node, no pip."
echo ""
read -n 1 -s -r -p "  Press any key to close..."
echo ""
