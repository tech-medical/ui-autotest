# ui-autotest

Python + Playwright + pytest UI automation.

## Read first

- [`docs/BRANCHING.md`](docs/BRANCHING.md) — git baseline is `main`.
- [`docs/development.md`](docs/development.md) — install, run, and verify.
- [`prompt.md`](prompt.md) — page objects and test authoring.
- [`README.md`](README.md) — quick start.

## Skills

No `.agents/skills` directory in this repo. Follow this file and `docs/`.

## Verify

```bash
bash scripts/agent-verify.sh
```

A full UI run needs a local `.env` and Playwright browsers. See `docs/development.md`. Do not put credentials in CI.

## Secrets and PHI

Never copy secrets, passwords, tokens, or PHI into chat, docs, tests, screenshots, or commits. Keep real values in local `.env` only. `.env.example` stays names and non-secret placeholders.
