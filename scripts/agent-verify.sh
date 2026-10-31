#!/usr/bin/env bash
# Syntax check for ui-autotest. Does not start a browser, call the portal, or read secrets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m compileall -q -x '/(\.git|\.venv|venv|__pycache__)/' .

if python3 -c "import pytest, playwright" >/dev/null 2>&1; then
  python3 -m pytest --collect-only -q
else
  echo "pytest/playwright not installed; skipped collection. See docs/development.md."
fi
