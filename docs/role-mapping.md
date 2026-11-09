# Role mapping provenance

Profile models and effort values come from the current `role_delegation` entries in `minimax-code-customizations/router/llm-routing.yaml`. Resolution is deterministic: use the GPT primary when it is `openai-codex/...`; otherwise use the GPT backup when it is `openai-codex/...`. The profile comment preserves whether the selected route was primary or backup. For `session_model` primaries, this is a Codex-specific pin to the accepted GPT backup, not a dynamic fallback implementation.

A prior live verification is documented for `architecture`, `audit`, and `expert_review`; this file does not archive its journals, so that historical claim cannot be independently rechecked from this repository. Ordinary Codex child threads with `agent_role: null` prove that a child was spawned, but do not prove a named profile was selected. Current named-profile verification requires child journals containing the expected role, model, effort, and completion marker.

Run `scripts/check_role_profiles.py` to compare every profile against the current matrix, preserve Codex `agent_type` names, and verify representative roles through actual child session journals with `scripts/itest_codex_delegation.py`.
