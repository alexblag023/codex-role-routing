# Codex role routing

Codex custom agent profiles bind 24 delegation roles to GPT models and reasoning effort.

## Install

Copy files from `.codex/agents/` into the target project's `.codex/agents/` directory. Start a new Codex session in that project. Delegate by profile name, for example `expert_review`. Codex loads the model and effort from the matching profile.

Each profile comment records whether GPT was primary or backup in the source matrix. The profile pins that GPT route for Codex. It does not implement provider failover.

## Verify a live delegation

Run from a trusted project with the profiles installed:

    codex exec --json -s read-only 'Spawn three custom agents by role: architecture, audit, and expert_review. Use no model or effort overrides. Ask each to return exactly ROUTE_SMOKE followed by a space and its role name, without using tools. Wait for all three.'

Find `thread.started` in the output. Pass its thread ID and the corresponding daily Codex session directory to the verifier:

    python scripts/itest_codex_delegation.py "$sessionDay" "$parentThreadId"

The verifier checks each child journal for selected role, model, effort and completion marker.

## Contents

- `.codex/agents/` contains profiles for 24 canonical roles.
- `scripts/itest_codex_delegation.py` verifies a live three-role smoke run.
- `docs/` records mapping provenance.
