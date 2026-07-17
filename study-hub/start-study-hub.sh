#!/bin/sh
# WGU Study Hub launcher (Linux) — run me, or double-click if your file
# manager allows executing scripts.
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
  exec python3 wgu_study_hub.py "$@"
fi

echo ""
echo "  Python 3 was not found. Install it with your package manager,"
echo "  e.g.:  sudo apt install python3     (Debian/Ubuntu)"
echo "         sudo dnf install python3     (Fedora)"
echo "  then run this script again."
echo ""
echo "  Nothing else to install — no npm, no Node, no pip."
exit 1
