# Codex role delegation

For every canonical role in `.codex/agents/`, select the profile through the structured `agent_type` field in the Codex subagent call. `task_name` is only the child task identifier and does not select a profile. Leave model and reasoning effort unset unless an explicit override is intended; otherwise the profile TOML supplies both.

After a live routing check, verify the child's `agent_role`, its own turn's model and effort, and its exact completion marker with `scripts/itest_codex_delegation.py`. Do not infer the selected role from `agent_path` or the task name. A child with no `agent_role` means the profile was not selected.
