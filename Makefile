.PHONY: verify test

verify:
	bash scripts/agent-verify.sh

test:
	pytest
