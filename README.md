# Codex role routing

Codex custom agent profiles bind delegation roles to GPT models and reasoning effort. The approved routing matrix remains the source of truth; these profiles select the GPT primary when present, otherwise the accepted GPT backup.

## Install

Copy files from `.codex/agents/` into the target project's `.codex/agents/` directory. Start a new Codex session in that project. Delegate by profile name, for example `expert_review`. Codex loads the model and effort from the matching profile.

Each profile comment records whether GPT was primary or backup in the source matrix. The profile pins that GPT route for Codex. It does not implement primary-provider selection or provider failover. `audit`, `classify`, `compliance_check`, `fact_check`, `patch_proposal`, and `source_synthesis` therefore run on their configured GPT backup in Codex, even though the matrix primary is `session_model`.

The checked-in profiles are the distributable source. The root `.codex/agents/` copy in the IT workspace is maintained separately; run the validator against that directory too when updating local profiles.

## Validate profile mapping

Install PyYAML in the Python environment, then run from this directory:

    python scripts/check_role_profiles.py

To check a project's installed profiles against the same matrix:

    python scripts/check_role_profiles.py --profiles ../.codex/agents

Validation fails on missing or extra roles and on any model/effort mismatch.

## Verify a live delegation

Run a parent Codex session in a trusted project with the profiles installed. Use a Codex tool/API that passes each selected profile in its structured `agent_type` field, without model or effort overrides. Ask each child to return exactly `ROUTE_SMOKE <role>` without using tools, then wait for all children. Merely naming roles in natural language or asking `codex exec` to spawn them can create generic child threads and does not test the profiles. If the available interface has no structured `agent_type` selector, report the route as unverified.

Find the parent thread ID and daily Codex session directory, then pass the exact set of requested roles to the verifier:

    python scripts/itest_codex_delegation.py "$sessionDay" "$parentThreadId" architecture audit expert_review

The verifier checks each child journal for a named role, the model and effort recorded in `turn_context`, and the exact completion marker. A child with a missing `agent_role` is reported as an unverified profile route, even if an ordinary child task completed successfully. This distinguishes successful generic delegation from verified named-profile routing.

## Contents

- `.codex/agents/` contains profiles for 24 canonical roles.
- `scripts/check_role_profiles.py` verifies every profile against the approved matrix.
- `scripts/itest_codex_delegation.py` verifies live named-role delegations against child journals.
- `docs/` records mapping provenance.
