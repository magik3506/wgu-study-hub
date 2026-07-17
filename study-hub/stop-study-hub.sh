#!/bin/sh
# Stops a running WGU Study Hub.
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then
  exec python3 wgu_study_hub.py --stop
fi
echo "  Python was not found — but then the hub can't be running either."
exit 1
