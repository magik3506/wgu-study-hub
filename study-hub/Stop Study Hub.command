#!/bin/bash
# Stops a running WGU Study Hub — double-click me.
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 wgu_study_hub.py --stop
else
  echo "  Python was not found — but then the hub can't be running either."
fi
echo ""
read -n 1 -s -r -p "  Press any key to close..."
echo ""
