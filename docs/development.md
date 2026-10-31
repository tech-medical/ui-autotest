# Development

Stack: Python 3, Playwright, pytest. This repository is a UI automation client. It does not listen on an application port. The site under test is `BASE_URL` (see `.env.example`). Optional MySQL access in `db/` uses `DB_HOST` / `DB_PORT` (example default `3306`).

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Fill secrets only in the local `.env`. Never commit `.env` or real passwords, tokens, or PHI.

## Run tests

```bash
pytest

pytest tests/test_portal_home.py::TestPortalHome::test_open_homepage -v

HEADLESS=false pytest

SLOW_MO=500 pytest
```

`pytest.ini` sets `testpaths = tests`, verbose output, and short tracebacks. It does not pass `--html`. To write the HTML report described in the README:

```bash
pytest --html=reports/report.html --self-contained-html
```

`logs/`, `reports/`, and `screenshots/` are gitignored.

## Verify without a browser or secrets

```bash
bash scripts/agent-verify.sh
```

That compiles the Python tree and, only when `pytest` and `playwright` import, collects tests without running them.

Page-object and case conventions: [`prompt.md`](../prompt.md). Quick start: [`README.md`](../README.md).
