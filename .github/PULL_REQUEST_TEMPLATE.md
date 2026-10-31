## Summary

<!-- What changed and why. -->

## Checklist

- [ ] Module / package boundaries respected
- [ ] API / routes / contracts updated if needed
- [ ] State enums / constants not changed without call-site + docs updates
- [ ] SQL / migrations include verify + rollback notes (if any)
- [ ] External deps (payments, auth, webhooks, PHI) called out
- [ ] No secrets / PHI in PR text, screenshots, or commits
- [ ] Baseline branch followed (`docs/BRANCHING.md` or AGENTS.md)

## Verify commands

```bash
bash scripts/agent-verify.sh
```

## Test plan

<!-- How verified. Full UI pytest needs a local .env and browsers; see docs/development.md. -->
