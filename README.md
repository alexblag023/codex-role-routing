# Codex role routing

Codex custom agent profiles bind delegation roles to GPT models and reasoning effort. The approved routing matrix remains the source of truth; these profiles select the GPT primary when present, otherwise the accepted GPT backup.

## Install

Copy files from `.codex/agents/` into the target project's `.codex/agents/` directory. Mark the target project as trusted in Codex and start a new session there so the project-local agent profiles are loaded. In the structured subagent call, set `agent_type` to the profile name, for example `expert_review`; `task_name` is only a task identifier and does not select a profile. Leave model and effort unset so Codex reads both from the selected profile.

Each profile comment records whether GPT was primary or backup in the source matrix. The profile pins that GPT route for Codex. It does not implement primary-provider selection or provider failover. `audit`, `classify`, `compliance_check`, `fact_check`, `patch_proposal`, and `source_synthesis` therefore run on their configured GPT backup in Codex, even though the matrix primary is `session_model`.

The checked-in profiles are the distributable source. The root `.codex/agents/` copy in the IT workspace is maintained separately; run the validator against that directory too when updating local profiles.

## Validate profile mapping

Install PyYAML in the Python environment, then run from this directory:

    python scripts/check_role_profiles.py

To check a project's installed profiles against the same matrix:

    python scripts/check_role_profiles.py --profiles ../.codex/agents

Validation fails on missing or extra roles, filename/name disagreement and any model/effort mismatch.

## Verify a live delegation

Run this smoke from the trusted project root with the profiles installed:

    codex exec --json -s read-only -C C:\Claude\IT\codex-role-routing 'Call the subagent tool three times with these exact structured arguments. For each call set `task_name` to `route_<role>_smoke`, `agent_type` to the corresponding role (`architecture`, `audit`, `expert_review`), `fork_turns` to `none`, and `message` to `Reply exactly ROUTE_SMOKE <role> and do not use tools.` Do not set model or effort. Wait for all three children.'

The parent process must read trusted project-local profiles. Mark the repository as trusted in Codex settings before using the command. Merely naming roles in natural language without setting `agent_type` creates generic children and does not test these profiles. If the interface lacks a structured `agent_type` selector, report the route as unverified.

Find the parent thread ID and daily Codex session directory, then pass the exact set of requested roles to the verifier:

    python scripts/itest_codex_delegation.py "$sessionDay" "$parentThreadId" architecture audit expert_review

The verifier checks each child journal for a named role, the model and effort recorded in `turn_context`, and the exact completion marker. A child with a missing `agent_role` is reported as an unverified profile route, even if an ordinary child task completed successfully. This distinguishes successful generic delegation from verified named-profile routing.

## Contents

- `.codex/agents/` contains profiles for 30 canonical roles.
- `scripts/check_role_profiles.py` verifies every profile against the approved matrix.
- `scripts/itest_codex_delegation.py` verifies live named-role delegations against child journals.
- `docs/` records mapping provenance.
